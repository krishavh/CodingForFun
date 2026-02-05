const express = require("express");
const path = require("path");
const fs = require("fs");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = process.env.PORT || 3000;

const dataDir = path.join(__dirname, "data");
const dbPath = path.join(dataDir, "brainaccelerator.sqlite");

fs.mkdirSync(dataDir, { recursive: true });

const db = new sqlite3.Database(dbPath);

const MODES = {
  "focus-run": {
    label: "Focus Run",
    durationSec: 60,
    maxScore: 5000,
    memoryBase: 4,
    memoryMax: 8,
    mathMax: 30,
    flashMs: 2000
  },
  "deep-focus": {
    label: "Deep Focus",
    durationSec: 180,
    maxScore: 15000,
    memoryBase: 5,
    memoryMax: 10,
    mathMax: 40,
    flashMs: 2600
  },
  "recall-ladder": {
    label: "Recall Ladder",
    durationSec: 90,
    maxScore: 8000,
    memoryBase: 5,
    memoryMax: 12,
    mathMax: 26,
    flashMs: 1800
  }
};

db.serialize(() => {
  db.run(
    `CREATE TABLE IF NOT EXISTS scores (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      score INTEGER NOT NULL,
      mode TEXT NOT NULL,
      created_at TEXT NOT NULL
    )`
  );

  db.run(
    `CREATE TABLE IF NOT EXISTS profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      created_at TEXT NOT NULL,
      last_practice_date TEXT,
      streak_count INTEGER DEFAULT 0,
      best_streak INTEGER DEFAULT 0,
      last_run_at TEXT
    )`
  );

  db.run(
    `CREATE TABLE IF NOT EXISTS runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      profile_id INTEGER NOT NULL,
      score INTEGER NOT NULL,
      mode TEXT NOT NULL,
      duration_sec INTEGER NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY(profile_id) REFERENCES profiles(id)
    )`
  );
});

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.get("/health", (req, res) => {
  res.json({ ok: true });
});

app.get("/api/modes", (req, res) => {
  const modes = Object.entries(MODES).map(([key, mode]) => ({
    key,
    ...mode
  }));
  res.json({ modes });
});

app.get("/api/profile", (req, res) => {
  const nameRaw = (req.query.name || "").toString().trim();
  const name = nameRaw.replace(/[^a-zA-Z0-9 _-]/g, "").slice(0, 24);
  if (!name) {
    return res.status(400).json({ error: "invalid_name" });
  }

  db.get("SELECT name, created_at, last_practice_date, streak_count, best_streak FROM profiles WHERE name = ?", [name], (err, row) => {
    if (err) {
      return res.status(500).json({ error: "db_read_failed" });
    }
    if (!row) {
      return res.json({ name, exists: false });
    }
    return res.json({ name, exists: true, ...row });
  });
});

app.get("/api/plan", (req, res) => {
  const nameRaw = (req.query.name || "").toString().trim();
  const name = nameRaw.replace(/[^a-zA-Z0-9 _-]/g, "").slice(0, 24);
  if (!name) {
    return res.status(400).json({ error: "invalid_name" });
  }

  db.get("SELECT streak_count, last_practice_date FROM profiles WHERE name = ?", [name], (err, row) => {
    if (err) {
      return res.status(500).json({ error: "db_read_failed" });
    }

    const streakCount = row ? row.streak_count || 0 : 0;
    const lastPractice = row ? row.last_practice_date : null;
    const todayKey = new Date().toISOString().slice(0, 10);

    const tasks = [
      {
        mode: "focus-run",
        label: "Focus Run",
        goal: "1 session",
        reason: "Warm up attention and accuracy."
      },
      {
        mode: "recall-ladder",
        label: "Recall Ladder",
        goal: "1 session",
        reason: "Strengthen short-term recall."
      }
    ];

    if (streakCount >= 3) {
      tasks.push({
        mode: "deep-focus",
        label: "Deep Focus",
        goal: "1 session",
        reason: "Build sustained focus endurance."
      });
    }

    res.json({
      name,
      streak_count: streakCount,
      last_practice_date: lastPractice,
      today: todayKey,
      tasks
    });
  });
});

app.get("/api/scores", (req, res) => {
  const mode = (req.query.mode || "focus-run").toString();
  const limitRaw = parseInt(req.query.limit || "20", 10);
  const limit = Number.isFinite(limitRaw) ? Math.min(Math.max(limitRaw, 1), 100) : 20;

  db.all(
    "SELECT name, score, mode, created_at FROM scores WHERE mode = ? ORDER BY score DESC, created_at ASC LIMIT ?",
    [mode, limit],
    (err, rows) => {
      if (err) {
        return res.status(500).json({ error: "db_read_failed" });
      }
      return res.json({ mode, scores: rows });
    }
  );
});

app.post("/api/scores", (req, res) => {
  const nameRaw = (req.body.name || "").toString().trim();
  const modeRaw = (req.body.mode || "focus-run").toString().trim();
  const scoreRaw = Number(req.body.score);

  const name = nameRaw.replace(/[^a-zA-Z0-9 _-]/g, "").slice(0, 24);
  const mode = modeRaw.replace(/[^a-zA-Z0-9 _-]/g, "").slice(0, 24) || "focus-run";
  const score = Number.isFinite(scoreRaw) ? Math.floor(scoreRaw) : NaN;
  const modeConfig = MODES[mode];

  if (!name || !Number.isFinite(score) || score < 0 || !modeConfig) {
    return res.status(400).json({ error: "invalid_payload" });
  }
  if (score > modeConfig.maxScore) {
    return res.status(400).json({ error: "score_out_of_range" });
  }

  const createdAt = new Date().toISOString();
  const todayKey = createdAt.slice(0, 10);

  db.serialize(() => {
    db.run(
      "INSERT INTO profiles (name, created_at, last_practice_date, streak_count, best_streak, last_run_at) VALUES (?, ?, NULL, 0, 0, NULL) ON CONFLICT(name) DO NOTHING",
      [name, createdAt]
    );

    db.get("SELECT id, last_practice_date, streak_count, best_streak FROM profiles WHERE name = ?", [name], (err, profile) => {
      if (err || !profile) {
        return res.status(500).json({ error: "profile_failed" });
      }

      let nextStreak = profile.streak_count || 0;
      let bestStreak = profile.best_streak || 0;
      let lastPractice = profile.last_practice_date;

      if (score > 0) {
        if (!lastPractice) {
          nextStreak = 1;
        } else if (lastPractice === todayKey) {
          // keep streak
        } else {
          const lastDate = new Date(`${lastPractice}T00:00:00Z`);
          const todayDate = new Date(`${todayKey}T00:00:00Z`);
          const diffDays = Math.round((todayDate - lastDate) / 86400000);
          if (diffDays === 1) {
            nextStreak += 1;
          } else {
            nextStreak = 1;
          }
        }

        if (nextStreak > bestStreak) {
          bestStreak = nextStreak;
        }

        lastPractice = todayKey;
      }

      db.run(
        "UPDATE profiles SET last_practice_date = ?, streak_count = ?, best_streak = ?, last_run_at = ? WHERE id = ?",
        [lastPractice, nextStreak, bestStreak, createdAt, profile.id]
      );

      db.run(
        "INSERT INTO scores (name, score, mode, created_at) VALUES (?, ?, ?, ?)",
        [name, score, mode, createdAt]
      );

      db.run(
        "INSERT INTO runs (profile_id, score, mode, duration_sec, created_at) VALUES (?, ?, ?, ?, ?)",
        [profile.id, score, mode, modeConfig.durationSec, createdAt],
        function onInsert(err2) {
          if (err2) {
            return res.status(500).json({ error: "db_write_failed" });
          }
          return res.status(201).json({
            id: this.lastID,
            name,
            score,
            mode,
            created_at: createdAt,
            streak: nextStreak,
            best_streak: bestStreak
          });
        }
      );
    });
  });
});

app.listen(PORT, () => {
  console.log(`BrainAccelerator running on http://localhost:${PORT}`);
});
