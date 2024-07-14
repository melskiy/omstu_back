from fastapi import FastAPI

from src.api.base_router import router

from fastapi.middleware.cors import CORSMiddleware

origins = [
   '*'
]
tags_dict = [
    {
        'name': 'data',
        'description': 'Работа с данными',
    },
    {
        'name': 'fraud',
        'description': 'Работа с фродами'
    }
]

app = FastAPI(
    title="OmSTU_Practice",
    description="Практика",
    version="0.1.0",
    openapi_tags=tags_dict,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
