#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import queue
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


TEMP_KEYS = {
    "temp",
    "temperature",
    "temp_c",
    "temperature_c",
    "celsius",
    "ambient",
    "ambient_c",
    "case",
    "case_c",
    "inlet",
    "inlet_c",
    "outlet",
    "outlet_c",
    "board",
    "board_c",
    "probe",
    "probe_c",
}


def now_epoch() -> int:
    return int(time.time())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def as_float(value: Any) -> float | None:
    if value is None or value is True or value is False:
        return None
    try:
        f = float(value)
        if not math.isfinite(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def clean_metric(name: str) -> str:
    metric = name.strip().lower().replace("temperature", "temp")
    metric = metric.replace("-", "_").replace(" ", "_")
    if metric in {"temp", "temp_c", "celsius"}:
        return "ambient"
    return metric.removesuffix("_c")


def topic_device(topic: str) -> str:
    parts = [p for p in topic.strip("/").split("/") if p]
    if not parts:
        return "unknown"
    if parts[0].lower() in {"esp32", "thermal", "sensors", "sensor", "home"} and len(parts) > 1:
        return parts[1]
    if len(parts) >= 2 and parts[-1].lower() in TEMP_KEYS:
        return parts[-2]
    return parts[0]


def topic_metric(topic: str) -> str:
    last = topic.strip("/").split("/")[-1].lower()
    if last in TEMP_KEYS:
        return clean_metric(last)
    return "ambient"


def _dedup_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the first row per (device, metric) to prevent duplicate series."""
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        key = (row["device"], row["metric"])
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def parse_payload(topic: str, payload_text: str) -> list[dict[str, Any]]:
    payload_text = payload_text.strip()
    if not payload_text:
        return []

    obj: Any
    try:
        obj = json.loads(payload_text)
    except json.JSONDecodeError:
        value = as_float(payload_text)
        if value is None:
            return []
        return [
            {
                "device": topic_device(topic),
                "metric": topic_metric(topic),
                "value_c": value,
                "humidity": None,
                "battery": None,
                "rssi": None,
            }
        ]

    if isinstance(obj, (int, float)):
        return [
            {
                "device": topic_device(topic),
                "metric": topic_metric(topic),
                "value_c": float(obj),
                "humidity": None,
                "battery": None,
                "rssi": None,
            }
        ]

    if not isinstance(obj, dict):
        return []

    device = str(
        obj.get("device")
        or obj.get("device_id")
        or obj.get("id")
        or obj.get("name")
        or obj.get("location")
        or topic_device(topic)
    )
    humidity = as_float(obj.get("humidity") or obj.get("humidity_pct"))
    battery = as_float(obj.get("battery") or obj.get("battery_v") or obj.get("battery_pct"))
    rssi = as_float(obj.get("rssi") or obj.get("wifi_rssi"))

    rows: list[dict[str, Any]] = []
    for key, value in obj.items():
        lower = str(key).lower()
        if lower in TEMP_KEYS or lower.endswith("_c") or lower.endswith("temp"):
            temp = as_float(value)
            if temp is not None:
                rows.append(
                    {
                        "device": device,
                        "metric": clean_metric(lower),
                        "value_c": temp,
                        "humidity": humidity,
                        "battery": battery,
                        "rssi": rssi,
                    }
                )

    if not rows and "readings" in obj and isinstance(obj["readings"], list):
        for reading in obj["readings"]:
            if not isinstance(reading, dict):
                continue
            metric = clean_metric(str(reading.get("metric") or reading.get("name") or "ambient"))
            temp = as_float(reading.get("value_c") or reading.get("temperature_c") or reading.get("temp_c"))
            if temp is not None:
                rows.append(
                    {
                        "device": device,
                        "metric": metric,
                        "value_c": temp,
                        "humidity": humidity,
                        "battery": battery,
                        "rssi": rssi,
                    }
                )

    return _dedup_rows(rows)


def init_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    try:
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
        con.execute("PRAGMA auto_vacuum=INCREMENTAL;")
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts_epoch INTEGER NOT NULL,
              device TEXT NOT NULL,
              metric TEXT NOT NULL,
              value_c REAL NOT NULL,
              humidity REAL,
              battery REAL,
              rssi REAL,
              topic TEXT NOT NULL,
              raw_payload TEXT NOT NULL
            );
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_samples_ts ON samples(ts_epoch);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_samples_device_metric_ts ON samples(device, metric, ts_epoch);")
        con.commit()
    finally:
        con.close()


@dataclass
class AppState:
    db_path: Path
    broker: str
    mqtt_port: int
    topic: str
    machine_host: str
    machine_interval: int
    retention_days: int
    event_queue: queue.Queue[dict[str, Any]]
    mqtt_started_at: str | None = None
    mqtt_last_message_at: str | None = None
    mqtt_error: str | None = None
    machine_started_at: str | None = None
    machine_last_poll_at: str | None = None
    machine_error: str | None = None


class ThermalStore:
    def __init__(self, state: AppState):
        self.state = state
        init_db(state.db_path)

    def insert(self, *, topic: str, payload: str, rows: list[dict[str, Any]], update_mqtt: bool = True) -> None:
        if not rows:
            return
        ts = now_epoch()
        con = sqlite3.connect(str(self.state.db_path), timeout=10)
        try:
            con.executemany(
                """
                INSERT INTO samples
                (ts_epoch, device, metric, value_c, humidity, battery, rssi, topic, raw_payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                [
                    (
                        ts,
                        row["device"],
                        row["metric"],
                        row["value_c"],
                        row.get("humidity"),
                        row.get("battery"),
                        row.get("rssi"),
                        topic,
                        payload,
                    )
                    for row in rows
                ],
            )
            con.commit()
        finally:
            con.close()

        if update_mqtt:
            self.state.mqtt_last_message_at = now_iso()
        for row in rows:
            event = {"ts_epoch": ts, "topic": topic, **row}
            try:
                self.state.event_queue.put_nowait(event)
            except queue.Full:
                pass

    def latest(self) -> list[dict[str, Any]]:
        con = sqlite3.connect(str(self.state.db_path), timeout=10)
        con.row_factory = sqlite3.Row
        try:
            rows = con.execute(
                """
                SELECT *
                FROM samples
                WHERE id IN (
                  SELECT id
                  FROM (
                    SELECT
                      id,
                      ROW_NUMBER() OVER (
                        PARTITION BY device, metric, ts_epoch
                        ORDER BY id DESC
                      ) AS rn
                    FROM samples
                  )
                  WHERE rn = 1
                )
                ORDER BY device, metric;
                """
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            con.close()

    def history(self, *, hours: float, device: str | None, metric: str | None) -> list[dict[str, Any]]:
        since = now_epoch() - int(hours * 3600)
        clauses = ["ts_epoch >= ?"]
        params: list[Any] = [since]
        if device and device != "all":
            clauses.append("device = ?")
            params.append(device)
        if metric and metric != "all":
            clauses.append("metric = ?")
            params.append(metric)
        where = " AND ".join(clauses)
        con = sqlite3.connect(str(self.state.db_path), timeout=10)
        con.row_factory = sqlite3.Row
        try:
            rows = con.execute(
                f"""
                SELECT ts_epoch, device, metric, value_c, humidity, battery, rssi, topic
                FROM samples
                WHERE {where}
                ORDER BY ts_epoch ASC, device ASC, metric ASC
                LIMIT 12000;
                """,
                params,
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            con.close()

    def devices(self) -> list[dict[str, Any]]:
        con = sqlite3.connect(str(self.state.db_path), timeout=10)
        con.row_factory = sqlite3.Row
        try:
            rows = con.execute(
                """
                SELECT device, metric, MAX(ts_epoch) AS last_seen
                FROM samples
                GROUP BY device, metric
                ORDER BY device ASC, metric ASC;
                """
            ).fetchall()
        finally:
            con.close()

        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            device = row["device"]
            item = grouped.setdefault(device, {"name": device, "metrics": [], "last_seen": row["last_seen"]})
            item["metrics"].append(row["metric"])
            item["last_seen"] = max(item["last_seen"], row["last_seen"])
        return list(grouped.values())

    def summary(self) -> dict[str, Any]:
        con = sqlite3.connect(str(self.state.db_path), timeout=10)
        con.row_factory = sqlite3.Row
        try:
            row = con.execute(
                """
                SELECT
                  COUNT(*) AS samples,
                  COUNT(DISTINCT device) AS device_count,
                  COUNT(DISTINCT device || char(31) || metric) AS series_count,
                  MIN(ts_epoch) AS first_sample,
                  MAX(ts_epoch) AS last_sample,
                  MAX(value_c) AS max_c,
                  AVG(value_c) AS avg_c
                FROM samples;
                """
            ).fetchone()
            devices = [item["device"] for item in con.execute("SELECT DISTINCT device FROM samples ORDER BY device;")]
        finally:
            con.close()
        return {
            "samples": row["samples"] or 0,
            "device_count": row["device_count"] or 0,
            "series_count": row["series_count"] or 0,
            "first_sample": row["first_sample"],
            "last_sample": row["last_sample"],
            "max_c": row["max_c"],
            "avg_c": row["avg_c"],
            "devices": devices,
        }

    def purge_retention(self) -> int:
        """Delete rows older than retention_days. Returns rows deleted."""
        cutoff = now_epoch() - self.state.retention_days * 24 * 3600
        con = sqlite3.connect(str(self.state.db_path), timeout=10)
        try:
            cur = con.execute("DELETE FROM samples WHERE ts_epoch < ?;", (cutoff,))
            deleted = cur.rowcount
            con.execute("VACUUM;")
            con.commit()
            return deleted
        finally:
            con.close()


class MqttWorker(threading.Thread):
    def __init__(self, state: AppState, store: ThermalStore):
        super().__init__(daemon=True)
        self.state = state
        self.store = store
        self.stop_event = threading.Event()
        self.proc: subprocess.Popen[str] | None = None
        self._stderr_thread: threading.Thread | None = None

    def _drain_stderr(self) -> None:
        """Background thread to drain stderr so the child process doesn't block."""
        if self.proc and self.proc.stderr:
            try:
                self.proc.stderr.read()
            except Exception:
                pass

    def _start_stderr_drain(self) -> None:
        self._stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr_thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.proc and self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait(timeout=5)

    def run(self) -> None:
        self.state.mqtt_started_at = now_iso()
        while not self.stop_event.is_set():
            cmd = [
                "mosquitto_sub",
                "-h",
                self.state.broker,
                "-p",
                str(self.state.mqtt_port),
                "-t",
                self.state.topic,
                "-v",
            ]
            try:
                self.proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )
            except OSError as exc:
                self.state.mqtt_error = str(exc)
                time.sleep(5)
                continue

            self._start_stderr_drain()
            assert self.proc.stdout is not None

            try:
                for line in self.proc.stdout:
                    if self.stop_event.is_set():
                        break
                    topic, sep, payload = line.rstrip("\n").partition(" ")
                    if not sep:
                        continue
                    rows = parse_payload(topic, payload)
                    self.store.insert(topic=topic, payload=payload, rows=rows)
            except Exception:
                pass

            if self.stop_event.is_set():
                break

            returncode = self.proc.poll()
            err = ""
            if self.proc.stderr:
                try:
                    err = self.proc.stderr.read().strip()
                except Exception:
                    pass
            if returncode not in (None, 0):
                self.state.mqtt_error = err or f"mosquitto_sub exited {returncode}"
            self.proc.wait()

            self.stop_event.wait(2)


def parse_machine_thermals(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    acpi_values: list[float] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("GPU,"):
            parts = [part.strip() for part in line.split(",")]
            if len(parts) >= 2:
                temp = as_float(parts[1])
                if temp is not None:
                    rows.append(
                        {
                            "device": "dgx-spark",
                            "metric": "gpu",
                            "value_c": temp,
                            "humidity": None,
                            "battery": None,
                            "rssi": None,
                        }
                    )
            continue
        if line.startswith("THERMAL,"):
            parts = [part.strip() for part in line.split(",", 3)]
            if len(parts) >= 4:
                idx = parts[1]
                temp_milli = as_float(parts[3])
                if temp_milli is None:
                    continue
                temp = temp_milli / 1000 if abs(temp_milli) > 200 else temp_milli
                acpi_values.append(temp)
                rows.append(
                    {
                        "device": "dgx-spark",
                        "metric": f"acpi_{idx}",
                        "value_c": temp,
                        "humidity": None,
                        "battery": None,
                        "rssi": None,
                    }
                )
    if acpi_values:
        rows.append(
            {
                "device": "dgx-spark",
                "metric": "acpi_max",
                "value_c": max(acpi_values),
                "humidity": None,
                "battery": None,
                "rssi": None,
            }
        )
    return rows


class MachineWorker(threading.Thread):
    def __init__(self, state: AppState, store: ThermalStore):
        super().__init__(daemon=True)
        self.state = state
        self.store = store
        self.stop_event = threading.Event()

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        self.state.machine_started_at = now_iso()
        consecutive_failures = 0
        first_error: str | None = None
        max_failures = 3  # stop polling after 3 consecutive failures

        while not self.stop_event.is_set():
            cmd = [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=8",
                self.state.machine_host,
                r"""printf 'GPU,'; nvidia-smi --query-gpu=temperature.gpu,power.draw,utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -n1 || true; i=0; for z in /sys/class/thermal/thermal_zone*; do [ -r "$z/temp" ] || continue; i=$((i+1)); type=$(cat "$z/type" 2>/dev/null || basename "$z"); temp=$(cat "$z/temp" 2>/dev/null || true); printf 'THERMAL,%s,%s,%s\n' "$i" "$type" "$temp"; done""",
            ]
            try:
                result = subprocess.run(cmd, text=True, capture_output=True, timeout=15, check=False)
            except Exception as exc:
                if first_error is None:
                    first_error = str(exc)
                self.state.machine_error = str(exc)
                # exponential backoff: 5, 10, 20 seconds, cap at 30s
                wait = min(5 * (2 ** consecutive_failures), 30)
                self.stop_event.wait(wait)
                continue

            if result.returncode != 0:
                error_msg = (result.stderr or result.stdout).strip() or f"ssh exited {result.returncode}"
                if first_error is None:
                    first_error = error_msg
                self.state.machine_error = error_msg
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    self.state.machine_error = f"Consecutive failures ({consecutive_failures}): {first_error}"
                    self.stop_event.wait(30)
                    break
                # exponential backoff
                wait = min(5 * (2 ** consecutive_failures), 30)
                self.stop_event.wait(wait)
                continue

            # Success — reset
            rows = parse_machine_thermals(result.stdout)
            if rows:
                payload = json.dumps({"host": self.state.machine_host, "raw": result.stdout}, separators=(",", ":"))
                self.store.insert(topic="machine/dgx-spark/thermal", payload=payload, rows=rows, update_mqtt=False)
                self.state.machine_last_poll_at = now_iso()
                self.state.machine_error = None
                consecutive_failures = 0
                first_error = None
            else:
                if first_error is None:
                    first_error = "No machine thermal rows parsed"
                self.state.machine_error = "No machine thermal rows parsed"
                consecutive_failures += 1

            self.stop_event.wait(self.state.machine_interval)


def json_response(handler: BaseHTTPRequestHandler, obj: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
    body = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def csv_response(handler: BaseHTTPRequestHandler, rows: list[dict[str, Any]]) -> None:
    output = io.StringIO()
    fieldnames = ["ts_epoch", "device", "metric", "value_c", "humidity", "battery", "rssi", "topic"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    body = output.getvalue().encode("utf-8")
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "text/csv; charset=utf-8")
    handler.send_header("Content-Disposition", 'attachment; filename="thermal-readings.csv"')
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def read_static(name: str) -> bytes:
    return (Path(__file__).parent / "static" / name).read_bytes()


class Handler(BaseHTTPRequestHandler):
    state: AppState
    store: ThermalStore

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[%s] %s\n" % (now_iso(), fmt % args))

    def do_HEAD(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in {
            "/",
            "/about",
            "/app.js",
            "/api/status",
            "/api/history",
            "/api/devices",
            "/api/summary",
            "/api/download",
            "/api/events",
        }:
            self.send_response(HTTPStatus.OK)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            body = read_static("index.html")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/about":
            body = read_static("about.html")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/app.js":
            body = read_static("app.js")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/status":
            json_response(
                self,
                {
                    "broker": self.state.broker,
                    "mqtt_port": self.state.mqtt_port,
                    "topic": self.state.topic,
                    "started_at": self.state.mqtt_started_at,
                    "last_message_at": self.state.mqtt_last_message_at,
                    "mqtt_error": self.state.mqtt_error,
                    "machine_host": self.state.machine_host,
                    "machine_started_at": self.state.machine_started_at,
                    "machine_last_poll_at": self.state.machine_last_poll_at,
                    "machine_error": self.state.machine_error,
                    "latest": self.store.latest(),
                },
            )
            return
        if parsed.path == "/api/history":
            params = urllib.parse.parse_qs(parsed.query)
            hours = as_float((params.get("hours") or ["6"])[0]) or 6
            device = (params.get("device") or ["all"])[0]
            metric = (params.get("metric") or ["all"])[0]
            json_response(self, {"samples": self.store.history(hours=hours, device=device, metric=metric)})
            return
        if parsed.path == "/api/devices":
            json_response(self, {"devices": self.store.devices()})
            return
        if parsed.path == "/api/summary":
            json_response(self, self.store.summary())
            return
        if parsed.path == "/api/download":
            params = urllib.parse.parse_qs(parsed.query)
            hours = as_float((params.get("hours") or ["24"])[0]) or 24
            device = (params.get("device") or ["all"])[0]
            metric = (params.get("metric") or ["all"])[0]
            csv_response(self, self.store.history(hours=hours, device=device, metric=metric))
            return
        if parsed.path == "/api/events":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            deadline = time.time() + 60
            while time.time() < deadline:
                try:
                    event = self.state.event_queue.get(timeout=10)
                    self.wfile.write(f"data: {json.dumps(event, separators=(',', ':'))}\n\n".encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    break
                except TimeoutError:
                    break
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/sample":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8")
        try:
            obj = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Expected JSON")
            return
        topic = str(obj.get("topic") or "esp32/manual/telemetry")
        payload_obj = obj.get("payload", obj)
        payload = json.dumps(payload_obj, separators=(",", ":")) if isinstance(payload_obj, (dict, list)) else str(payload_obj)
        rows = parse_payload(topic, payload)
        self.store.insert(topic=topic, payload=payload, rows=rows)
        json_response(self, {"accepted": len(rows), "rows": rows})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ESP32 thermal lab dashboard")
    parser.add_argument("--bind", default=os.environ.get("ESP32_THERMAL_BIND", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("ESP32_THERMAL_PORT", "8765")))
    parser.add_argument("--broker", default=os.environ.get("ESP32_MQTT_HOST", "192.168.186.19"))
    parser.add_argument("--mqtt-port", type=int, default=int(os.environ.get("ESP32_MQTT_PORT", "1884")))
    parser.add_argument("--topic", default=os.environ.get("ESP32_MQTT_TOPIC", "#"))
    parser.add_argument("--machine-host", default=os.environ.get("ESP32_THERMAL_MACHINE_HOST", "kpopsparky"))
    parser.add_argument("--machine-interval", type=int, default=int(os.environ.get("ESP32_THERMAL_MACHINE_INTERVAL", "30")))
    parser.add_argument(
        "--db",
        default=os.environ.get(
            "ESP32_THERMAL_DB",
            str(Path.home() / ".local/share/esp32-thermal-lab/thermal.sqlite3"),
        ),
    )
    parser.add_argument("--retention-days", type=int, default=int(os.environ.get("ESP32_THERMAL_RETENTION_DAYS", "30")))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = AppState(
        db_path=Path(args.db).expanduser(),
        broker=args.broker,
        mqtt_port=args.mqtt_port,
        topic=args.topic,
        machine_host=args.machine_host,
        machine_interval=args.machine_interval,
        retention_days=args.retention_days,
        event_queue=queue.Queue(maxsize=1000),
    )
    store = ThermalStore(state)
    Handler.state = state
    Handler.store = store

    worker = MqttWorker(state, store)
    worker.start()
    machine_worker = MachineWorker(state, store)
    machine_worker.start()

    server = ThreadingHTTPServer((args.bind, args.port), Handler)
    server.socket.settimeout(1.0)

    def shutdown(_signum: int, _frame: Any) -> None:
        worker.stop()
        machine_worker.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    print(
        f"[{now_iso()}] esp32-thermal-lab listening on http://{args.bind}:{args.port} "
        f"mqtt={args.broker}:{args.mqtt_port} topic={args.topic} db={state.db_path}",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        worker.stop()
        machine_worker.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
