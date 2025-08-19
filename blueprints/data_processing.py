from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
import os
import pandas as pd
from utils.data_utils import read_file_by_extension, handle_missing_data, handle_outliers
from utils.ml_utils import *
from utils.linear_models import *
from utils.tree_models import *
from utils.other_models import *
from utils.model_selector import *
from database.crud import *
from utils.file_utils import save_model_files, allowed_file

CURRENT_MODEL = None
CURRENT_ENCODERS = None
CURRENT_SCALER = None

processing_bp = Blueprint('processing', __name__)

@processing_bp.route('/select-columns/<filename>')
def select_columns(filename):
    """
    Kolon seçimi sayfası - kullanıcı hangi kolonları analiz edeceğini seçer
    """
    try:
        filepath = os.path.join('uploads', filename)
        if not os.path.exists(filepath):
            flash('Dosya bulunamadı!', 'error')
            return redirect(url_for('upload.upload_file'))
        
        # CSV dosyasını oku ve kolonları al
        from utils.data_utils import read_file_by_extension
        df = read_file_by_extension(filepath, filename)
        
        # Boş DataFrame kontrolü
        if df.empty:
            flash('Dosya boş veya geçersiz!', 'error')
            return redirect(url_for('upload.upload_file'))
        
        # Kolon adlarını temizle (boşlukları kaldır, özel karakterleri düzelt)
        df.columns = df.columns.str.strip()
        columns = df.columns.tolist()
        
        # İlk 5 satırı önizleme için al - güvenli şekilde
        try:
            preview_data = df.head(5).fillna('').to_dict('records')
            # Çok uzun değerleri kısalt
            for row in preview_data:
                for key, value in row.items():
                    if isinstance(value, str) and len(str(value)) > 50:
                        row[key] = str(value)[:50] + "..."
        except Exception:
            preview_data = []
        
        # Kolon tiplerini belirle - daha güvenli
        column_types = {}
        for col in columns:
            try:
                dtype = str(df[col].dtype)
                # Numeric olmaya çalış
                if 'int' in dtype or 'float' in dtype:
                    column_types[col] = 'sayısal'
                else:
                    # String bir kolonu numeric'e çevirmeyi dene
                    try:
                        pd.to_numeric(df[col].dropna().head(10), errors='raise')
                        column_types[col] = 'sayısal'
                    except:
                        column_types[col] = 'metin'
            except Exception:
                column_types[col] = 'metin'
        
        # Dosya bilgilerini session'a kaydet
        session['current_file'] = filename
        session['file_columns'] = columns
        session['column_types'] = column_types
        
        return render_template('select_columns.html', 
                             filename=filename, 
                             columns=columns, 
                             column_types=column_types,
                             preview_data=preview_data,
                             df_shape=df.shape)
        
    except Exception as e:
        print(f"Select columns error: {str(e)}", flush=True)
        flash(f'Dosya işleme hatası: {str(e)}', 'error')
        return redirect(url_for('upload.upload_file'))

@processing_bp.route('/clear-session')
def clear_session():
    """
    Session'ı temizler ve başa döner
    """
    session.clear()
    flash('Oturum temizlendi. Yeni bir analiz başlatabilirsiniz.', 'info')
    return redirect(url_for('main.index'))