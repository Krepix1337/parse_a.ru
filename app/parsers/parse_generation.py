import asyncio

from playwright.async_api import async_playwright
import re

from app.database.crud import save_generation
from app.database.database import async_session_maker


async def parse_generations():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto("https://auto.ru/cars/all/")

    # Список марок
    await page.wait_for_selector('[placeholder="Марка"]', timeout=10000)
    await page.get_by_placeholder("Марка").click()
    await page.wait_for_selector('text="212"', timeout=10000)
    mark_elements = await page.locator('[role="menuitem"]').all()

    marks = []
    start_collecting = False
    for mark in mark_elements:
        text = await mark.text_content()
        if text == "212":
            start_collecting = True
        if start_collecting and text not in ["Все", "Популярные", "Иномарки", "Отечественные"]:
            marks.append(text)

    print(f"Найдено марок: {len(marks)}")
    print(marks[:10])

    for mark in marks[:4]:
        print(f"\n{'=' * 50}")
        print(f"ОБРАБОТКА МАРКИ: {mark}")
        print(f"{'=' * 50}")

        await page.goto("https://auto.ru/cars/all/")
        await page.wait_for_selector('[placeholder="Марка"]', timeout=10000)
        await page.get_by_placeholder("Марка").click()
        await page.wait_for_selector('[role="menuitem"]', timeout=10000)
        await page.get_by_role("menuitem", name=mark).first.click()

        # Список моделей
        await page.wait_for_selector('[placeholder="Модель"]', timeout=10000)
        await page.get_by_placeholder("Модель").click()
        await page.wait_for_selector('[role="menuitem"]', timeout=10000)

        model_elements = await page.locator('[role="menuitem"]').all()

        models = []
        for el in model_elements:
            text = await el.text_content()
            if text not in ["Любая", "Популярные", "Все"]:
                models.append(text)

        unique_models = list(dict.fromkeys(models))
        print(f"Моделей у марки {mark}: {len(unique_models)}")
        print(f"Первые 10 моделей: {unique_models[:10]}")

        # Парсим поколения
        for i, model in enumerate(unique_models):
            print(f"\n--- Модель {i+1}: {model} ---")

            await page.get_by_role("menuitem", name=model).first.click()

            await page.get_by_placeholder("Поколение").click()
            await page.wait_for_selector('.Checkbox', timeout=30000)

            gen_elements = await page.locator('.Checkbox').all()

            for gen in gen_elements:
                year_element = gen.locator('.GenerationFilterPopupItem__years')
                if await year_element.count() > 0:
                    years_text = await year_element.text_content()
                    name_element = gen.locator('.GenerationFilterPopupItem__name')
                    gen_name = await name_element.text_content() if await name_element.count() > 0 else ""
                    print(f"   Поколение: {gen_name}")

                    years = re.findall(r"\d+", years_text)
                    if len(years) >= 2:
                        year_start = int(years[0])
                        year_end = int(years[1])
                        print(f"   Годы: {year_start}—{year_end}")

                        # Сохранение в БД
                        async with async_session_maker() as session:
                            await save_generation(session, {
                                "mark": mark,
                                "model": model,
                                "generation_name": gen_name,
                                "year_start": year_start,
                                "year_end": year_end,
                            })

            if i < len(unique_models) - 1:
                await page.get_by_placeholder("Модель").click()
                await page.get_by_role("menuitem", name="Любая").first.click()
                await page.wait_for_selector('[placeholder="Модель"]')
                await page.get_by_placeholder("Модель").click()
                await page.wait_for_selector('[role="menuitem"]', timeout=30000)



    await browser.close()


if __name__ == '__main__':
    asyncio.run(parse_generations())

