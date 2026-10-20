from sqlalchemy import func, select

from database.models import Company, Skill, Vacancy, VacancySkill


def _execute(engine, query):
    # выполняем запрос и возвращаем готовые строки как список словарей
    with engine.connect() as connection:
        return [dict(row) for row in connection.execute(query).mappings()] 


def companies_by_vacancies(engine):
    """Количество вакансий по компаниям.

    SELECT c.company_name, COUNT(v.id) AS vacancy_count
    FROM companies AS c
    JOIN vacancies AS v ON v.company_id = c.id
    GROUP BY c.company_name
    ORDER BY c.company_name;
    """
    query = (
        select(Company.company_name, func.count(Vacancy.id).label("vacancy_count"))
        .join(Vacancy, Vacancy.company_id == Company.id)
        .group_by(Company.company_name)
        .order_by(Company.company_name)
    )
    return _execute(engine, query)


def seniority_distribution(engine):
    """Количество вакансий по уровням специалистов.

    SELECT COALESCE(seniority, 'Не указан') AS seniority,
           COUNT(*) AS vacancy_count
    FROM vacancies
    GROUP BY COALESCE(seniority, 'Не указан')
    ORDER BY seniority;
    """
    level = func.coalesce(Vacancy.seniority, "Не указан")
    query = (
        select(level.label("seniority"), func.count(Vacancy.id).label("vacancy_count"))
        .group_by(level)
        .order_by(level)
    )
    return _execute(engine, query)


def remote_distribution(engine):
    """Количество вакансий с удалёнкой и без неё.

    SELECT remote_allowed, COUNT(*) AS vacancy_count
    FROM vacancies
    GROUP BY remote_allowed
    ORDER BY remote_allowed;
    """
    query = (
        select(Vacancy.remote_allowed, func.count(Vacancy.id).label("vacancy_count"))
        .group_by(Vacancy.remote_allowed)
        .order_by(Vacancy.remote_allowed)
    )
    return _execute(engine, query)


def skills_by_demand(engine):
    """Количество вакансий, в которых требуется каждый навык.

    SELECT s.skill_name, COUNT(vs.vacancy_id) AS vacancy_count
    FROM skills AS s
    JOIN vacancy_skills AS vs ON vs.skill_id = s.id
    GROUP BY s.skill_name
    ORDER BY s.skill_name;
    """
    query = (
        select(Skill.skill_name, func.count(VacancySkill.vacancy_id).label("vacancy_count"))
        .join(VacancySkill, VacancySkill.skill_id == Skill.id)
        .group_by(Skill.skill_name)
        .order_by(Skill.skill_name)
    )
    return _execute(engine, query)


def salary_by_seniority(engine):
    """Средняя известная зарплата по уровням специалистов, в рублях.

    SELECT COALESCE(seniority, 'Не указан') AS seniority,
           AVG(salary) AS average_salary
    FROM vacancies
    GROUP BY COALESCE(seniority, 'Не указан')
    ORDER BY seniority;
    """
    level = func.coalesce(Vacancy.seniority, "Не указан")
    query = (
        select(
            level.label("seniority"),
            func.avg(Vacancy.salary).label("average_salary"),
        )
        .group_by(level)
        .order_by(level)
    )
    return _execute(engine, query)
