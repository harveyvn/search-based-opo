import json
import numpy as np
import pandas as pd
from numpy import trapz
from src.models.ac3rp import CrashScenario
from src.models import SimulationFactory, Simulation, SimulationScore


class Preprocessing:
    def __init__(self, file_path):
        self.auc_df = None
        self.mean_matrix_dict = None
        self.df_rand_m1, self.df_opo_m1 = pd.DataFrame(), pd.DataFrame()
        self.df_rand_m2, self.df_opo_m2 = pd.DataFrame(), pd.DataFrame()
        self.df_rand_opo_m1, self.df_rand_opo_m2 = pd.DataFrame(), pd.DataFrame()
        with open(file_path) as file:
            scenario = json.load(file)
        crash_scenario = CrashScenario.from_json(scenario)
        sim_factory = SimulationFactory(crash_scenario)
        simulation = Simulation(sim_factory=sim_factory)
        self.target = SimulationScore(simulation).get_expected_score()
        self.case = crash_scenario.name

    @staticmethod
    def process_individual(path, col_name):
        df = pd.read_csv(path, usecols=["score"])
        df = df.rename({"score": col_name}, axis=1)
        df = df.append([[] for _ in range(31 - len(df.index))], ignore_index=True)
        latest_score = 0
        for val in df[col_name]:
            if not np.isnan(val):
                latest_score = val

        df[col_name].fillna(latest_score, inplace=True)
        df[col_name] = df.apply(lambda r: r[col_name] if r[col_name] >= 0 else r[col_name] / 1000, axis=1)
        return df

    def preprocess_df(self, algorithm, mutator):
        df = pd.DataFrame()
        dfs = []
        for i in np.arange(start=1, stop=11, step=1):
            df_tmp = self.process_individual(f'output/{self.case}/{mutator}_{algorithm}_{i}.csv', f'repetition_{i}')
            dfs.append(df_tmp)
        df = pd.concat(dfs, axis=1)
        df[algorithm] = df.mean(numeric_only=True, axis=1)
        df["std"] = df.std(numeric_only=True, axis=1)
        df["i"] = np.arange(start=0, stop=31, step=1)
        return df

    def generate_dfs(self):
        self.df_rand_m1 = self.preprocess_df("Random", "Single")
        self.df_opo_m1 = self.preprocess_df("OpO", "Single")
        self.df_rand_m2 = self.preprocess_df("Random", "Multi")
        self.df_opo_m2 = self.preprocess_df("OpO", "Multi")

        self.df_rand_opo_m1 = pd.DataFrame()
        self.df_rand_opo_m1["i"] = self.df_rand_m1["i"]
        self.df_rand_opo_m1["Random"] = self.df_rand_m1["Random"]
        self.df_rand_opo_m1["OpO"] = self.df_opo_m1["OpO"]

        self.df_rand_opo_m2 = pd.DataFrame()
        self.df_rand_opo_m2["i"] = self.df_rand_m2["i"]
        self.df_rand_opo_m2["Random"] = self.df_rand_m2["Random"]
        self.df_rand_opo_m2["OpO"] = self.df_opo_m2["OpO"]
        return self.df_rand_m1, self.df_opo_m1, self.df_rand_m2, self.df_opo_m2, self.df_rand_opo_m1, self.df_rand_opo_m2

    def compute_auc(self):
        df_rand_m1, df_opo_m1, df_rand_m2, df_opo_m2, df_rand_opo_m1, df_rand_opo_m2 = self.generate_dfs()
        auc_df = pd.DataFrame(columns=["auc_rand_m1", "auc_opo_m1", "auc_rand_m2", "auc_opo_m2"])

        for i in range(1, 11):
            rand_m1 = df_rand_m1[f'repetition_{i}'].tolist()
            opo_m1 = df_opo_m1[f'repetition_{i}'].tolist()
            rand_m2 = df_rand_m2[f'repetition_{i}'].tolist()
            opo_m2 = df_opo_m2[f'repetition_{i}'].tolist()
            # Get min value across the df
            min_val = abs(min(rand_m1 + opo_m1 + rand_m2 + opo_m2))
            # Level up
            rand_m1 = [x + min_val for x in rand_m1]
            opo_m1 = [x + min_val for x in opo_m1]
            rand_m2 = [x + min_val for x in rand_m2]
            opo_m2 = [x + min_val for x in opo_m2]
            # Calculate AUC for each repetition - append to the last row of auc_df
            new_auc_row = {
                "auc_rand_m1": trapz(rand_m1),
                "auc_opo_m1": trapz(opo_m1),
                "auc_rand_m2": trapz(rand_m2),
                "auc_opo_m2": trapz(opo_m2)
            }
            auc_df = pd.concat([auc_df, pd.DataFrame([new_auc_row])])

        # Combine all auc and get mean
        dfs = list()
        dfs.append(auc_df[["auc_rand_m1", "auc_opo_m1", "auc_rand_m2", "auc_opo_m2"]].mean(axis=0))
        mean_matrix = pd.concat(dfs, axis=1).T

        # auc_df = pd.concat([auc_df, mean_matrix])
        auc_df = auc_df.reset_index(drop=True)
        mean_matrix_dict = mean_matrix.to_dict(orient="records")[0]
        mean_matrix_dict = dict(sorted(mean_matrix_dict.items(), key=lambda item: item[1]))
        self.mean_matrix_dict = mean_matrix_dict
        self.auc_df = auc_df
