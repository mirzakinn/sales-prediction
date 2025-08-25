from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

def decision_tree(x_train, x_test, y_train, y_test, max_depth=None, min_samples_leaf=1):
    regressor = DecisionTreeRegressor(max_depth=max_depth, min_samples_leaf=min_samples_leaf)
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = model.score(x_test, y_test)

    return model, y_pred, score

def random_forest(x_train, x_test, y_train, y_test, n_estimators=100, max_depth=None):
    regressor = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = model.score(x_test, y_test)

    return model, y_pred, score

def xgboost(x_train, x_test, y_train, y_test, n_estimators=100, learning_rate=0.1, max_depth=6):
    regressor = xgb.XGBRegressor(n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth)
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = model.score(x_test, y_test)

    return model, y_pred, score

def lightgbm(x_train, x_test, y_train, y_test, n_estimators=100, learning_rate=0.1, max_depth=-1):
    regressor = lgb.LGBMRegressor(n_estimators=n_estimators, learning_rate=learning_rate, max_depth=max_depth, verbose=-1)
    model = regressor.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    score = model.score(x_test, y_test)

    return model, y_pred, score
