"""
Otomatik En İyi Model Seçici
Tüm algoritmaları test ederek en iyi performansı veren modeli ve parametrelerini bulur.
"""

from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
import numpy as np
import pandas as pd
import time
import sys
import io
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import signal


def auto_select_best_model(x_train, x_test, y_train, y_test, feature_columns=None, timeout_seconds=300):
    """
    Tüm mevcut algoritmaları test ederek en iyi performansı veren modeli bulur.
    
    Args:
        x_train: Eğitim verisi özellikleri
        y_train: Eğitim verisi hedef değişkeni
        x_test: Test verisi özellikleri
        y_test: Test verisi hedef değişkeni
        cv_folds: Cross-validation fold sayısı
        detailed_mode: Detaylı mod (daha fazla parametre kombinasyonu)
        max_time_per_model: Her model için maksimum süre (saniye)
    
    Returns:
        dict: En iyi model bilgileri
    """
    
    # Dataset boyutunu kontrol et
    n_samples = len(x_train)
    n_features = x_train.shape[1] if hasattr(x_train, 'shape') else len(x_train[0])
    
    # Büyük dataset kategorilendirmesi - daha agresif
    is_large_dataset = n_samples > 30000 or n_features > 15
    is_huge_dataset = n_samples > 100000 or n_features > 25
    is_massive_dataset = n_samples > 300000
    
    if is_massive_dataset:
        detailed_mode = False
        max_time_per_model = 120
        cv_folds = 2
    elif is_huge_dataset:
        detailed_mode = False
        max_time_per_model = 180
        cv_folds = 3
    elif is_large_dataset:
        detailed_mode = False
        cv_folds = 3
    else:
        detailed_mode = True
        cv_folds = 5
    
    # Sampling fonksiyonu
    def smart_sample(x_train, y_train, x_test, y_test, sample_size=80000):
        from sklearn.model_selection import train_test_split
        
        if len(x_train) > sample_size:
            x_sample, _, y_sample, _ = train_test_split(
                x_train, y_train, train_size=sample_size, random_state=42
            )
            test_ratio = min(0.3, 20000 / len(x_test))
            x_test_sample, _, y_test_sample, _ = train_test_split(
                x_test, y_test, train_size=test_ratio, random_state=42
            )
            return x_sample, y_sample, x_test_sample, y_test_sample
        return x_train, y_train, x_test, y_test
    
    # Sampling uygula
    if is_huge_dataset or is_massive_dataset:
        x_train_work, y_train_work, x_test_work, y_test_work = smart_sample(
            x_train, y_train, x_test, y_test, sample_size=80000
        )
    else:
        x_train_work, y_train_work, x_test_work, y_test_work = x_train, y_train, x_test, y_test
    
    # ULTRA HIZLI mod parametre gridleri (massive dataset için)
    ultra_minimal_params = {
        'linear_regression': {'fit_intercept': [True]},
        'ridge': {'alpha': [1.0]},
        'lasso': {'alpha': [1.0]},
        'elasticnet': {'alpha': [1.0], 'l1_ratio': [0.5]},
        'knn': {'n_neighbors': [5]},
        'svr': {'C': [1.0], 'gamma': ['scale']},
        'decision_tree': {'max_depth': [10]},
        'random_forest': {'n_estimators': [50], 'max_depth': [10]},
        'xgboost': {'n_estimators': [50], 'learning_rate': [0.1], 'max_depth': [6]},
        'lightgbm': {'n_estimators': [50], 'learning_rate': [0.1], 'max_depth': [10]}
    }
    
    # Ultra hızlı mod parametre gridleri (büyük dataset için)
    ultra_fast_params = {
        'linear_regression': {'fit_intercept': [True, False]},
        'ridge': {'alpha': [1.0, 10.0]},
        'lasso': {'alpha': [1.0, 10.0]},
        'elasticnet': {'alpha': [1.0], 'l1_ratio': [0.5, 0.7]},
        'knn': {'n_neighbors': [5, 10]},
        'svr': {'C': [1.0], 'gamma': ['scale']},
        'decision_tree': {'max_depth': [10, 15]},
        'random_forest': {'n_estimators': [50, 100], 'max_depth': [10]},
        'xgboost': {'n_estimators': [50, 100], 'learning_rate': [0.1], 'max_depth': [6]},
        'lightgbm': {'n_estimators': [50, 100], 'learning_rate': [0.1], 'max_depth': [10]}
    }
    
    # Hızlı mod parametre gridleri
    fast_params = {
        'linear_regression': {
            'fit_intercept': [True, False],
            'positive': [True, False]
        },
        'ridge': {
            'alpha': [0.1, 1.0, 10.0, 100.0],
            'solver': ['auto', 'svd', 'cholesky']
        },
        'lasso': {
            'alpha': [0.1, 1.0, 10.0, 100.0],
            'max_iter': [1000, 2000, 5000]
        },
        'elasticnet': {
            'alpha': [0.1, 1.0, 10.0],
            'l1_ratio': [0.1, 0.5, 0.7, 0.9]
        },
        'knn': {
            'n_neighbors': [3, 5, 7, 10],
            'weights': ['uniform', 'distance']
        },
        'svr': {
            'C': [0.1, 1.0, 10.0],
            'gamma': ['scale', 'auto']
        },
        'decision_tree': {
            'max_depth': [None, 5, 10, 15],
            'min_samples_leaf': [1, 2, 4, 8]
        },
        'random_forest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 5, 10, 15]
        },
        'xgboost': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 6, 9]
        },
        'lightgbm': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [-1, 5, 10, 15]
        }
    }
    
    # Detaylı mod parametre gridleri (daha kapsamlı)
    detailed_params = {
        'linear_regression': {
            'fit_intercept': [True, False],
            'positive': [True, False]
        },
        'ridge': {
            'alpha': [0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0],
            'solver': ['auto', 'svd', 'cholesky', 'lsqr']
        },
        'lasso': {
            'alpha': [0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0],
            'max_iter': [1000, 2000, 3000, 5000, 8000]
        },
        'elasticnet': {
            'alpha': [0.01, 0.1, 0.5, 1.0, 5.0, 10.0],
            'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9, 0.95]
        },
        'knn': {
            'n_neighbors': [3, 5, 7, 9, 11, 15, 20],
            'weights': ['uniform', 'distance'],
            'algorithm': ['auto', 'ball_tree', 'kd_tree']
        },
        'svr': {
            'C': [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0],
            'gamma': ['scale', 'auto'],
            'kernel': ['rbf', 'linear', 'poly']
        },
        'decision_tree': {
            'max_depth': [None, 3, 5, 7, 10, 15, 20],
            'min_samples_leaf': [1, 2, 4, 6, 8, 12],
            'min_samples_split': [2, 5, 10, 15]
        },
        'random_forest': {
            'n_estimators': [50, 100, 150, 200, 300, 400],
            'max_depth': [None, 5, 10, 15, 20, 25],
            'min_samples_leaf': [1, 2, 4, 6]
        },
        'xgboost': {
            'n_estimators': [50, 100, 150, 200, 300, 400],
            'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2, 0.3],
            'max_depth': [3, 4, 5, 6, 7, 8, 9],
            'subsample': [0.8, 0.9, 1.0]
        },
        'lightgbm': {
            'n_estimators': [50, 100, 150, 200, 300, 400],
            'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2, 0.3],
            'max_depth': [-1, 5, 7, 10, 15, 20],
            'num_leaves': [31, 50, 100, 150]
        }
    }
    
    # Parametre gridini seç - daha agresif
    if is_massive_dataset:
        param_grids = ultra_minimal_params
        cv_folds = 2
        mode_text = "🔥 ULTRA MİNİMAL MOD (300K+ Dataset)"
    elif is_huge_dataset:
        param_grids = ultra_fast_params
        cv_folds = 3
        mode_text = "⚡ ULTRA HIZLI MOD (100K+ Dataset)"
    elif is_large_dataset:
        param_grids = ultra_fast_params
        cv_folds = 3
        mode_text = "🚀 HIZLI MOD (30K+ Dataset)"
    else:
        param_grids = detailed_params if detailed_mode else fast_params
        mode_text = "📊 DETAYLI MOD" if detailed_mode else "⚡ STANDART MOD"
    
    # Tüm modeller ve seçilen parametre gridleri
    models_config = {
        'linear_regression': {
            'model': LinearRegression(),
            'params': param_grids['linear_regression']
        },
        'ridge': {
            'model': Ridge(),
            'params': param_grids['ridge']
        },
        'lasso': {
            'model': Lasso(),
            'params': param_grids['lasso']
        },
        'elasticnet': {
            'model': ElasticNet(),
            'params': param_grids['elasticnet']
        },
        'knn': {
            'model': KNeighborsRegressor(),
            'params': param_grids['knn']
        },
        'svr': {
            'model': SVR(),
            'params': param_grids['svr']
        },
        'decision_tree': {
            'model': DecisionTreeRegressor(),
            'params': param_grids['decision_tree']
        },
        'random_forest': {
            'model': RandomForestRegressor(),
            'params': param_grids['random_forest']
        },
        'xgboost': {
            'model': xgb.XGBRegressor(),
            'params': param_grids['xgboost']
        },
        'lightgbm': {
            'model': lgb.LGBMRegressor(verbose=-1),
            'params': param_grids['lightgbm']
        }
    }
    
    # Akıllı model sıralaması - hızlı modeller önce
    model_order = [
        'linear_regression',  # En hızlı
        'ridge', 'lasso',     # Hızlı linear modeller
        'decision_tree',      # Orta hızlı
        'elasticnet',
        'random_forest',      # Ensemble - orta
        'lightgbm',          # Hızlı gradient boosting
        'xgboost',           # Yavaş gradient boosting
        'knn',               # Yavaş (büyük data için)
        'svr'                # En yavaş
    ]
    
    # Erken durma için baseline belirleme
    baseline_r2 = -float('inf')
    early_stop_threshold = 0.1  # R2 < 0.1 ise modeli atla
    models_tested = 0
    max_models_to_test = 6 if is_massive_dataset else 8 if is_huge_dataset else 10
    
    results = []
    total_start_time = time.time()
    
    
    def train_single_model(model_name, config):
        """Tek model eğitimi - timeout ile"""
        try:
            start_time = time.time()
            
            # GridSearchCV ile en iyi parametreleri bul
            grid_search = GridSearchCV(
                config['model'],
                config['params'],
                cv=cv_folds,
                scoring='r2',
                n_jobs=-1,
                verbose=0
            )
            
            # LGBMRegressor için DataFrame kullan
            if model_name == 'lightgbm':
                # DataFrame'e çevir
                x_train_work_df = pd.DataFrame(x_train_work, columns=feature_columns)
                y_train_work_df = pd.Series(y_train_work)
                
                grid_search.fit(x_train_work_df, y_train_work_df)
                
                # En iyi modeli test et
                best_model = grid_search.best_estimator_
                
                # Büyük dataset ise final modeli tam veri ile eğit
                if is_huge_dataset or is_massive_dataset:
                    x_train_df = pd.DataFrame(x_train, columns=feature_columns)
                    y_train_df = pd.Series(y_train)
                    best_model.fit(x_train_df, y_train_df)
                
                x_test_df = pd.DataFrame(x_test, columns=feature_columns)
                y_pred = best_model.predict(x_test_df)
            else:
                grid_search.fit(x_train_work, y_train_work)
                
                # En iyi modeli test et
                best_model = grid_search.best_estimator_
                
                # Büyük dataset ise final modeli tam veri ile eğit
                if is_huge_dataset or is_massive_dataset:
                    best_model.fit(x_train, y_train)
                
                y_pred = best_model.predict(x_test)
            
            # Performans metrikleri hesapla
            from sklearn.metrics import r2_score as r2_metric
            r2 = r2_metric(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Cross-validation skoru
            if model_name == 'lightgbm':
                cv_data_x = x_train_work_df if (is_huge_dataset or is_massive_dataset) else pd.DataFrame(x_train, columns=feature_columns)
                cv_data_y = y_train_work_df if (is_huge_dataset or is_massive_dataset) else pd.Series(y_train)
            else:
                cv_data_x = x_train_work if (is_huge_dataset or is_massive_dataset) else x_train
                cv_data_y = y_train_work if (is_huge_dataset or is_massive_dataset) else y_train
            cv_scores = cross_val_score(best_model, cv_data_x, cv_data_y, cv=cv_folds, scoring='r2')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            elapsed_time = time.time() - start_time
            
            return {
                'model_name': model_name,
                'model': best_model,
                'best_params': grid_search.best_params_,
                'r2_score': r2,
                'mse': mse,
                'mae': mae,
                'rmse': rmse,
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'training_time': elapsed_time,
                'predictions': y_pred,
                'success': True
            }
            
        except Exception as e:
            return {
                'model_name': model_name,
                'error': str(e),
                'success': False
            }
    
    # Modelleri sıralı olarak test et (erken durma ile)
    for model_name in model_order:
        if model_name not in models_config:
            continue
            
        if models_tested >= max_models_to_test:
            break
            
        config = models_config[model_name]
        try:
            
            # Timeout ile model eğitimi
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(train_single_model, model_name, config)
                try:
                    result = future.result(timeout=max_time_per_model)
                    
                    if result['success']:
                        r2_score = result['r2_score']
                        
                        # Erken durma kontrolü
                        if r2_score < early_stop_threshold and models_tested > 2:
                            continue
                        
                        results.append(result)
                        models_tested += 1
                        
                        # Baseline güncelle
                        if r2_score > baseline_r2:
                            baseline_r2 = r2_score
                        
                        elapsed = result['training_time']
                        
                        # Çok iyi sonuç varsa erken bitir
                        if r2_score > 0.95 and models_tested >= 3:
                            break
                            
                    else:
                        pass
                        
                except TimeoutError:
                    future.cancel()
                    continue
                    
        except Exception as e:
            continue
    
    total_elapsed = time.time() - total_start_time
    
    # Sonuçları R² skoruna göre sırala (en yüksekten en düşüğe)
    results.sort(key=lambda x: x['r2_score'], reverse=True)
    
    if not results:
        raise Exception("Hiçbir model başarıyla eğitilemedi!")
    
    best_result = results[0]
    
    
    # Tüm sonuçları da döndür (karşılaştırma için)
    best_result['all_results'] = results
    
    return best_result

def get_model_comparison_summary(results):
    """
    Tüm modellerin performans karşılaştırmasını özetler.
    
    Args:
        results: find_best_model fonksiyonundan dönen sonuç
    
    Returns:
        str: Karşılaştırma özeti
    """
    if 'all_results' not in results:
        return "Karşılaştırma verisi bulunamadı."
    
    all_results = results['all_results']
    
    summary = "\n" + "="*60 + "\n"
    summary += "TUM MODELLERIN PERFORMANS KARSILASTIRMASI\n"
    summary += "="*60 + "\n"
    
    for i, result in enumerate(all_results, 1):
        summary += f"{i:2d}. {result['model_name'].upper():<15} "
        summary += f"R2: {result['r2_score']:.4f} "
        summary += f"RMSE: {result['rmse']:.4f} "
        summary += f"CV: {result['cv_mean']:.4f}+-{result['cv_std']:.4f}\n"
    
    summary += "="*60 + "\n"
    summary += f"KAZANAN: {results['model_name'].upper()}\n"
    summary += f"PERFORMANS ARTISI: "
    
    if len(all_results) > 1:
        second_best = all_results[1]['r2_score']
        improvement = ((results['r2_score'] - second_best) / second_best) * 100
        summary += f"{improvement:.2f}% daha iyi\n"
    else:
        summary += "Tek model test edildi\n"
    
    summary += "="*60
    
    return summary

def get_model_display_name(model_name):
    """Model adını kullanıcı dostu formata çevirir."""
    display_names = {
        'linear_regression': 'Linear Regression',
        'ridge': 'Ridge Regression',
        'lasso': 'Lasso Regression',
        'elasticnet': 'ElasticNet Regression',
        'knn': 'KNN Regression',
        'svr': 'SVR (Support Vector Regression)',
        'decision_tree': 'Decision Tree',
        'random_forest': 'Random Forest',
        'xgboost': 'XGBoost',
        'lightgbm': 'LightGBM'
    }
    return display_names.get(model_name, model_name)
