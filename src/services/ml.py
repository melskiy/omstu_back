import pickle
from pyod.models.suod import SUOD
from pyod.models.lof import LOF
from pyod.models.iforest import IForest
from pyod.models.copod import COPOD
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from pathlib import Path
import pandas as pd
import numpy as np


class MLService:
    @staticmethod
    async def create_model_suod():
        detector_list = [LOF(n_neighbors=15), LOF(n_neighbors=20),
                         LOF(n_neighbors=25), LOF(n_neighbors=35),
                         COPOD(), IForest(n_estimators=100),
                         IForest(n_estimators=200)]
        suod = SUOD(base_estimators=detector_list, combination='average',
                    verbose=False)
        return suod

    @staticmethod
    async def create_transformer_minmax():
        column_transformer = ColumnTransformer(remainder='passthrough',
                                               transformers=[
                                                   ('minmax', MinMaxScaler(), ['amount'])
                                               ])
        return column_transformer

    async def get_model_info(self, model):
        model_map = {
            'suod': {'file_name': 'SUOD.pkl',
                     'create_function': self.create_model_suod}
        }
        return model_map[model]

    async def get_transformer_info(self, transformer):
        transformer_map = {
            'minmax': {'file_name': 'minmax.pkl',
                       'create_function': self.create_transformer_minmax}
        }
        return transformer_map[transformer]

    @staticmethod
    async def transform_df(df: pd.DataFrame, transformer_info: dict) -> np.ndarray:
        df_ml = df[['age', 'amount', 'time_difference_seconds',
                    'operation_type', 'operation_result', 'terminal_type']]
        df_ml = pd.get_dummies(df_ml, columns=['operation_type', 'operation_result', 'terminal_type'])
        transformer_path = Path(f"ML/transformer/{transformer_info['file_name']}")
        transformer_path.parent.mkdir(parents=True, exist_ok=True)
        if transformer_path.is_file():
            with open(transformer_path, 'rb') as file:
                transformer = pickle.load(file)
                return transformer.transform(df_ml)
        with open(transformer_path, 'wb') as file:
            transformer = await transformer_info['create_function']()
            X = transformer.fit_transform(df_ml)
            pickle.dump(transformer, file)
            return X

    @staticmethod
    async def predict_model(X: np.ndarray, model_info: dict, weight: float) -> np.ndarray:
        model_path = Path(f"ML/model/{model_info['file_name']}")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        if model_path.is_file():
            with open(model_path, 'rb') as file:
                model = pickle.load(file)
                Y = model.predict(X)
                return Y * weight
        with open(model_path, 'wb') as file:
            model = await model_info['create_function']()
            Y = model.fit_predict(X)
            pickle.dump(model, file)
            return Y * weight

    async def find_factor(self, df: pd.DataFrame, model='suod', transformer='minmax', weight=0.4) -> np.ndarray:
        model_info = await self.get_model_info(model)
        transformer_info = await self.get_transformer_info(transformer)
        X = await self.transform_df(df, transformer_info)
        return await self.predict_model(X, model_info, weight)
