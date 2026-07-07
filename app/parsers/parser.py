# import asyncio
#
# from playwright.async_api import async_playwright
# from app.database.crud import save_car
# from app.database.database import async_session_maker
#
# from app.parsers.cleaners import extract_subtitle, extract_specs, clean_price, parse_year_mileage
#
#
# async def main_parser():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#         await page.goto("https://auto.ru/yaroslavl/cars/all/")
#
#         # Марка
#         await page.wait_for_selector('[placeholder="Марка"]', timeout=10000)
#         await page.get_by_placeholder("Марка").click()
#         await page.wait_for_selector('[role="menuitem"]', timeout=10000)
#         await page.get_by_role("menuitem", name="Audi").first.click()
#
#         # Модель
#         await page.wait_for_selector('[placeholder="Модель"]', timeout=5000)
#         await page.get_by_placeholder("Модель").click()
#         await page.get_by_role("menuitem", name="A4").first.wait_for(state="visible", timeout=5000)
#         await page.get_by_role("menuitem", name="A4").first.click()
#
#         # Поколение
#         await page.get_by_placeholder("Поколение").click()
#         await page.get_by_role("checkbox", name="2011—2015").first.wait_for(state="visible", timeout=5000)
#         await page.get_by_role("checkbox", name="2011—2015").first.click()
#
#         # Показать + ожидание загрузки
#         await page.get_by_role("button", name="Показать").first.wait_for(state="visible", timeout=5000)
#         old_price = await page.locator('[class*="ListingItemUniversal__price"]').first.text_content()
#         await page.get_by_role("button", name="Показать").first.click()
#
#         print("Жду загрузку страницы...")
#         await page.wait_for_function('''
#             oldPrice => {
#                 const priceEl = document.querySelector('[class*="ListingItemUniversal__price"]');
#                 return priceEl && priceEl.textContent !== oldPrice;
#             }
#         ''', arg=old_price)
#
#         # Парсинг
#
#         cards = await page.locator(".ListingCars__universalSnippetWrapper").all()
#
#         cars_data = []
#
#         for i, card in enumerate(cards):
#             print(f"\n--- Карточка {i + 1} ---\n")
#
#             # Заголовок
#             title_container = card.locator("[class*='ListingItemTitle']").first
#             link_element = title_container.locator('a[href*="/cars/used/sale/"]').first
#
#             if await link_element.count() > 0:
#                 title = await link_element.text_content()
#                 url = await link_element.get_attribute('href')
#             else:
#                 title = "нет"
#                 url = "нет"
#             print(f"Заголовок: {title}. URL: {url}")
#
#             # Комплектация
#             subtitle_element = card.locator("[class*='ListingItemUniversalSpecs__subtitle']").first
#             subtitle_text = await subtitle_element.text_content() if await subtitle_element.count() > 0 else "нет"
#             subtitle = extract_subtitle(subtitle_text)
#             print(f"Комплектация: {subtitle}")
#
#             # Характеристики
#             specs_element = card.locator("[class*='ListingItemUniversalSpecs__specs']").first
#             specs_text = await specs_element.text_content() if await specs_element.count() > 0 else "нет"
#             specs = extract_specs(specs_text)
#             print(f"Характеристики: {specs}")
#
#             # Год и пробег
#             condition_element = card.locator("[class*='ListingItemUniversalCondition']").first
#             condition_text = await condition_element.text_content() if await condition_element.count() > 0 else "нет"
#             print(f"RAW condition_text: '{condition_text}'")
#             year_int, mileage_int = parse_year_mileage(condition_text)
#             print(f"RESULT: year={year_int}, mileage={mileage_int}")
#             print(f"Год и пробег: {year_int, mileage_int}")
#
#             # Цена
#             price_element = card.locator("[class*='ListingItemUniversal__price']").first
#             price_text = await price_element.text_content() if await price_element.count() > 0 else "нет"
#             if price_text is None:
#                 price_text = "нет"
#             price = clean_price(price_text)
#             print(f"Цена: {price}")
#
#             car_info = {
#                 "title": title,
#                 "url": url,
#                 "subtitle": subtitle,
#                 "specs": ", ".join(specs) if isinstance(specs, list) else specs,
#                 "year": year_int,
#                 "mileage": mileage_int,
#                 "price": price,
#             }
#             cars_data.append(car_info)
#
#         async with async_session_maker() as session:
#             for car in cars_data:
#                 await save_car(session, car)
#
#         await browser.close()
#
#
#
# if __name__ == "__main__":
#     asyncio.run(main_parser())
