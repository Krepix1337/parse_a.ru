import re
import asyncio
from urllib.parse import urlparse

from playwright.async_api import async_playwright
from sqlalchemy import select

from app.database.crud import save_generation
from app.database.database import async_session_maker
from app.models.generation import Generation
from app.parsers.captcha import wait_if_captcha
from app.parsers.cleaners import clean_model_name

MARK_RE = re.compile(r"^/catalog/cars/([a-z0-9_]+)/?$")

MODEL_RE = re.compile(r"^/catalog/cars/([a-z0-9_]+)/([a-z0-9_]+)/?$")

GEN_RE = re.compile(r"^/catalog/cars/([a-z0-9_]+)/([a-z0-9_]+)/(\d+)(?:/.*)?$")

types = ["Седан", "Лимузин", "Пикап", "Хэтчбек", "Универсал", "Лифтбек", "Минивэн", "Купе", "Кабриолет",
                 "Родстер", "Тарга", "Внедорожник", "Компактвэн", "Фургон", "Микровэн", "Фастбек", "Микроавтобус", "Ландо"]

EXCLUDED_MODEL_NAMES = {"Двигатели", "Все", "Популярные"}

async def parse_marks(page) -> dict[str, str]:
    await page.goto("https://auto.ru/catalog/cars/all/", wait_until="domcontentloaded")
    await page.wait_for_timeout(1500)

    await wait_if_captcha(page)

    marks = {}
    links = await page.locator("a[href*='/catalog/cars/']").all()
    for a in links:
        href = await a.get_attribute("href") or ""
        path = urlparse(href).path
        m = MARK_RE.match(path)
        if not m:
            continue
        code = m.group(1)
        name = (await a.text_content() or code).strip()
        marks[code] = name
    return marks

async def parse_models(page, mark_code: str) -> dict[str, str]:
    url = f"https://auto.ru/catalog/cars/{mark_code}/all/"
    try:
        await page.goto(url, wait_until="domcontentloaded")
    except Exception as e:
        print(f"    ⚠️ Не удалось открыть {url}: {e}")
        return []
    await page.wait_for_timeout(1500)

    await wait_if_captcha(page)

    models = {}
    seen_models = set()
    links = await page.locator("a[href*='/catalog/cars/']").all()
    for a in links:
        href = await a.get_attribute("href") or ""
        path = urlparse(href).path
        m = MODEL_RE.match(path)
        if not m or m.group(1) != mark_code:
            continue
        model_code = m.group(2)
        if model_code in seen_models:
            continue
        seen_models.add(model_code)
        if model_code == 'all':
            continue

        raw_name = (await a.text_content() or model_code).strip()
        name = clean_model_name(raw_name)

        if name in EXCLUDED_MODEL_NAMES or name.startswith("Фотографии"):
            continue

        models[model_code] = name
    return models

YEARS_RE = re.compile(r"(\d{4})\s*[—\-–]\s*(\d{4}|н\.?\s*в\.?)")
SINCE_YEAR_RE = re.compile(r"[cс]\s*(\d{4})\s*года")

async def parse_generations(page, mark_code: str, model_code: str) -> list[dict]:
    url = f"https://auto.ru/catalog/cars/{mark_code}/{model_code}/all/"
    try:
        await page.goto(url, wait_until="domcontentloaded")
    except Exception as e:
        print(f"    ⚠️ Не удалось открыть {url}: {e}")
        return []
    await page.wait_for_timeout(1500)

    await wait_if_captcha(page)

    generations = []
    seen_codes = set()

    links = await page.locator("a[href*='/catalog/cars/']").all()
    for a in links:
        href = await a.get_attribute("href") or ""
        path = urlparse(href).path
        m = GEN_RE.match(path)
        if not m or m.group(1) != mark_code or m.group(2) != model_code:
            continue

        gen_code = m.group(3)
        if gen_code in seen_codes:
            continue
        seen_codes.add(gen_code)

        parent_text = await a.locator("xpath=..").text_content() or ""
        years_match = YEARS_RE.search(parent_text)
        years_since_match = SINCE_YEAR_RE.search(parent_text)

        if years_match:
            year_start = int(years_match.group(1))
            year_end_raw = years_match.group(2)
            year_end = int(year_end_raw) if year_end_raw.isdigit() else 2100
        elif years_since_match:
            year_start = int(years_since_match.group(1))
            year_end = 2100
        else:
            year_start, year_end = 0, 0

        pattern = "|".join(map(re.escape, types))

        gen_name_raw = parent_text
        if years_match:
            gen_name_raw = parent_text[years_match.end():]
        elif years_since_match:
            gen_name_raw = parent_text[years_since_match.end():]

        match = re.search(pattern, gen_name_raw)
        generation_name = gen_name_raw[:match.start()].strip() if match else gen_name_raw.strip()

        print(f"parent_text: {parent_text!r}")
        print(f"gen_name_raw: {gen_name_raw!r}")
        print(f"generation_name: {generation_name!r}")
        print("---")

        generations.append({
            "gen_code": gen_code,
            "generation_name": generation_name,
            "year_start": year_start,
            "year_end": year_end,
        })

    return generations

async def is_mark_already_parsed(session, mark_code: str) -> bool:
    # Сравниваем с mark_code, а не с mark: в mark лежит название ("Audi"), а тут код ("audi").
    # gen_code IS NOT NULL — марки, спарсенные до появления кодов, считаем непройденными,
    # чтобы save_generation дописал им коды.
    result = await session.execute(
        select(Generation).where(
            Generation.mark_code == mark_code,
            Generation.gen_code.is_not(None),
        ).limit(1)
    )
    return result.scalar_one_or_none() is not None

async def parse_catalog(limit_marks: int | None = None):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    try:
        marks = await parse_marks(page)
        mark_items = list(marks.items())
        if limit_marks:
            mark_items = mark_items[:limit_marks]

        print(f"Всего марок найдено: {len(mark_items)}")

        for mark_code, mark_name in mark_items:
            async with async_session_maker() as session:
                already_done = await is_mark_already_parsed(session, mark_code)
            if already_done:
                print(f"Марка {mark_name} уже есть в базе, пропускаю")
                continue

            print(f"\nОбрабатываю марку: {mark_name} ({mark_code})")
            models = await parse_models(page, mark_code)

            for model_code, model_name in models.items():
                print(f"  Модель: {model_name}")
                gens = await parse_generations(page, mark_code, model_code)

                async with async_session_maker() as session:
                    for gen in gens:
                        await save_generation(session, {
                            "mark": mark_name,
                            "model": model_name,
                            "generation_name": gen["generation_name"],
                            "year_start": gen["year_start"],
                            "year_end": gen["year_end"],
                            "mark_code": mark_code,
                            "model_code": model_code,
                            "gen_code": gen["gen_code"],
                        })
    finally:
        await browser.close()
        await playwright.stop()


async def debug_main():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    try:
        gens = await parse_models(page, mark_code="audi")
        print(f"\nИтого извлечено поколений: {len(gens)}")
        for g in gens:
            print(g)
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(parse_catalog())
    # asyncio.run(debug_main())
