"""
Ana sayfa Blueprint'i
"""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')
