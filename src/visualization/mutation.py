import numpy as np
from numpy import trapz
from scipy.integrate import simps
from sklearn.metrics import mean_squared_error


class Mutation:
    def __init__(self, name, xs, ys, color, short_name, family, target_score, y_pred, method: str = "trapz"):
        self.name = name
        self.short_name = short_name
        self.family = family
        self.color = color
        self.target_score = target_score
        self.method_name = method
        self.xs = xs
        self.ys = ys
        # Convert pandas df into list of lists and take the 1st one
        y_pred = y_pred.values.tolist()[0]
        self.mse = self.compute_mse([target_score for i in range(0, len(y_pred))], y_pred)

    @staticmethod
    def compute_mse(y_true: [float], y_pred: [float], debug: bool = False):
        assert len(y_true) == len(y_pred)
        mse = mean_squared_error(np.asarray(y_true), np.asarray(y_pred))

        if debug:
            print(f'Computed MSE: {mse}')
        return mse

    @staticmethod
    def compute_auc(xs: [float], ys: [float], method: str = "trapz", debug: bool = False):
        # The y values.  A numpy array is used here,
        ys = np.asarray(ys, dtype=np.float32)
        auc = -1

        if method == "trapz":
            # Compute the area using the composite trapezoidal rule.
            auc = trapz(ys, xs)
        elif method == "simp":
            # Compute the area using the composite Simpson's rule.
            auc = simps(ys, xs)

        if debug:
            print(f'Computed AUC using {method}: {auc}')
        return auc

    def get_label(self, use_family: bool = False, use_short: bool = False):
        if use_family:
            return f'{self.family} - MSE: {str(round(self.mse, 2))}'
        if use_short:
            return f'{self.short_name} - MSE: {str(round(self.mse, 2))}'
        return f'{self.name} - MSE: {str(round(self.mse, 2))}'


