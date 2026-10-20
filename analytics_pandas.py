import pandas as pd
from sqlalchemy import select

from database.models import Company, Skill, Vacancy, VacancySkill


def _read_table(engine, model):
    # читаем с базы в df
    with engine.connect() as connection:
        return pd.read_sql(select(model), connection)


def companies_by_vacancies(engine):
    """Количество вакансий по компаниям

    SELECT c.company_name, COUNT(v.id) AS vacancy_count
    FROM companies AS c
    JOIN vacancies AS v ON v.company_id = c.id
    GROUP BY c.company_name
    ORDER BY c.company_name;
    """
    companies = _read_table(engine, Company)
    vacancies = _read_table(engine, Vacancy)

    joined = vacancies.merge(
        companies,
        left_on="company_id",
        right_on="id",
    )

    return (
        joined.groupby("company_name")
        .size()
        .reset_index(name="vacancy_count")
    )

def seniority_distribution(engine):
    """Количество вакансий по уровням специалистов.

    SELECT COALESCE(seniority, 'Не указан') AS seniority,
           COUNT(*) AS vacancy_count
    FROM vacancies
    GROUP BY COALESCE(seniority, 'Не указан')
    ORDER BY seniority;
    """
    df = _read_table(engine, Vacancy)

    df["seniority"] = df["seniority"].fillna("Не указан")

    return (
        df.groupby("seniority")
        .size()
        .reset_index(name="vacancy_count")
    )

def remote_distribution(engine):
    """Количество вакансий с удалёнкой и без неё.

    SELECT remote_allowed, 
        COUNT(*) AS vacancy_count
    FROM vacancies
    GROUP BY remote_allowed
    ORDER BY remote_allowed;
    """
    df = _read_table(engine, Vacancy)
    return df.groupby("remote_allowed").size().reset_index(name="vacancy_count")


def skills_by_demand(engine):
    """Количество вакансий, в которых требуется каждый навык.

    SELECT s.skill_name, 
        COUNT(vs.vacancy_id) AS vacancy_count
    FROM skills AS s
    JOIN vacancy_skills AS vs 
    ON vs.skill_id = s.id
    GROUP BY s.skill_name
    ORDER BY s.skill_name;
    """
    skills = _read_table(engine, Skill)
    links = _read_table(engine, VacancySkill)
    joined = links.merge(skills, left_on="skill_id", right_on="id")
    return (
        joined.groupby("skill_name")
        .size()
        .reset_index(name="vacancy_count")
    )


def salary_by_seniority(engine):
    """Средняя известная зарплата по уровням специалистов, в рублях.

    SELECT COALESCE(seniority, 'Не указан') AS seniority,
           AVG(salary) AS average_salary
    FROM vacancies
    GROUP BY COALESCE(seniority, 'Не указан')
    ORDER BY seniority;
    """
    df = _read_table(engine, Vacancy)
    df["seniority"] = df["seniority"].fillna("Не указан")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")  #coerce — превратить неправильные значения в пропуски и продолжить
    
    return (
        df.groupby("seniority", as_index=False)["salary"]
        .mean()
        .rename(columns={"salary": "average_salary"})
    )
