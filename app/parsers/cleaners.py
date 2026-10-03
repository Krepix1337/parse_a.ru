import re

def clean_price(price_text: str) -> int:
    if not price_text or price_text == "нет":
        return 0
    # Вариант с заменами
    # cleaned = price_text.replace('\xa0', ' ').replace('₽', '').replace(' ', '')
    # digits = re.sub(r'\D', '', cleaned)

    rubl_index = price_text.find("₽")
    if rubl_index != -1:
        price_part = price_text[:rubl_index+1]
    else:
        price_part = price_text

    digits = re.sub(r'\D', '', price_part)
    return int(digits) if digits else 0

def parse_year_mileage(condition_text:str) -> tuple[int, int]:
    if not condition_text or condition_text == "нет" or len(condition_text) < 4:
        return 0, 0

    year_str = condition_text[:4]
    mileage_str = condition_text[4:]
    mileage_clean = re.sub(r'\D', '', mileage_str)

    year = int(year_str) if year_str.isdigit() else 0
    mileage = int(mileage_clean) if mileage_clean else 0

    return year, mileage

def extract_subtitle(subtitle_text:str) -> str:
    if subtitle_text.startswith('Комплектация'):
        subtitle = subtitle_text.replace('Комплектация', '', 1)
    else:
        subtitle = subtitle_text
    text = subtitle.replace('•', ', ')
    return text.strip()

def extract_specs(specs_text: str) -> list:
    cleaned_specs = specs_text.replace('\xa0', ' ')
    return re.findall(r'[А-Я][^А-Я]*', cleaned_specs)

def clean_model_name(raw: str) -> str:
    match = re.search(r'\d+\s*в\s*продаже', raw)
    if match:
        return raw[:match.start()].strip()
    return raw.strip()