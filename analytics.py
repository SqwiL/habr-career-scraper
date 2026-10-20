from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

import analytics_pandas
import analytics_sqlalchemy
from database.database import SQLITE_URI


def print_results(title, sqlalchemy_result, pandas_result):
    print(f"\n{title}")
    print("SQLAlchemy:")
    # список словарей в таблицу для удобной печати
    sql_table = pd.DataFrame(sqlalchemy_result)
    print(sql_table)

    print("Pandas:")
    print(pandas_result)


def main():
    if not Path("habr_career.db").is_file():
        print("База habr_career.db не найдена. Сначала запустите python main.py.")
        return

    engine = create_engine(SQLITE_URI)
    try:
        print_results(
            "1. Вакансии по компаниям",
            analytics_sqlalchemy.companies_by_vacancies(engine),
            analytics_pandas.companies_by_vacancies(engine),
        )
        

    finally:
        engine.dispose()  # освобождает ресурсы


if __name__ == "__main__":
    main()


'''
print_results(
    "2. Вакансии по уровням",
    analytics_sqlalchemy.seniority_distribution(engine),
    analytics_pandas.seniority_distribution(engine),
)

print_results(
    "3. Вакансии с удалёнкой и без неё",
    analytics_sqlalchemy.remote_distribution(engine),
    analytics_pandas.remote_distribution(engine),
)

print_results(
    "4. Вакансии по навыкам",
    analytics_sqlalchemy.skills_by_demand(engine),
    analytics_pandas.skills_by_demand(engine),
)

print_results(
    "5. Средняя зарплата по уровням, руб.",
    analytics_sqlalchemy.salary_by_seniority(engine),
    analytics_pandas.salary_by_seniority(engine),
)

'''
