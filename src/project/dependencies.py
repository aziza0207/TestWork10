import os
from collections.abc import Generator
from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session, sessionmaker
from .database import engine
from sqlalchemy import exc


def get_db_session() -> Generator[Session, None, None]:
    factory = sessionmaker(engine)
    with factory() as session:
        try:
            yield session
            session.commit()
        except exc.SQLAlchemyError as error:
            session.rollback()
            raise error
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()
