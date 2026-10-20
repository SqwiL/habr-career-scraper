import asyncio

from database.database import Database
from scraper.scraper import get_and_scrape, test_sync_get_and_scrape


async def main():
    vacancies = test_sync_get_and_scrape(2)
    # vacancies = await get_and_scrape() #correct way
    print(f"Собрано вакансий: {len(vacancies)}")

    database = Database()
    # передаём результаты парсера в базу
    result = database.save_vacancies(vacancies)
    print(f"Добавлено в базу: {result['added']}")
    print(f"Уже было в базе: {result['skipped']}")


if __name__ == "__main__":
    asyncio.run(main())
