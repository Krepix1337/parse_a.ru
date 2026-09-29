from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from app.parsers.captcha import wait_if_captcha

REGION = "yaroslavl"
CARD_SELECTOR = ".ListingCars__universalSnippetWrapper"


def build_search_url(mark_code: str, model_code: str, gen_code: str) -> str:
    # Фильтр "марка + модель + поколение" auto.ru хранит прямо в адресе страницы,
    # поэтому вместо кликов по дропдаунам можно сразу открыть нужный URL
    return f"https://auto.ru/{REGION}/cars/{mark_code}/{model_code}/{gen_code}/all/"


async def search_cars(mark_code: str, model_code: str, gen_code: str):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    url = build_search_url(mark_code, model_code, gen_code)
    print(f"Открываю {url}")
    await page.goto(url, wait_until="domcontentloaded")
    await wait_if_captcha(page)

    # Ждём, пока появится хотя бы одна карточка. Если объявлений нет —
    # карточки не появятся никогда, поэтому ловим таймаут и отдаём пустой список
    try:
        await page.wait_for_selector(CARD_SELECTOR, timeout=15000)
    except PlaywrightTimeoutError:
        print("Карточки не появились — объявлений нет (или страница не загрузилась)")
        return playwright, page, browser, []

    cards = await page.locator(CARD_SELECTOR).all()
    return playwright, page, browser, cards
