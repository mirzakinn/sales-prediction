"""
Sonuçlar Blueprint'i - Kullanıcı Odaklı ML Pipeline
Veri yükleme → Kolon seçimi → Model eğitimi → Tahmin yapma akışı
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json
import os
import pandas as pd
from utils.data_utils import read_file_by_extension, handle_missing_data, handle_outliers
from utils.ml_utils import *
from database.crud import *
from utils.file_utils import save_model_files, allowed_file

# Global değişkenler - eğitilen model objeleri
CURRENT_MODEL = None
CURRENT_ENCODERS = None
CURRENT_SCALER = None

results_bp = Blueprint('results', __name__)


