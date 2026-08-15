const state = {
  latest: [],
  samples: [],
  filters: { device: "all", metric: "all", hours: "6" },
  unit: localStorage.getItem("esp32-thermal-unit") || "c",
};

const colors = [
  "#0f766e",
  "#b45309",
  "#0284c7",
  "#7c3aed",
  "#be123c",
  "#15803d",
  "#a16207",
  "#4338ca",
];

const signalTimeoutSeconds = 60;
const expectedKriUnits = [
  "esp32kriunit1",
  "esp32kriunit2",
  "esp32kriunit3",
  "esp32kriunit4",
  "esp32kriunit5",
  "esp32kriunit6",
];

function isEspDevice(device) {
  return String(device || "").toLowerCase().startsWith("esp32");
}

function isFresh(row, timeout = signalTimeoutSeconds) {
  return row && Math.floor(Date.now() / 1000) - row.ts_epoch < timeout;
}

function displayRows() {
  const rows = [...state.latest];
  const seen = new Set(rows.map((row) => row.device));
  for (const device of expectedKriUnits) {
    if (!seen.has(device)) {
      rows.push({ device, metric: "board", value_c: null, ts_epoch: 0, no_signal: true });
    }
  }
  return rows.map((row) => ({
    ...row,
    no_signal: row.no_signal || (isEspDevice(row.device) && !isFresh(row)),
  }));
}

function fmtTime(epoch) {
  return new Date(epoch * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function fmtDateTime(epoch) {
  return new Date(epoch * 1000).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function ageText(epoch) {
  const seconds = Math.max(0, Math.floor(Date.now() / 1000 - epoch));
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

function tempClass(value) {
  if (value >= 40) return "hot";
  if (value >= 32) return "warn";
  if (value <= 20) return "cool";
  return "";
}

function displayTemp(celsius) {
  if (state.unit === "f") return celsius * 9 / 5 + 32;
  return celsius;
}

function unitLabel() {
  return state.unit === "f" ? "°F" : "°C";
}

function fmtTemp(celsius, digits = 1) {
  return `${displayTemp(celsius).toFixed(digits)} ${unitLabel()}`;
}

async function getJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

function syncFilters() {
  state.filters.device = document.getElementById("device-filter").value;
  state.filters.metric = document.getElementById("metric-filter").value;
  state.filters.hours = document.getElementById("hours-filter").value;
}

function updateFilterOptions() {
  const devices = [...new Set(state.latest.map((row) => row.device))].sort();
  const metrics = [...new Set(state.latest.map((row) => row.metric))].sort();
  const deviceSelect = document.getElementById("device-filter");
  const metricSelect = document.getElementById("metric-filter");

  const fill = (select, values, allLabel, current) => {
    const existing = new Set([...select.options].map((option) => option.value));
    for (const value of values) {
      if (!existing.has(value)) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
      }
    }
    if (![...select.options].some((option) => option.value === current)) {
      select.value = "all";
    }
    select.options[0].textContent = allLabel;
  };

  fill(deviceSelect, devices, "All devices", state.filters.device);
  fill(metricSelect, metrics, "All metrics", state.filters.metric);
}

async function loadDeviceOptions() {
  try {
    const data = await getJson("/api/devices");
    const devices = data.devices || [];
    const deviceSelect = document.getElementById("device-filter");
    const metricSelect = document.getElementById("metric-filter");
    deviceSelect.replaceChildren(new Option("All devices", "all"));
    metricSelect.replaceChildren(new Option("All metrics", "all"));
    const metrics = new Set();
    for (const device of devices) {
      deviceSelect.appendChild(new Option(device.name, device.name));
      for (const metric of device.metrics || []) metrics.add(metric);
    }
    for (const metric of [...metrics].sort()) {
      metricSelect.appendChild(new Option(metric, metric));
    }
  } catch (_) {
    updateFilterOptions();
  }
}

async function refreshSummaryCount() {
  const summary = await getJson("/api/summary");
  document.getElementById("sample-count").textContent = `${Number(summary.samples || 0).toLocaleString()} samples`;
}

function renderStatus(status) {
  document.getElementById("broker").textContent = `${status.broker}:${status.mqtt_port}`;
  const dot = document.getElementById("live-dot");
  const mqttState = document.getElementById("mqtt-state");
  if (status.mqtt_error) {
    dot.classList.remove("live");
    mqttState.textContent = "mqtt error";
  } else if (status.last_message_at) {
    dot.classList.add("live");
    mqttState.textContent = "live";
  } else {
    dot.classList.remove("live");
    mqttState.textContent = "listening";
  }
  document.getElementById("last-message").textContent = status.last_message_at
    ? `last ${new Date(status.last_message_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`
    : "no readings";
}

function renderDevices() {
  const host = document.getElementById("devices");
  host.replaceChildren();
  const rowsForDisplay = displayRows();
  if (!rowsForDisplay.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No ESP32 temperature readings yet.";
    host.appendChild(empty);
    return;
  }

  const grouped = new Map();
  for (const row of rowsForDisplay) {
    if (!grouped.has(row.device)) grouped.set(row.device, []);
    grouped.get(row.device).push(row);
  }

  for (const [device, rows] of [...grouped.entries()].sort()) {
    const onlineRows = rows.filter((row) => !row.no_signal && row.value_c != null);
    const maxTemp = onlineRows.length ? Math.max(...onlineRows.map((row) => row.value_c)) : null;
    const newest = Math.max(...rows.map((row) => row.ts_epoch));
    const card = document.createElement("article");
    card.className = `device ${onlineRows.length ? tempClass(maxTemp) : "no-signal"}`;

    const head = document.createElement("div");
    head.className = "device-head";
    head.innerHTML = `<div class="device-name"></div><div class="age"></div>`;
    head.querySelector(".device-name").textContent = device;
    head.querySelector(".age").textContent = onlineRows.length ? ageText(newest) : "No signal";
    card.appendChild(head);

    for (const row of rows.sort((a, b) => a.metric.localeCompare(b.metric))) {
      const line = document.createElement("div");
      line.className = "metric-row";
      line.innerHTML = `<div class="metric-name"></div><div class="metric-value"></div>`;
      line.querySelector(".metric-name").textContent = row.metric;
      const value = line.querySelector(".metric-value");
      if (row.no_signal || row.value_c == null) {
        value.classList.add("no-signal");
        value.textContent = "No signal";
      } else {
        value.textContent = fmtTemp(row.value_c);
      }
      card.appendChild(line);
    }
    host.appendChild(card);
  }
}

function renderSummary(status) {
  const freshRows = state.latest.filter((row) => !isEspDevice(row.device) || isFresh(row, isEspDevice(row.device) ? signalTimeoutSeconds : 120));
  const devices = new Set(freshRows.map((row) => row.device));
  const espRows = freshRows.filter((row) => isEspDevice(row.device));
  const hottest = [...freshRows].sort((a, b) => b.value_c - a.value_c)[0];
  const espSignals = espRows.map((row) => row.rssi).filter((value) => value != null);

  document.getElementById("summary-devices").textContent = String(devices.size || 0);

  if (hottest) {
    document.getElementById("summary-hot").textContent = fmtTemp(hottest.value_c);
    document.getElementById("summary-hot-note").textContent = `${hottest.device} / ${hottest.metric}`;
  } else {
    document.getElementById("summary-hot").textContent = "--";
    document.getElementById("summary-hot-note").textContent = "Waiting for data.";
  }

  if (espSignals.length) {
    const avg = espSignals.reduce((sum, value) => sum + value, 0) / espSignals.length;
    document.getElementById("summary-rssi").textContent = `${avg.toFixed(0)} dBm`;
  } else {
    document.getElementById("summary-rssi").textContent = "--";
  }

  const statusValue = document.getElementById("summary-status");
  const statusNote = document.getElementById("summary-status-note");
  const maxC = hottest ? hottest.value_c : null;
  if (status.mqtt_error || status.machine_error) {
    statusValue.textContent = "Check";
    statusNote.textContent = status.mqtt_error || status.machine_error;
  } else if (maxC == null) {
    statusValue.textContent = "--";
    statusNote.textContent = "Waiting for readings.";
  } else if (maxC >= 80) {
    statusValue.textContent = "Hot";
    statusNote.textContent = "Try more airflow, less blockage, or moving the probe.";
  } else if (maxC >= 65) {
    statusValue.textContent = "Warm";
    statusNote.textContent = "Good moment to compare fan and vent changes.";
  } else {
    statusValue.textContent = "Stable";
    statusNote.textContent = "Readings are in a comfortable lab range.";
  }
}

function renderSpotlight() {
  const name = document.getElementById("spot-name");
  const value = document.getElementById("spot-value");
  const freshRows = state.latest.filter((row) => !isEspDevice(row.device) || isFresh(row));
  if (!freshRows.length) {
    name.textContent = "Waiting for ESP32 data";
    value.textContent = "--";
    return;
  }
  const row = [...freshRows].sort((a, b) => b.ts_epoch - a.ts_epoch || b.value_c - a.value_c)[0];
  name.textContent = `${row.device} / ${row.metric} · ${ageText(row.ts_epoch)} ago`;
  value.textContent = fmtTemp(row.value_c);
}

function seriesKey(row) {
  return `${row.device} / ${row.metric}`;
}

function renderChart() {
  const canvas = document.getElementById("chart");
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);

  const width = rect.width;
  const height = rect.height;
  ctx.clearRect(0, 0, width, height);

  const pad = { left: 54, right: 18, top: 24, bottom: 42 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  ctx.fillStyle = "#fffdf8";
  ctx.fillRect(0, 0, width, height);

  const samples = state.samples;
  if (!samples.length) {
    ctx.fillStyle = "#706b61";
    ctx.font = "14px system-ui";
    ctx.fillText("Waiting for readings", pad.left, pad.top + 28);
    return;
  }

  const minT = Math.min(...samples.map((row) => row.ts_epoch));
  const maxT = Math.max(...samples.map((row) => row.ts_epoch));
  const displayValues = samples.map((row) => displayTemp(row.value_c));
  const minVRaw = Math.min(...displayValues);
  const maxVRaw = Math.max(...displayValues);
  const step = state.unit === "f" ? 10 : 5;
  const minV = Math.floor((minVRaw - step / 2) / step) * step;
  const maxV = Math.ceil((maxVRaw + step / 2) / step) * step || minV + step;
  const tSpan = Math.max(1, maxT - minT);
  const vSpan = Math.max(1, maxV - minV);

  const x = (t) => pad.left + ((t - minT) / tSpan) * plotW;
  const y = (v) => pad.top + plotH - ((v - minV) / vSpan) * plotH;

  ctx.strokeStyle = "#d8d2c5";
  ctx.lineWidth = 1;
  ctx.fillStyle = "#706b61";
  ctx.font = "12px system-ui";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= 5; i++) {
    const value = minV + (vSpan * i) / 5;
    const yy = y(value);
    ctx.beginPath();
    ctx.moveTo(pad.left, yy);
    ctx.lineTo(width - pad.right, yy);
    ctx.stroke();
    ctx.fillText(`${value.toFixed(0)}${unitLabel()}`, pad.left - 8, yy);
  }

  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (let i = 0; i <= 4; i++) {
    const t = minT + (tSpan * i) / 4;
    ctx.fillText(fmtTime(t), x(t), height - pad.bottom + 14);
  }

  const grouped = new Map();
  for (const row of samples) {
    const key = seriesKey(row);
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(row);
  }

  let idx = 0;
  for (const [key, rows] of grouped.entries()) {
    const color = colors[idx % colors.length];
    idx += 1;
    rows.sort((a, b) => a.ts_epoch - b.ts_epoch);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.25;
    ctx.beginPath();
    rows.forEach((row, index) => {
      const xx = x(row.ts_epoch);
      const yy = y(displayTemp(row.value_c));
      if (index === 0) ctx.moveTo(xx, yy);
      else ctx.lineTo(xx, yy);
    });
    ctx.stroke();
    const last = rows[rows.length - 1];
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x(last.ts_epoch), y(displayTemp(last.value_c)), 3.5, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.textAlign = "left";
  ctx.textBaseline = "top";
  ctx.font = "12px system-ui";
  let legendX = pad.left;
  let legendY = 8;
  idx = 0;
  for (const key of grouped.keys()) {
    const color = colors[idx % colors.length];
    idx += 1;
    ctx.fillStyle = color;
    ctx.fillRect(legendX, legendY + 4, 9, 9);
    ctx.fillStyle = "#22201c";
    ctx.fillText(key, legendX + 14, legendY);
    legendX += Math.min(220, 38 + key.length * 7);
    if (legendX > width - 220) {
      legendX = pad.left;
      legendY += 18;
    }
  }
}

function renderTable() {
  const body = document.getElementById("samples");
  body.replaceChildren();
  const rows = [...state.samples].slice(-250).reverse();
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${fmtDateTime(row.ts_epoch)}</td>
      <td></td>
      <td></td>
      <td>${fmtTemp(row.value_c, 2)}</td>
      <td>${row.rssi == null ? "" : row.rssi}</td>
      <td></td>
    `;
    tr.children[1].textContent = row.device;
    tr.children[2].textContent = row.metric;
    tr.children[5].textContent = row.topic;
    body.appendChild(tr);
  }
}

async function refreshStatus() {
  const status = await getJson("/api/status");
  state.latest = status.latest || [];
  renderStatus(status);
  renderSummary(status);
  updateFilterOptions();
  renderSpotlight();
  renderDevices();
}

async function refreshHistory() {
  syncFilters();
  const params = new URLSearchParams(state.filters);
  const data = await getJson(`/api/history?${params}`);
  state.samples = data.samples || [];
  renderChart();
  renderTable();
}

async function refreshAll() {
  try {
    await refreshStatus();
    await refreshSummaryCount();
    await refreshHistory();
  } catch (error) {
    document.getElementById("mqtt-state").textContent = "offline";
    document.getElementById("live-dot").classList.remove("live");
  }
}

async function injectSample() {
  const n = Math.sin(Date.now() / 40000);
  await getJson("/api/sample", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic: "esp32/test-bench/telemetry",
      payload: {
        device: "test-bench",
        ambient_c: 24 + n,
        inlet_c: 28 + n * 2,
        outlet_c: 33 + n * 3,
        rssi: -48,
      },
    }),
  });
  await refreshAll();
}

function downloadCsv() {
  syncFilters();
  const params = new URLSearchParams({
    hours: state.filters.hours || "24",
    device: state.filters.device || "all",
    metric: state.filters.metric || "all",
  });
  window.location.href = `/api/download?${params}`;
}

document.getElementById("device-filter").addEventListener("change", refreshHistory);
document.getElementById("metric-filter").addEventListener("change", refreshHistory);
document.getElementById("hours-filter").addEventListener("change", refreshHistory);
document.getElementById("download-csv").addEventListener("click", downloadCsv);
for (const button of document.querySelectorAll("[data-unit]")) {
  button.addEventListener("click", () => {
    state.unit = button.dataset.unit;
    localStorage.setItem("esp32-thermal-unit", state.unit);
    document.querySelectorAll("[data-unit]").forEach((item) => {
      item.classList.toggle("active", item.dataset.unit === state.unit);
    });
    renderSpotlight();
    renderSummary({ mqtt_error: null, machine_error: null });
    renderDevices();
    renderChart();
    renderTable();
  });
}
window.addEventListener("resize", renderChart);

document.querySelectorAll("[data-unit]").forEach((item) => {
  item.classList.toggle("active", item.dataset.unit === state.unit);
});

loadDeviceOptions();
refreshAll();
setInterval(refreshAll, 3000);

try {
  const events = new EventSource("/api/events");
  events.onmessage = () => refreshAll();
} catch (_) {
  // Polling above is enough when EventSource is unavailable.
}
