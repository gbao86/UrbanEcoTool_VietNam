-- Tạo database nếu chưa tồn tại
CREATE DATABASE IF NOT EXISTS urban_eco_tool;
USE urban_eco_tool;

-- Bảng lưu lịch sử phân tích
CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    location_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    analysis_type TEXT NOT NULL,
    analysis_parameters TEXT,
    results TEXT,
    notes TEXT
);

-- Bảng lưu các điểm đề xuất trồng cây
CREATE TABLE IF NOT EXISTS tree_planting_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    priority_score REAL,
    reason TEXT,
    suggested_tree_type TEXT,
    estimated_space_sqm REAL,
    min_distance_to_other_trees REAL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analysis_history(id)
);

-- Tạo index cho tìm kiếm nhanh
CREATE INDEX IF NOT EXISTS idx_location ON analysis_history(location_name);
CREATE INDEX IF NOT EXISTS idx_coordinates ON tree_planting_suggestions(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_analysis_date ON analysis_history(analysis_date); 