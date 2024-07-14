from fastapi import APIRouter, Depends, UploadFile, status
from src.services.data import DataService


router = APIRouter(
    prefix='/data',
    tags=['data'],
)


@router.post("/inputCSV", status_code=status.HTTP_200_OK, name="Ввод данных формата csv")
async def input_data(file: UploadFile, methods_service: DataService = Depends()):
    return await methods_service.insert(file.file)
