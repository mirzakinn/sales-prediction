from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
import xgboost as xgb
import lightgbm as lgb

from .linear_models import linear_regression, ridge_regression, lasso_regression, elasticnet_regression
from .tree_models import decision_tree, random_forest, xgboost, lightgbm
from .other_models import knn_regression, svr_regression

def grid_search_model(x_train, y_train, model_type):
    """
    GridSearchCV ile en iyi parametreleri bulur
    """
    param_grids = {
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
            'max_iter': [1000, 2000, 3000]
        },
        'elasticnet': {
            'alpha': [0.1, 1.0, 10.0],
            'l1_ratio': [0.1, 0.5, 0.7, 0.9]
        },
        'knn': {
            'n_neighbors': [3, 5, 7, 9],
            'weights': ['uniform', 'distance']
        },
        'svr': {
            'C': [0.1, 1, 10, 100],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1]
        },
        'decision_tree': {
            'max_depth': [None, 5, 10, 15, 20],
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
    
    models = {
        'linear_regression': LinearRegression(),
        'ridge': Ridge(),
        'lasso': Lasso(),
        'elasticnet': ElasticNet(),
        'knn': KNeighborsRegressor(),
        'svr': SVR(),
        'decision_tree': DecisionTreeRegressor(),
        'random_forest': RandomForestRegressor(),
        'xgboost': xgb.XGBRegressor(),
        'lightgbm': lgb.LGBMRegressor(verbose=-1)
    }
    
    if model_type not in param_grids:
        raise ValueError(f"Bilinmeyen model tipi: {model_type}")
    
    model = models[model_type]
    param_grid = param_grids[model_type]
    
    grid_search = GridSearchCV(
        model, 
        param_grid, 
        cv=5, 
        scoring='r2', 
        n_jobs=-1
    )
    
    grid_search.fit(x_train, y_train)
    
    return grid_search.best_estimator_, grid_search.best_params_, grid_search.best_score_

def select_model(x_train, y_train, x_test, y_test, model_type, model_params=None, use_grid_search=False):
    if use_grid_search:
        # GridSearch kullan
        best_model, best_params, best_score = grid_search_model(x_train, y_train, model_type)
        y_pred = best_model.predict(x_test)
        score = best_model.score(x_test, y_test)
        return best_model, y_pred, score
    else:
        # Manuel parametreler kullan
        if model_params is None:
            model_params = {}
            
        if model_type == 'linear_regression':
            fit_intercept = model_params.get('fit_intercept', True)
            positive = model_params.get('positive', False)
            return linear_regression(x_train, x_test, y_train, y_test, fit_intercept=fit_intercept, positive=positive)
        elif model_type == 'ridge':
            alpha = model_params.get('alpha', 1.0)
            solver = model_params.get('solver', 'auto')
            return ridge_regression(x_train, x_test, y_train, y_test, alpha=alpha, solver=solver)
        elif model_type == 'lasso':
            alpha = model_params.get('alpha', 1.0)
            max_iter = model_params.get('max_iter', 1000)
            return lasso_regression(x_train, x_test, y_train, y_test, alpha=alpha, max_iter=max_iter)
        elif model_type == 'elasticnet':
            alpha = model_params.get('alpha', 1.0)
            l1_ratio = model_params.get('l1_ratio', 0.5)
            return elasticnet_regression(x_train, x_test, y_train, y_test, alpha=alpha, l1_ratio=l1_ratio)
        elif model_type == 'knn':
            n_neighbors = model_params.get('n_neighbors', 5)
            weights = model_params.get('weights', 'distance')
            return knn_regression(x_train, x_test, y_train, y_test, n_neighbors=n_neighbors, weights=weights)
        elif model_type == 'svr':
            C = model_params.get('C', 1.0)
            gamma = model_params.get('gamma', 'scale')
            return svr_regression(x_train, x_test, y_train, y_test, C=C, gamma=gamma)
        elif model_type == 'decision_tree':
            max_depth = model_params.get('max_depth', None)
            min_samples_leaf = model_params.get('min_samples_leaf', 1)
            return decision_tree(x_train, x_test, y_train, y_test, max_depth=max_depth, min_samples_leaf=min_samples_leaf)
        elif model_type == 'random_forest':
            n_estimators = model_params.get('n_estimators', 100)
            max_depth = model_params.get('max_depth', None)
            return random_forest(x_train, x_test, y_train, y_test, n_estimators=n_estimators, max_depth=max_depth)
        elif model_type == 'xgboost':
            n_estimators = model_params.get('n_estimators', 100)
            learning_rate = model_params.get('learning_rate', 0.1)
            max_depth = model_params.get('max_depth', 6)
            return xgboost(x_train, x_test, y_train, y_test, n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth)
        elif model_type == 'lightgbm':
            n_estimators = model_params.get('n_estimators', 100)
            learning_rate = model_params.get('learning_rate', 0.1)
            max_depth = model_params.get('max_depth', -1)
            return lightgbm(x_train, x_test, y_train, y_test, n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth)
        else:
            raise ValueError(f"Bilinmeyen model tipi: {model_type}")
