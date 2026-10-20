from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from database.models import Base, Company, Location, Skill, Vacancy, VacancySkill

SQLITE_URI = "sqlite:///habr_career.db"


class Database:
    def __init__(self, uri=SQLITE_URI):
        # engine управлеят соединением с бд и выполняет sql запросы
        self.engine = create_engine(uri)
        # Создаем таблицы по описанию Base.metadata, если их еще нет в бд
        Base.metadata.create_all(self.engine)

    def save_vacancies(self, vacancies):
        """Добавить новые вакансии, пропуская уже сохранённые по habr_id."""
        added = 0
        skipped = 0

        # сессия выполняет запросы и отслеживает изменения объектов
        # при выходе из with сессия закрывается
        with Session(self.engine) as session:
            # одна транзакция на весь список
            # успешный выход подтверждает изменения (commit)
            # исключение откатывает их (rollback)
            with session.begin():
                for scraped_vacancy in vacancies:
                    # scalar возвращает первый ORM-объект либо None
                    existing_vacancy = session.scalar(
                        select(Vacancy).where(
                            Vacancy.habr_id == scraped_vacancy.habr_id
                        )
                    )

                    if existing_vacancy is not None:
                        skipped += 1
                        continue

                    # компанию сохраняем один раз, а в вакансиях используем её id
                    company = session.scalar(
                        select(Company).where(
                            Company.company_name == scraped_vacancy.company
                        )
                    )
                    if company is None:
                        company = Company(company_name=scraped_vacancy.company)
                        session.add(company) # добавить в базу на изменение
                        session.flush() # выполнить sql insert и теперь company.id не None

                    # если город не указан, внешний ключ останется none
                    location_id = None
                    if scraped_vacancy.location is not None:
                        location = session.scalar(
                            select(Location).where(
                                Location.location_name == scraped_vacancy.location
                            )
                        )
                        if location is None:
                            location = Location(
                                location_name=scraped_vacancy.location
                            )
                            session.add(location)
                            session.flush()
                        location_id = location.id

                    # создаем объект для сохранения в бд, используя id из внешних таблиц
                    vacancy = Vacancy(
                        title=scraped_vacancy.title,
                        company_id=company.id,
                        seniority=scraped_vacancy.seniority,
                        remote_allowed=scraped_vacancy.remote_allowed,
                        location_id=location_id,
                        salary=scraped_vacancy.salary,
                        habr_id=scraped_vacancy.habr_id,
                    )
                    session.add(vacancy)
                    session.flush()

                    for skill_name in set(scraped_vacancy.skills):
                        skill = session.scalar(
                            select(Skill).where(Skill.skill_name == skill_name)
                        )
                        if skill is None:
                            skill = Skill(skill_name=skill_name)
                            session.add(skill)
                            session.flush()

                        # каждая строка связывает одну вакансию с одним навыком
                        session.add(
                            VacancySkill(
                                vacancy_id=vacancy.id,
                                skill_id=skill.id,
                            )
                        )

                    added += 1

        return {"added": added, "skipped": skipped}
