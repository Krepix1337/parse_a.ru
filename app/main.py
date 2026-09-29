import asyncio
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.parsers.main_parser import main_by_year

from app.core.config import settings
import logging

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auto.ru Parser")

class SearchRequest(BaseModel):
    mark: str
    model: str
    year: int

class CarResponse(BaseModel):
    mark: str
    model: str
    generation: str
    title: str
    url: str
    price: int
    year: int
    mileage: int
    specs: str
    subtitle: str

@app.get("/")
async def root():
    return {"message": "Auto.ru Parser", "debug": settings.MODE}

@app.post("/search", response_model=list[CarResponse])
async def search(request: SearchRequest):
    try:
        logger.info(f"Поиск: {request.mark} {request.model} {request.year}")
        cars = await main_by_year(request.mark, request.model, request.year)
        logger.info(f"Найдено {len(cars)} машин")
        return cars
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)