from src.db.db import Session
from src.models.transaction import Transaction
from src.models.predict_view import PredictView
from src.services.ml import MLService
from sqlalchemy import select, update
import pandas as pd
import numpy as np
from typing import List, Tuple


class FraudService:

    def __init__(self):
        self.mlservice = MLService()

    @staticmethod
    def find_age_factor(age: int) -> float:
        if age > 60:
            return 0.3
        return 0.0

    @staticmethod
    def find_amount_factor(amount: float) -> float:
        if amount >= 100000:
            return 0.4
        return 0.0

    @staticmethod
    def find_time_factor_dif(time: int) -> float:
        if time >= 6:
            return 0.0
        return 0.9 - time * 0.05

    @staticmethod
    def find_hour_factor(hour: int) -> float:
        if hour >= 8:
            return 0.00
        return 0.4 - abs(3 - hour) * 0.05

    @staticmethod
    def pandas_query(session: Session) -> pd.DataFrame:
        conn = session.connection()
        query = select(PredictView)

        return pd.read_sql_query(query, conn)

    @staticmethod
    def get_time_difference(df: pd.DataFrame) -> pd.Series:
        df['prev_date'] = df.groupby('card')['date'].shift()
        df['time_difference_seconds'] = (df['date'] - df['prev_date']).dt.total_seconds()
        df['time_difference_seconds'] = df['time_difference_seconds'].replace(
            np.nan,
            np.mean(df['time_difference_seconds'])
        )
        return df['time_difference_seconds']

    @staticmethod
    def get_city_factor(df: pd.DataFrame, weight: float = 0.6) -> pd.Series:
        df['prev_city'] = df.groupby('card')['city'].shift()
        df['prev_city'] = df['prev_city'].replace(np.nan, -1)
        df['factor_city'] = 0.00
        df.loc[(df['prev_city'] != df['city']) & (df['prev_city'] != -1), 'factor_city'] = weight
        return df['factor_city']

    async def get_ml_factor(self, df: pd.DataFrame, model='suod', transformer='minmax', weight=0.4) -> np.ndarray:
        return await self.mlservice.find_factor(df, model, transformer, weight)

    def prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by=['card', 'date'], inplace=True)
        df['time_difference_seconds'] = self.get_time_difference(df)
        df = df[['id_transaction', 'date', 'card', 'date_of_birth', 'operation_type', 'amount', 'operation_result',
                 'terminal_type', 'city', 'time_difference_seconds', 'fraud_probability']]
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
        df['age'] = (df['date'].dt.year - df['date_of_birth'].dt.year).astype(int)
        df = df.drop('date_of_birth', axis=1)
        df['hour'] = df['date'].dt.hour
        df = df.drop('date', axis=1)
        return df

    async def find_factors(self, df: pd.DataFrame, null: bool = False) -> List[Tuple[int, float]]:
        df = self.prepare_df(df)
        df['factor_time_dif'] = df['time_difference_seconds'].apply(self.find_time_factor_dif)
        df['factor_hour'] = df['hour'].apply(self.find_hour_factor)
        df['factor_city'] = self.get_city_factor(df)
        df['factor_amount'] = df['amount'].apply(self.find_amount_factor)
        df['factor_age'] = df['age'].apply(self.find_age_factor)
        df['factor_ML'] = await self.get_ml_factor(df)
        if null:
            df = df.loc[df['fraud_probability'].isnull()]
        df_factors = df[['id_transaction', 'factor_age', 'factor_amount', 'factor_city', 'factor_hour',
                         'factor_time_dif', 'factor_ML']]
        result = []
        for index, row in df_factors.iterrows():
            factors = sorted(list(row[1:]), reverse=True)
            now_factor = 0.0
            for factor in factors:
                now_factor += (1.0 - now_factor) * factor
            result.append((row[0], now_factor))
        return result

    async def predict(self, null: bool = False) -> None:
        async with Session() as session:
            df = await session.run_sync(self.pandas_query)
            result = await self.find_factors(df, null)
            i = 0
            for index, probability in result:
                if i % 100 == 0:
                    await session.commit()
                q = (update(Transaction)
                     .where(Transaction.transaction_id == index)
                     .values(transaction_fraud_probability=probability))
                await session.execute(q)
                i += 1
            await session.commit()
