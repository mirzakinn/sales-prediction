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
import time
import sys
import io

# Windows konsol encoding sorunu için - print fonksiyonunu override et
import builtins
original_print = builtins.print

def safe_print(*args, **kwargs):
    try:
        original_print(*args, **kwargs)
    except UnicodeEncodeError:
        # Unicode karakterleri ASCII'ye çevir
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('ascii', 'ignore').decode('ascii'))
            else:
                safe_args.append(str(arg))
        original_print(*safe_args, **kwargs)

# print fonksiyonunu güvenli versiyonla değiştir
builtins.print = safe_print

def find_best_model(x_train, y_train, x_test, y_test, cv_folds=5, detailed_mode=False):
    """
    Tüm mevcut algoritmaları test ederek en iyi performansı veren modeli bulur.
    
    Args:
        x_train: Eğitim verisi özellikleri
        y_train: Eğitim verisi hedef değişkeni
        x_test: Test verisi özellikleri
        y_test: Test verisi hedef değişkeni
        cv_folds: Cross-validation fold sayısı
        detailed_mode: Detaylı mod (daha fazla parametre kombinasyonu)
    
    Returns:
        dict: En iyi model bilgileri
    """
    
    # Dataset boyutunu kontrol et
    n_samples = len(x_train)
    n_features = x_train.shape[1] if hasattr(x_train, 'shape') else len(x_train[0])
    
    # Büyük dataset kategorilendirmesi
    is_large_dataset = n_samples > 50000 or n_features > 20
    is_huge_dataset = n_samples > 200000
    
    if is_huge_dataset:
        print(f"ÇOK BÜYÜK DATASET TESPIT EDİLDİ: {n_samples:,} satır, {n_features} kolon")
        print("Sampling + Ultra hızlı mod aktif - Tahmini süre: 5-8 dakika")
        detailed_mode = False  # Zorla kapat
    elif is_large_dataset:
        print(f"BÜYÜK DATASET TESPIT EDİLDİ: {n_samples:,} satır, {n_features} kolon")
        print("Ultra hızlı mod aktif - Tahmini süre: 8-12 dakika")
        detailed_mode = False  # Zorla kapat
    
    # Sampling fonksiyonu
    def smart_sample(x_train, y_train, x_test, y_test, sample_size=80000):
        from sklearn.model_selection import train_test_split
        
        if len(x_train) > sample_size:
            print(f"Hızlı model karşılaştırması için {sample_size:,} satır sample alınıyor...")
            x_sample, _, y_sample, _ = train_test_split(
                x_train, y_train, 
                train_size=sample_size, 
                random_state=42, 
                stratify=None
            )
            # Test setini de orantılı küçült
            test_ratio = min(0.3, 20000 / len(x_test))
            x_test_sample, _, y_test_sample, _ = train_test_split(
                x_test, y_test, train_size=test_ratio, random_state=42
            )
            print(f"Sample boyutu: Eğitim {len(x_sample):,}, Test {len(x_test_sample):,}")
            return x_sample, y_sample, x_test_sample, y_test_sample
        return x_train, y_train, x_test, y_test
    
    # Sampling uygula
    if is_huge_dataset:
        x_train_work, y_train_work, x_test_work, y_test_work = smart_sample(
            x_train, y_train, x_test, y_test, sample_size=80000
        )
    else:
        x_train_work, y_train_work, x_test_work, y_test_work = x_train, y_train, x_test, y_test
    
    # Ultra hızlı mod parametre gridleri (büyük dataset için)
    ultra_fast_params = {
        'linear_regression': {
            'fit_intercept': [True, False]
        },
        'ridge': {
            'alpha': [1.0, 10.0],
            'solver': ['auto']
        },
        'lasso': {
            'alpha': [1.0, 10.0],
            'max_iter': [1000]
        },
        'elasticnet': {
            'alpha': [1.0],
            'l1_ratio': [0.5, 0.7]
        },
        'knn': {
            'n_neighbors': [5, 10],
            'weights': ['uniform']
        },
        'svr': {
            'C': [1.0],
            'gamma': ['scale']
        },
        'decision_tree': {
            'max_depth': [10, 15],
            'min_samples_leaf': [4]
        },
        'random_forest': {
            'n_estimators': [50, 100],
            'max_depth': [10]
        },
        'xgboost': {
            'n_estimators': [50, 100],
            'learning_rate': [0.1],
            'max_depth': [6]
        },
        'lightgbm': {
            'n_estimators': [50, 100],
            'learning_rate': [0.1],
            'max_depth': [10]
        }
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
    
    # Parametre gridini seç
    if is_large_dataset:
        param_grids = ultra_fast_params
        cv_folds = 3  # Büyük dataset için daha az CV fold
        mode_text = "ULTRA HIZLI MOD (Büyük Dataset)"
    else:
        param_grids = detailed_params if detailed_mode else fast_params
        mode_text = "DETAYLI MOD" if detailed_mode else "HIZLI MOD"
    
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
    
    results = []
    
    print(f"Tum modeller test ediliyor... ({mode_text})")
    if detailed_mode and not is_large_dataset:
        print("UYARI: Detayli mod 5-10 dakika surebilir!")
    elif is_large_dataset:
        print(f"CV Folds: {cv_folds} (hızlandırılmış)")
    
    for model_name, config in models_config.items():
        try:
            start_time = time.time()
            print(f"{model_name} test ediliyor...")
            
            # GridSearchCV ile en iyi parametreleri bul
            grid_search = GridSearchCV(
                config['model'],
                config['params'],
                cv=cv_folds,
                scoring='r2',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(x_train_work, y_train_work)
            
            # En iyi modeli test et
            best_model = grid_search.best_estimator_
            
            # Büyük dataset ise final modeli tam veri ile eğit
            if is_huge_dataset:
                print(f"  -> En iyi parametreler bulundu, tam dataset ile final eğitim...")
                best_model.fit(x_train, y_train)
            
            y_pred = best_model.predict(x_test)
            r2_score = best_model.score(x_test, y_test)
            
            # Performans metrikleri hesapla
            from sklearn.metrics import r2_score as r2_metric
            r2 = r2_metric(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Cross-validation skoru (büyük dataset için sample kullan)
            cv_data_x = x_train_work if is_huge_dataset else x_train
            cv_data_y = y_train_work if is_huge_dataset else y_train
            cv_scores = cross_val_score(best_model, cv_data_x, cv_data_y, cv=cv_folds, scoring='r2')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
            
            elapsed_time = time.time() - start_time
            
            result = {
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
                'predictions': y_pred
            }
            
            results.append(result)
            print(f"{model_name} tamamlandi - R2: {r2:.4f} ({elapsed_time:.2f}s)")
            
        except Exception as e:
            print(f"{model_name} hata: {str(e)}")
            continue
    
    # Sonuçları R² skoruna göre sırala (en yüksekten en düşüğe)
    results.sort(key=lambda x: x['r2_score'], reverse=True)
    
    if not results:
        raise Exception("Hiçbir model başarıyla eğitilemedi!")
    
    best_result = results[0]
    
    print(f"\nEN IYI MODEL: {best_result['model_name']}")
    print(f"R2 Skoru: {best_result['r2_score']:.4f}")
    print(f"Cross-Validation: {best_result['cv_mean']:.4f} (+-{best_result['cv_std']:.4f})")
    print(f"En Iyi Parametreler: {best_result['best_params']}")
    
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
