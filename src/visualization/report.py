import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from scipy.stats import ttest_ind
from src.libraries.libs import VD_A


class Report:
    def __init__(self, case_id, df: pd.DataFrame):
        self.df = df
        self.case_id = case_id

    def are_they_different(self):
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        data = self.df.to_dict("list")
        boxplot = self.df.boxplot(column=['S.Rand', 'S.OpO', 'M.Rand', 'M.OpO'], grid=False)
        boxplot.plot()
        for i, d in enumerate(self.df):
            y = data[d]
            x = np.random.normal(i + 1, 0.04, len(y))
            plt.plot(x, y, 'r.', alpha=0.4)
        plt.show()
        fig.savefig(f'output/{self.case_id}/Plot - DataPoints.png', bbox_inches="tight")
        for k, v in data.items():
            print(k, v)
        p_value = 0.05
        print(f'p-value is {p_value}')
        for list1, list2 in combinations(data.keys(), 2):
            t, p = ttest_ind(data[list1], data[list2])
            result = (p, "same") if p > p_value else (p, "different")
            print(list1, list2, result)

    def which_is_better(self):
        data = self.df.to_dict("list")

        mt = {}
        for l1, l2 in combinations(data.keys(), 2):
            result = VD_A(data[l1], data[l2])
            point = str(round(result[0], 2))
            m_point = str(round(1 - result[0], 2))
            mt.update({(l1, l2): point})
            mt.update({(l2, l1): m_point})

        mt.update({("S.Rand", "S.Rand"): 0.5})
        mt.update({("S.OpO", "S.OpO"): 0.5})
        mt.update({("M.Rand", "M.Rand"): 0.5})
        mt.update({("M.OpO", "M.OpO"): 0.5})

        # for k,v in mt.items():
        #     print(k, v)

        print(r'\begin{table}[h!]')
        print(r'  \begin{center}')
        print(r'    \caption{Case ' + f'{self.case_id}' + ': Quantitative comparison of Single Random (S.Rand), Single OpO (S.OpO), Multiple Random (M.Rand), and Multiple OpO (M.OpO)\\\\}')
        print(r'    \label{tab:table_a12_'+self.case_id+'}')
        print(r'    \begin{tabular}{l|c|c|c|c}')
        print(r'      \textbf{(p-value < 0.05)} & \textbf{S.Rand} & \textbf{S.OpO} & \textbf{M.Rand} & \textbf{M.OpO}\\')
        print(r'      \hline')
        print(r'      \textbf{S.Rand}' + '  & 0.5  & {}    & {}     & {}   \\\\'.format(mt[('S.OpO', 'S.Rand')],
                                                                                      mt[('M.Rand', 'S.Rand')],
                                                                                      mt['M.OpO', 'S.Rand']))
        print(r'      \textbf{S.OpO} ' + '  & {}    & 0.5  & {}     & {}   \\\\'.format(mt[('S.Rand', 'S.OpO')],
                                                                                      mt[('M.Rand', 'S.OpO')],
                                                                                      mt['M.OpO', 'S.OpO']))
        print(r'      \textbf{M.Rand}' + '  & {}    & {}    & 0.5   & {}   \\\\'.format(mt[('S.Rand', 'M.Rand')],
                                                                                      mt[('S.OpO', 'M.Rand')],
                                                                                      mt['M.OpO', 'M.Rand']))
        print(r'      \textbf{M.OpO} ' + '  & {}    & {}    & {}    & 0.5  \\\\'.format(mt[('S.Rand', 'M.OpO')],
                                                                                      mt[('S.OpO', 'M.OpO')],
                                                                                      mt['M.Rand', 'M.OpO']))
        print(r'    \end{tabular}')
        print(r'  \end{center}')
        print(r'\end{table}')
