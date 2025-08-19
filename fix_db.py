#!/usr/bin/env python3
"""
Veritabanına model_params kolonu ekler
"""
import sqlite3
import os

# Veritabanı dosyasının varlığını kontrol et
if os.path.exists('sales_prediction.db'):
    print('Veritabani dosyasi mevcut')
else:
    print('Veritabani dosyasi bulunamadi')
    exit()

conn = sqlite3.connect('sales_prediction.db')
cursor = conn.cursor()

# Mevcut tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f'Tablolar: {[table[0] for table in tables]}')

# trained_models tablosunun yapısını kontrol et
cursor.execute('PRAGMA table_info(trained_models);')
columns = cursor.fetchall()
print('trained_models tablosu kolonlari:')
for col in columns:
    print(f'  - {col[1]} ({col[2]})')

# model_params kolonunun var olup olmadığını kontrol et
column_names = [col[1] for col in columns]
if 'model_params' in column_names:
    print('model_params kolonu zaten mevcut')
else:
    print('model_params kolonu eksik, ekleniyor...')
    try:
        cursor.execute('ALTER TABLE trained_models ADD COLUMN model_params TEXT')
        conn.commit()
        print('model_params kolonu basariyla eklendi')
        
        # Kontrol için tekrar tabloyu listele
        cursor.execute('PRAGMA table_info(trained_models);')
        columns = cursor.fetchall()
        print('Guncellenen tablo yapisi:')
        for col in columns:
            print(f'  - {col[1]} ({col[2]})')
            
    except Exception as e:
        print(f'Hata: {e}')

conn.close()
print('Islem tamamlandi.')
