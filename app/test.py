import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        # Запускаем браузер
        browser = await p.chromium.launch(headless=False)  # headless=False чтобы увидеть браузер
        page = await browser.new_page()

        # Идем на авто.ру
        await page.goto("https://auto.ru")

        # Делаем скриншот (просто для проверки)
        await page.screenshot(path="example.png")
        print("Скриншот сохранен!")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())