from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR

def knn_regression(x_train, x_test, y_train, y_test, n_neighbors=5, weights='distance'):
    knn = KNeighborsRegressor(n_neighbors=n_neighbors, weights=weights)
    knn.fit(x_train, y_train)
    y_pred = knn.predict(x_test)
    score = knn.score(x_test, y_test)

    return knn, y_pred, score

def svr_regression(x_train, x_test, y_train, y_test, C=1.0, gamma='scale'):
    svr = SVR(C=C, gamma=gamma)
    svr.fit(x_train, y_train)
    y_pred = svr.predict(x_test)
    score = svr.score(x_test, y_test)

    return svr, y_pred, score
