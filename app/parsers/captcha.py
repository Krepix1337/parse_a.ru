CAPTCHA_MARKERS = [
    "captcha",
    "подозрительная активность",
    "confirm you are human",
    "подтвердите, что запросы отправляли вы, а не робот",
]


async def wait_if_captcha(page):
    """Если auto.ru показал капчу — ждём, пока человек пройдёт её в окне браузера."""
    content = (await page.content()).lower()
    # Все маркеры в нижнем регистре, потому что и content приведён к нижнему регистру
    if any(marker in content for marker in CAPTCHA_MARKERS):
        print("\n⚠️  ОБНАРУЖЕНА КАПЧА! Пройдите её в открытом окне браузера.")
        input("   После того как капча пройдена и страница обычная — нажмите Enter здесь...")
