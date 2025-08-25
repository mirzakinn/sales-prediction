"""
CRUD operations for trained models using SQLite.

Functions:
- save_trained_model(): Save model metadata and file paths
- get_all_models(): List all trained models
- get_model_by_id(): Get specific model details
- delete_model(): Remove model and associated files
- update_model_status(): Activate/deactivate models
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
from .database import get_db_connection

def get_all_models():
    # database'e bağlananıyoruz
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
        cursor.execute("SELECT * FROM trained_models ORDER BY created_at DESC")
        models = cursor.fetchall()
        
        return models

def save_trained_model(model_name, algorithm, r2_score, mae, mse, rmse, target_column, feature_columns, filename=None, model_params=None):
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Eğer filename verilmemişse default olarak 'data.csv' kullan
    if filename is None:
        filename = "data.csv"
    
    # Model parametrelerini JSON string'e çevir
    model_params_json = json.dumps(model_params) if model_params else None
    
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trained_models 
            (model_type, dataset_filename, target_column, feature_columns, 
             r2_score, mae, mse, rmse, is_active, created_at, model_params)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (algorithm, filename, target_column, str(feature_columns), 
              r2_score, mae, mse, rmse, 1, now, model_params_json))

        conn.commit()
        
        return cursor.lastrowid

def get_model_by_id(model_id):

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM trained_models WHERE id = ? ", (model_id,))

        model = cursor.fetchone()

        return model

def delete_model(model_id):

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM trained_models WHERE id = ?", (model_id,))

        conn.commit()

        