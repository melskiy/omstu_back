from fastapi import APIRouter, Depends, status
from src.services.fraud import FraudService

router = APIRouter(
    prefix='/fraud',
    tags=['fraud'],
)


@router.post("/predict", status_code=status.HTTP_200_OK, name="Предсказать метки транзакций")
async def input_data(null_flag: bool = True, predict_service: FraudService = Depends()):
    return await predict_service.predict(null_flag)
