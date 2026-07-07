import asyncio
from app.parsers.fetcher import search_cars as fetch_cars
from app.parsers.card_parser import parse_card
from app.database.crud import save_car, find_generation
from app.database.database import async_session_maker

async def main(mark: str, model: str, generation: str):
    playwright, page, browser, cards = await fetch_cars(mark, model, generation)

    try:
        tasks = [parse_card(card, mark, model, generation) for card in cards]
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

    print(f"✅ Найдено поколение: {generation}")

    # 2. Запускаем существующий парсер с найденным поколением
    return await main(mark, model, generation)


if __name__ == '__main__':
    result = asyncio.run(main_by_year("acura", "mdx", 2014))
    print(f"\n✅ Готово! Найдено {len(result)} машин")
    for car in result[:3]:
        print(f"  - {car['title']} | {car['price']} ₽ | {car['year']} г.")
