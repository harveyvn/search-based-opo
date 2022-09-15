import pandas as pd
from itertools import combinations
from scipy.stats import ttest_ind
from src.libraries.libs import VD_A


class Report:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def are_they_different(self):
        data = self.df.to_dict("list")
        p_value = 0.05
        print(f'p-value is {p_value}')
        for list1, list2 in combinations(data.keys(), 2):
            t, p = ttest_ind(data[list1], data[list2])
            result = (p, "same") if p > p_value else (p, "different")
            print(list1, list2, result)

    def which_is_better(self):
        data = self.df.to_dict("list")

        matrix_dict = {}
        for l1, l2 in combinations(data.keys(), 2):
            result = VD_A(data[l1], data[l2])
            matrix_dict.update({(l1, l2): result[0]})
            matrix_dict.update({(l2, l1): 1 - result[0]})

        matrix_dict.update({("S.Rand", "S.Rand"): 0.5})
        matrix_dict.update({("S.OpO", "S.OpO"): 0.5})
        matrix_dict.update({("M.Rand", "M.Rand"): 0.5})
        matrix_dict.update({("M.OpO", "M.OpO"): 0.5})
