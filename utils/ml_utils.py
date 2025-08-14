import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb

# kategorik verileri sayısal hale getir
# label encoding ve one-hot encoding
def encoding_data(df):
    df_processed = df.copy()
    encoders = {}
    
    categorical_columns = df_processed.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        encoder = LabelEncoder()
        df_processed[col] = encoder.fit_transform(df_processed[col])
        encoders[col] = encoder
    # label encoding ile kategorik veriler sayısal değerlere çevrildi
    return df_processed, encoders

def scaling_data(df, feature_columns, target_column):

    df_processed = df.copy()

    scaler = StandardScaler() # standardScaller ile her sütunun ortalaması 0, standart sapması 1 yapılır
    x = df_processed[feature_columns].values
    y = df_processed[target_column].values

    x = scaler.fit_transform(x) # feature kolonlarını scale ediyorum
    
    data = np.hstack((x, np.reshape(y, (-1, 1)))) # feature kolonu ile target kolonunu birleştiriyorum

    return data, x, y, scaler

def data_split(x, y, test_size):
    x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=test_size, random_state=42)
    return x_train, x_test, y_train, y_test


def linear_regression(x_train, x_test, y_train, y_test):
    reg = LinearRegression()
    reg.fit(x_train, y_train)
    y_pred = reg.predict(x_test)
    score = reg.score(x_test, y_test)

    return reg, y_pred, score

def ridge_regression(x_train, x_test, y_train, y_test, alpha=1.0):
    ridge = Ridge(alpha=alpha)
    ridge.fit(x_train, y_train)
    y_pred = ridge.predict(x_test)
    score = ridge.score(x_test, y_test)

    return ridge, y_pred, score

def lasso_regression(x_train, x_test, y_train, y_test, alpha=1.0):
    lasso = Lasso(alpha=alpha)
    lasso.fit(x_train, y_train)
    y_pred = lasso.predict(x_test)
    score = lasso.score(x_test, y_test)

    return lasso, y_pred, score

def elasticnet_regression(x_train, x_test, y_train, y_test, alpha=1.0, l1_ratio=0.5):
    elasticnet = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
    elasticnet.fit(x_train, y_train)
    y_pred = elasticnet.predict(x_test)
    score = elasticnet.score(x_test, y_test)

    return elasticnet, y_pred, score

def knn_regression(x_train, x_test, y_train, y_test, n_neighbors=5, weights='distance'):
    knn = KNeighborsRegressor(n_neighbors=n_neighbors, weights=weights)
    knn.fit(x_train, y_train)
    y_pred = knn.predict(x_test)
    score = knn.score(x_test, y_test)

    return knn, y_pred, score

def decision_tree(x_train, x_test, y_train, y_test):
    regressor = DecisionTreeRegressor()
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = model.score(x_test, y_test)

    return model, y_pred, score

def random_forest(x_train, x_test, y_train, y_test):
    regressor = RandomForestRegressor(n_estimators=200)
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = model.score(x_test, y_test)

    return model, y_pred, score

def xgboost(x_train, x_test, y_train, y_test):
    regressor = xgb.XGBRegressor()
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = model.score(x_test, y_test)

    return model, y_pred, score

def select_model(x_train, y_train, x_test, y_test, model_type, model_params=None):
    if model_params is None:
        model_params = {}
        
    if model_type == 'linear_regression':
        return linear_regression(x_train, x_test, y_train, y_test)
    elif model_type == 'ridge':
        alpha = model_params.get('alpha', 1.0)
        return ridge_regression(x_train, x_test, y_train, y_test, alpha=alpha)
    elif model_type == 'lasso':
        alpha = model_params.get('alpha', 1.0)
        return lasso_regression(x_train, x_test, y_train, y_test, alpha=alpha)
    elif model_type == 'elasticnet':
        alpha = model_params.get('alpha', 1.0)
        l1_ratio = model_params.get('l1_ratio', 0.5)
        return elasticnet_regression(x_train, x_test, y_train, y_test, alpha=alpha, l1_ratio=l1_ratio)
    elif model_type == 'knn':
        n_neighbors = model_params.get('n_neighbors', 5)
        weights = model_params.get('weights', 'distance')
        return knn_regression(x_train, x_test, y_train, y_test, n_neighbors=n_neighbors, weights=weights)
    elif model_type == 'decision_tree':
        return decision_tree(x_train, x_test, y_train, y_test)
    elif model_type == 'random_forest':
        return random_forest(x_train, x_test, y_train, y_test)
    elif model_type == 'xgboost':
        return xgboost(x_train, x_test, y_train, y_test)
    else:
        raise ValueError(f"Bilinmeyen model tipi: {model_type}")

def analyze_model(y_test, y_pred):
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2_score': r2,
        'accuracy': round(r2 * 100, 1)  # R² skorunu yüzdelik accuracy olarak ekle
    }