import asyncio
from app.parsers.fetcher import search_cars as fetch_cars
from app.parsers.card_parser import parse_card
from app.database.crud import save_car, find_generation
from app.database.database import async_session_maker
from app.models.generation import Generation


async def main(gen: Generation):
    """Парсит объявления одного поколения. Коды — для URL, названия — для записи в БД."""
    playwright, page, browser, cards = await fetch_cars(gen.mark_code, gen.model_code, gen.gen_code)

    try:
        tasks = [parse_card(card, gen.mark, gen.model, gen.generation_name) for card in cards]
        cars_data = await asyncio.gather(*tasks)

        async with async_session_maker() as session:
            for car in cars_data:
                await save_car(session, car)

        return cars_data
    finally:
        await browser.close()
        await playwright.stop()


async def main_by_year(mark: str, model: str, year: int):
    """Поиск по году — сначала находит поколение в БД, потом парсит"""

    # 1. Ищем поколение в БД
    async with async_session_maker() as session:
        generation = await find_generation(session, mark, model, year)

    if not generation:
        print(f"❌ Не найдено поколение для {mark} {model} {year}")
        return []

    print(f"✅ Найдено поколение: {generation.generation_name} ({generation.gen_code})")

    # 2. Парсим объявления этого поколения
    return await main(generation)


if __name__ == '__main__':
    result = asyncio.run(main_by_year("audi", "a4", 2013))
    print(f"\n✅ Готово! Найдено {len(result)} машин")
    for car in result[:3]:
        print(f"  - {car['title']} | {car['price']} ₽ | {car['year']} г.")
