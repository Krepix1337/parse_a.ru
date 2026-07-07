from playwright.async_api import async_playwright


async def search_cars(mark: str, model: str, generation: str):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto("https://auto.ru/yaroslavl/cars/all/")
    # await page.wait_for_load_state("networkidle")
    # await page.evaluate("window.scrollTo(0, 100)")

    # Марка
    await page.wait_for_selector('[placeholder="Марка"]', timeout=30000)
    # await page.screenshot(path="error.png")
    await page.get_by_placeholder("Марка").click()
    # await page.wait_for_selector('[role="menuitem"]', timeout=30000)
    # await page.get_by_role("menuitem", name=mark).first.click()
    await page.get_by_role("textbox", name="Марка").fill(mark)
    await page.locator(f'.ListItem2-YfpWi:has-text("{mark}")').first.click()

    # Модель
    await page.wait_for_selector('[placeholder="Модель"]', timeout=30000)
    await page.get_by_placeholder("Модель").click()
    # await page.get_by_role("menuitem", name=model).first.wait_for(state="visible", timeout=30000)
    # await page.get_by_role("menuitem", name=model).first.click()
    await page.get_by_role("textbox", name="Модель").fill(model)
    await page.locator(f'.ListItem2-YfpWi:has-text("{model}")').first.click()

    # Поколение
    await page.get_by_placeholder("Поколение").click()
    # await page.get_by_role("checkbox", name=generation).first.wait_for(state="visible", timeout=30000)
    # await page.get_by_role("checkbox", name=generation).first.click()
    await page.locator(f'.Checkbox__text:has-text("{generation}")').first.click()

    # Показать + ожидание загрузки
    await page.get_by_role("button", name="Показать").first.wait_for(state="visible", timeout=30000)
    old_price = await page.locator('[class*="ListingItemUniversal__price"]').first.text_content()
    await page.get_by_role("button", name="Показать").first.click()

    print("Жду загрузку страницы...")
    await page.wait_for_function('''
        oldPrice => {
            const priceEl = document.querySelector('[class*="ListingItemUniversal__price"]');
            return priceEl && priceEl.textContent !== oldPrice;
        }
    ''', arg=old_price)
    # await page.wait_for_selector('.ListingCars__universalSnippetWrapper', timeout=30000)

    cards = await page.locator(".ListingCars__universalSnippetWrapper").all()

    return playwright, page, browser, cards
