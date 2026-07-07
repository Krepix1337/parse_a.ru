from sqlalchemy import select, and_
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

        print(f"Обновлена машина {car_data['url']}: {', '.join(changes)}")
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

    if existing_generation:
        print(f"Уже есть: {generation_data['mark']} {generation_data['model']} {generation_data['generation_name']}")
        return existing_generation

    gen = Generation(**generation_data)
    session.add(gen)
    await session.commit()
    await session.refresh(gen)
    print(f"Добавлено: {gen.mark} {gen.model} {gen.generation_name}")
    return gen


async def find_generation(session: AsyncSession, mark: str, model: str, year: int) -> str | None:
    result = await session.execute(
        select(Generation).where(
            and_(
                Generation.mark.ilike(mark),
                Generation.model.ilike(model),
                Generation.year_start <= year,
                Generation.year_end >= year,
            )
        )
    )
    generation = result.scalar_one_or_none()
    return generation.generation_name if generation else None