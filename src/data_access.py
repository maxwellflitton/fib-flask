from flask import _app_ctx_stack
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from config import GlobalParams


class DbEngine:
    """
    This is an class for managing the connection and game_sessions to the database.

    Attributes:
        engine (sqlalchemy.create_engine.return_value): connection to DB
        session (sqlalchemy.orm.sessionmaker.return_value): manages game_sessions with database
    """

    def __init__(self) -> None:
        """
        The constructor for the DbEngine class.
        """
        params = GlobalParams()
        self.base = declarative_base()
        self.engine = create_engine(params.get("DB_URL"),
                                    echo=True,
                                    pool_recycle=3600,
                                    pool_size=2,
                                    max_overflow=1,
                                    connect_args={
                                        'connect_timeout': 5
                                    })
        self.session = scoped_session(sessionmaker(
            bind=self.engine
        ),
                                      scopefunc=_app_ctx_stack)
        self.url = params.get("DB_URL")


dal = DbEngine()
