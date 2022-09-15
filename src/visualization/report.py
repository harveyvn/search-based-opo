import pandas as pd
from itertools import combinations
from scipy.stats import ttest_ind


class Report:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def are_they_different(self):
        data = self.df.to_dict("list")
        for list1, list2 in combinations(data.keys(), 2):
            t, p = ttest_ind(data[list1], data[list2])
            print(list1, list2, p)