-- SQLite Schema for Sales Prediction App

CREATE TABLE IF NOT EXISTS trained_models
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_type TEXT NOT NULL,
    dataset_filename TEXT NOT NULL,
    target_column TEXT NOT NULL,
    feature_columns TEXT NOT NULL,
    r2_score REAL,
    mae REAL,
    mse REAL,
    rmse REAL,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS model_files 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    file_type TEXT,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    created_at TEXT,
    FOREIGN KEY (model_id) REFERENCES trained_models(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS training_sessions 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    test_size REAL,
    handle_missing TEXT,
    created_at TEXT,
    FOREIGN KEY (model_id) REFERENCES trained_models(id) ON DELETE CASCADE
);