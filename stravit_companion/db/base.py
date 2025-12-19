from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from stravit_companion.config import settings

engine = create_engine(f"sqlite:///{settings.db_path}", future=True)

Session = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
