import json
import numpy as np
import pandas as pd
from src.models.ac3rp import CrashScenario
from src.models import SimulationFactory, Simulation, SimulationScore


class Preprocessing:
    def __init__(self, file_path):
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
