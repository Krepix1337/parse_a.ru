from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.car import Car
from app.models.generation import Generation


async def save_car(session: AsyncSession, car_data: dict):
    result = await session.execute(
        select(Car).where(Car.url == car_data["url"])
    )
    existing_car = result.scalar_one_or_none()

    if existing_car:
        changes = []

        if existing_car.price != car_data["price"]:
            changes.append(f"цена: {existing_car.price} → {car_data['price']}")
            existing_car.price = car_data["price"]

        if existing_car.year != car_data["year"]:
            changes.append(f"год: {existing_car.year} → {car_data['year']}")
            existing_car.year = car_data["year"]

        if existing_car.mileage != car_data["mileage"]:
            changes.append(f"пробег: {existing_car.mileage} → {car_data['mileage']}")
            existing_car.mileage = car_data["mileage"]

        if existing_car.specs != car_data["specs"]:
            changes.append(f"характеристики: {existing_car.specs} → {car_data['specs']}")
            existing_car.specs = car_data["specs"]

        if existing_car.subtitle != car_data["subtitle"]:
            changes.append(f"комплектация: {existing_car.subtitle} → {car_data['subtitle']}")
            existing_car.subtitle = car_data["subtitle"]

        if not changes:
            print(f"Машина {car_data['url']} не изменилась")

        await session.commit()
        return existing_car

    car = Car(**car_data)
    session.add(car)
    await session.commit()
    await session.refresh(car)
    print(f"Добавлена новая машина: {car_data['url']}")
    return car

async def save_generation(session: AsyncSession, generation_data: dict):
    result = await session.execute(
        select(Generation).where(
            and_(
                Generation.mark == generation_data["mark"],
                Generation.model == generation_data["model"],
                Generation.generation_name == generation_data["generation_name"],
                Generation.year_start == generation_data["year_start"],
                Generation.year_end == generation_data["year_end"],
            )
        )
    )
    existing_generation = result.scalar_one_or_none()

    gen = Generation(**generation_data)
    session.add(gen)
    await session.commit()
    await session.refresh(gen)
    print(f"Добавлено: {gen.mark} {gen.model} {gen.generation_name}")
    return gen


def _to_code(text: str) -> str:
    return text.lower().replace(" ", "").replace("-", "").replace("_", "")


async def find_generation(session: AsyncSession, mark: str, model: str, year: int) -> Generation | None:
    result = await session.execute(
        select(Generation)
        .where(
            and_(
                # Пользователь может ввести и название ("Audi"), и код ("audi") — ищем по обоим
                or_(Generation.mark.ilike(mark), func.replace(Generation.mark_code, "_", "") == _to_code(mark)),
                or_(Generation.model.ilike(model), func.replace(Generation.model_code, "_", "") == _to_code(model)),
                Generation.year_start <= year,
                Generation.year_end >= year,
                Generation.gen_code.is_not(None),  # без кода не сможем построить URL
            )
        )
        # На стыке поколений год попадает в два (2015: B8 рест. и B9) — берём более новое
        .order_by(Generation.year_start.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()