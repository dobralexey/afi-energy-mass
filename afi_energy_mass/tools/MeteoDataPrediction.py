from sklearn import linear_model
from scipy import stats
import numpy as np
import pandas as pd

class LinearRegression(linear_model.LinearRegression):
    """
    LinearRegression class after sklearn's, but calculate t-statistics
    and p-values for model coefficients (betas).
    Additional attributes available after .fit()
    are `t` and `p` which are of the shape (y.shape[1], X.shape[1])
    which is (n_features, n_coefs)
    This class sets the intercept to 0 by default, since usually we include it
    in X.
    """

    def __init__(self, *args, **kwargs):
        if not "fit_intercept" in kwargs:
            kwargs['fit_intercept'] = False
        super(LinearRegression, self)\
                .__init__(*args, **kwargs)

    def fit(self, X, y, n_jobs=1):
        self = super(LinearRegression, self).fit(X, y, n_jobs)

        sse = np.sum((self.predict(X) - y) ** 2, axis=0) / float(X.shape[0] - X.shape[1])
        se = np.array([
            np.sqrt(np.diagonal(sse[i] * np.linalg.inv(np.dot(X.T, X))))
                                                    for i in range(sse.shape[0])
                    ])

        self.t = self.coef_ / se
        self.p = 2 * (1 - stats.t.cdf(np.abs(self.t), y.shape[0] - X.shape[1]))
        return self

class MeteoDataPrediction:

    def __init__(self, df, df_full):
        self.df = df
        self.df_full = df_full

    def meteo_linear_regression1(self, df_x, df_full=None, x=(), y=(), suffix='predict_'):

        df_x = df_x.loc[:, (x+y)].dropna()

        df_res = df_full.loc[:, x]
        df_res = df_res.dropna()

        model_outputs = {}

        for i in range(len(x)):
            x_train = np.array(df_x[[x[i]]])
            y_train = np.array(df_x[y[i]]).reshape(-1, 1)
            regr = LinearRegression()
            regr.fit(x_train, y_train)

            coef = float(regr.coef_)
            inter = float(regr.intercept_)
            R_square = float(regr.score(x_train, y_train))
            p_value = float(regr.p)

            regr_dict = {'coefficient': coef, 'intercept': inter, 'R_square': R_square, 'p-value': p_value}


            model_outputs[(x[i] + '-' + y[i])] = regr_dict

            if p_value < 0.05:
                x_full = np.array(df_res[[x[i]]])
                df_res[suffix + y[i]] = regr.predict(x_full)

        return df_res, model_outputs