import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.core.config import settings
from app.parsers.main_parser import main_by_year

bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarsSearch(StatesGroup):
    waiting_for_mark = State()
    waiting_for_model = State()
    waiting_for_year = State()


# Кнопки
CANCEL_BUTTON = KeyboardButton(text="Отмена")
BACK_BUTTON = KeyboardButton(text="Назад")
cancel_kb = ReplyKeyboardMarkup(keyboard=[
    [CANCEL_BUTTON],
    [BACK_BUTTON]],
    resize_keyboard=True
    )

@dp.message(lambda message: message.text == "Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Поиск отменён. Напиши /start, чтобы начать заново.")

@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🚗 Начнём поиск автомобиля.\nВведите марку:",
        reply_markup=cancel_kb
    )
    await state.set_state(CarsSearch.waiting_for_mark)

@dp.message(lambda message: message.text == "Назад")
async def back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == CarsSearch.waiting_for_model.state:
        await state.set_state(CarsSearch.waiting_for_mark)
        await message.answer("Введите марку:")
    elif current_state == CarsSearch.waiting_for_year.state:
        await state.set_state(CarsSearch.waiting_for_model)
        await message.answer("Введите модель:")
    else:
        await message.answer("🔙 Нельзя вернуться назад")


# Обработчик марки, модели, года

@dp.message(CarsSearch.waiting_for_mark)
async def process_mark(message: types.Message, state: FSMContext):
    mark = message.text.strip()
    await state.update_data(mark=mark)
    await message.answer("Теперь введите модель:")
    await state.set_state(CarsSearch.waiting_for_model)

@dp.message(CarsSearch.waiting_for_model)
async def process_model(message: types.Message, state: FSMContext):
    model = message.text.strip()
    await state.update_data(model=model)
    await message.answer("Теперь введите год:")
    await state.set_state(CarsSearch.waiting_for_year)

@dp.message(CarsSearch.waiting_for_year)
async def process_year(message: types.Message, state: FSMContext):
    year = message.text.strip()
    if not year.isdigit():
        await message.answer("❌ Год должен быть числом. Попробуйте снова:")
        return

    data = await state.get_data()
    mark = data.get('mark')
    model = data.get('model')
    year = int(year)

    await message.answer(f"🔍 Ищу {mark} {model} {year} год...")

    try:
        cars = await main_by_year(mark, model, year)
    except Exception:
        logger.exception(f"Ошибка парсинга для {mark} {model} {year}")
        await message.answer(
            "⚠️ Не получилось получить данные с auto.ru. "
            "Возможно, сайт временно недоступен или изменил структуру страницы. "
            "Попробуйте ещё раз чуть позже."
        )
        await state.clear()
        return
    if not cars:
        await message.answer("❌ Ничего не найдено")
        await state.clear()
        return

    for car in cars[:3]:
        text = f"🚗 {car['title']}\n💰 {car['price']} ₽\n📅 {car['year']} г.\n🔗 {car['url']}"
        await message.answer(text)

    if len(cars) > 3:
        await message.answer(f"✅ Найдено {len(cars)} объявлений.\nПоказаны первые 3.")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())