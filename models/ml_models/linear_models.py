from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet

def linear_regression(x_train, x_test, y_train, y_test, fit_intercept=True, positive=False):
    reg = LinearRegression(fit_intercept=fit_intercept, positive=positive)
    reg.fit(x_train, y_train)
    y_pred = reg.predict(x_test)
    score = reg.score(x_test, y_test)

    return reg, y_pred, score

def ridge_regression(x_train, x_test, y_train, y_test, alpha=1.0, solver='auto'):
    ridge = Ridge(alpha=alpha, solver=solver)
    ridge.fit(x_train, y_train)
    y_pred = ridge.predict(x_test)
    score = ridge.score(x_test, y_test)

    return ridge, y_pred, score

def lasso_regression(x_train, x_test, y_train, y_test, alpha=1.0, max_iter=1000):
    lasso = Lasso(alpha=alpha, max_iter=max_iter)
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
