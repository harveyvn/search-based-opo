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
        for l1, l2 in combinations(data.keys(), 2):
            result = VD_A(data[l1], data[l2])
            print(l1, l2, result)