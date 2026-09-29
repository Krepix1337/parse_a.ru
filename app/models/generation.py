from sqlalchemy import Column, String, Integer
from app.database.database import Base

class Generation(Base):
    __tablename__ = "Generation"

    id = Column(Integer, primary_key=True, index=True)
    mark = Column(String, nullable=True)
    model = Column(String, nullable=True)
    generation_name = Column(String, nullable=True)
    year_start = Column(Integer, nullable=True)
    year_end = Column(Integer, nullable=True)

    # Коды из URL auto.ru: /cars/{mark_code}/{model_code}/{gen_code}/all/
    # Нужны, чтобы открывать поиск сразу по ссылке, без кликов по дропдаунам
    mark_code = Column(String, nullable=True)
    model_code = Column(String, nullable=True)
    gen_code = Column(String, nullable=True)