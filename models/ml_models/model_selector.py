from sklearn.model_selection import GridSearchCV
from .linear_models import linear_regression, ridge_regression, lasso_regression, elasticnet_regression
from .tree_models import decision_tree, random_forest, xgboost, lightgbm
from .other_models import knn_regression, svr_regression

def select_model(x_train, y_train, x_test, y_test, model_type, model_params, use_grid_search=False):
    """
    Model seçimi ve eğitimi yapan ana fonksiyon
    """
    
    if use_grid_search:
        return _train_with_grid_search(x_train, y_train, x_test, y_test, model_type, model_params)
    else:
        return _train_single_model(x_train, y_train, x_test, y_test, model_type, model_params)

def _train_single_model(x_train, y_train, x_test, y_test, model_type, model_params):
    """
    Tek model eğitimi (grid search olmadan)
    """
    
    if model_type == 'linear_regression':
        return linear_regression(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'ridge':
        return ridge_regression(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'lasso':
        return lasso_regression(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'elasticnet':
        return elasticnet_regression(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'decision_tree':
        return decision_tree(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'random_forest':
        return random_forest(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'xgboost':
        return xgboost(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'lightgbm':
        return lightgbm(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'knn':
        return knn_regression(x_train, x_test, y_train, y_test, **model_params)
    
    elif model_type == 'svr':
        return svr_regression(x_train, x_test, y_train, y_test, **model_params)
    
    else:
        raise ValueError(f"Desteklenmeyen model türü: {model_type}")

def _train_with_grid_search(x_train, y_train, x_test, y_test, model_type, model_params):
    """
    Grid search ile model eğitimi
    """
    from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.svm import SVR
    import xgboost as xgb
    import lightgbm as lgb
    
    # Model ve parametre grid'lerini tanımla
    model_configs = {
        'linear_regression': {
            'model': LinearRegression(),
            'params': {'fit_intercept': [True, False]}
        },
        'ridge': {
            'model': Ridge(),
            'params': {'alpha': [0.1, 1.0, 10.0]}
        },
        'lasso': {
            'model': Lasso(),
            'params': {'alpha': [0.1, 1.0, 10.0]}
        },
        'elasticnet': {
            'model': ElasticNet(),
            'params': {'alpha': [0.1, 1.0], 'l1_ratio': [0.1, 0.5, 0.9]}
        },
        'decision_tree': {
            'model': DecisionTreeRegressor(),
            'params': {'max_depth': [3, 5, 10, None], 'min_samples_leaf': [1, 2, 4]}
        },
        'random_forest': {
            'model': RandomForestRegressor(),
            'params': {'n_estimators': [50, 100, 200], 'max_depth': [3, 5, 10, None]}
        },
        'xgboost': {
            'model': xgb.XGBRegressor(),
            'params': {'n_estimators': [50, 100], 'learning_rate': [0.1, 0.2], 'max_depth': [3, 6]}
        },
        'lightgbm': {
            'model': lgb.LGBMRegressor(verbose=-1),
            'params': {'n_estimators': [50, 100], 'learning_rate': [0.1, 0.2], 'max_depth': [3, 6]}
        },
        'knn': {
            'model': KNeighborsRegressor(),
            'params': {'n_neighbors': [3, 5, 7], 'weights': ['uniform', 'distance']}
        },
        'svr': {
            'model': SVR(),
            'params': {'C': [0.1, 1.0, 10.0], 'gamma': ['scale', 'auto']}
        }
    }
    
    if model_type not in model_configs:
        raise ValueError(f"Desteklenmeyen model türü: {model_type}")
    
    config = model_configs[model_type]
    
    # Grid search yap
    grid_search = GridSearchCV(
        config['model'], 
        config['params'], 
        cv=5, 
        scoring='r2',
        n_jobs=-1
    )
    
    grid_search.fit(x_train, y_train)
    
    # En iyi modeli al ve tahmin yap
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(x_test)
    score = best_model.score(x_test, y_test)
    
    return best_model, y_pred, score
