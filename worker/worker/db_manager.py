#!/bin/python3

import logging
import os
import sys
from typing import List, Optional
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped

#ORM classes
class Base(DeclarativeBase):
    pass


class Athleat(Base):
    __tablename__ = "athleats"

    athleat_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    gender: Mapped[str] = mapped_column(default='')
    age: Mapped[Optional[int]]
    ultrasignup_id: Mapped[Optional[int]]
    overall_elo: Mapped[int] = mapped_column(default=1000)
    elo_50k: Mapped[int] = mapped_column(default=1000)
    elo_50m: Mapped[int] = mapped_column(default=1000)
    elo_100k: Mapped[int] = mapped_column(default=1000)
    elo_100m: Mapped[int] = mapped_column(default=1000)

    results: Mapped[List["Result"]] = relationship(back_populates="athleat")

    def __repr__(self) -> str:
        return f"User(athleat_id={self.athleat_id!r}, name(f:l)={self.first_name!r},{self.last_name!r}, ultrasignup_id={self.ultrasignup_id!r}, elo(oa:50k,50m,100k,100m)={self.overall_elo!r}:{self.elo_50k!r}:{self.elo_50m!r}:{self.elo_100k!r}:{self.elo_100m!r}, events[]=[{self.events!r}])"

class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    location: Mapped[str]
    date: Mapped[str]
    distance: Mapped[str] #see about defining enums

    results: Mapped[List["Result"]] = relationship(back_populates="event")
    
    #purposly left out, test how well it works
    def __repr__(self) -> str:
        return f"Event(event_id={self.event_id!r}, name={self.name!r}, location={self.location!r}, date={self.date!r}, distance={self.distance!r}, results={self.results!r}"

class Result(Base):
    __tablename__ = "results"

    place: Mapped[int]
    time: Mapped[str]

    #relationships
    athleat_id: Mapped[int] = mapped_column(ForeignKey("athleats.athleat_id"), primary_key=True)
    athleat: Mapped["Athleat"] = relationship(back_populates="results")

    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id"), primary_key=True)
    event: Mapped["Event"] = relationship(back_populates="results")

class Db_manager():

    def __init__(self, config):
        self.config = config

        self.connect_db(self)
        self.create_tables_if_none(self)

    def set_logger(self):
        # set up logging to console
        console = logging.StreamHandler(stream=sys.stdout)
        console.setLevel(logging.WARNING)

        # set up logging to file
        logging.basicConfig(
            filename='db_manager.log',
            level=logging.INFO, 
            format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            handlers=[
            console,
            ]
        )

        
        # set a format which is simpler for console use
        formatter = logging.Formatter('[%(asctime)s] %(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
        self.logger = logging.getLogger(__name__)

        #now set engine loggin
        alch_log = logging.getLogger("sqlalchemy.engine")
        alch_log.setLevel(logging.INFO)
        #may want to see about setting a diff log level stream?

    def add_athleat_result(result_map):
        #need to impliment
        pass

    def connect_db(self):

        usr = os.environ.get("DB_USER","find_default")
        pw = os.environ.get("DB_PASS","find_default")
        h = os.environ.get("DB_HOST","find_default")
        p = os.environ.get("DB_PORT","find_default")
        n = os.environ.get("DB_NAME","find_default")
        self.engine = create_engine(f"postgresql://{usr}:{pw}@{h}:{p}/{n}")
        