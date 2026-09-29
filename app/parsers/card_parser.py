from app.parsers.cleaners import extract_subtitle, extract_specs, parse_year_mileage, clean_price
from urllib.parse import urljoin

BASE_URL = "https://auto.ru"

async def parse_card(card, mark: str, model: str, generation: str):
    # Заголовок
    title_container = card.locator("[class*='ListingItemTitle']").first
    link_element = title_container.locator('a[href*="/cars/used/sale/"]').first

    if await link_element.count() > 0:
        title = await link_element.text_content()
        raw_href = await link_element.get_attribute('href')
        url = urljoin(BASE_URL, raw_href) if raw_href else "нет"
    else:
        title = "нет"
        url = "нет"
    print(f"Заголовок: {title}. URL: {url}")

    # Комплектация
    subtitle_element = card.locator("[class*='ListingItemUniversalSpecs__subtitle']").first
    subtitle_text = await subtitle_element.text_content() if await subtitle_element.count() > 0 else "нет"
    subtitle = extract_subtitle(subtitle_text)
    print(f"Комплектация: {subtitle}")

    # Характеристики
    specs_element = card.locator("[class*='ListingItemUniversalSpecs__specs']").first
    specs_text = await specs_element.text_content() if await specs_element.count() > 0 else "нет"
    specs = extract_specs(specs_text)
    print(f"Характеристики: {specs}")

    # Год и пробег
    condition_element = card.locator("[class*='ListingItemUniversalCondition']").first
    condition_text = await condition_element.text_content() if await condition_element.count() > 0 else "нет"
    print(f"RAW condition_text: '{condition_text}'")
    year_int, mileage_int = parse_year_mileage(condition_text)
    print(f"RESULT: year={year_int}, mileage={mileage_int}")
    print(f"Год и пробег: {year_int, mileage_int}")

    # Цена
    price_element = card.locator("[class*='ListingItemUniversal__price']").first
    price_text = await price_element.text_content() if await price_element.count() > 0 else "нет"
    if price_text is None:
        price_text = "нет"
    price = clean_price(price_text)
    print(f"Цена: {price}")

    return {
        "mark": mark,
        "model": model,
        "generation": generation,
        "title": title,
        "url": url,
        "subtitle": subtitle,
        "specs": ", ".join(specs) if isinstance(specs, list) else specs,
        "year": year_int,
        "mileage": mileage_int,
        "price": price,
    }