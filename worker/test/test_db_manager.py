from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.orm import sessionmaker
import pytest
from worker.db_manager import Event, Result, Athleat, Base

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


@pytest.fixture(scope="session")
def session():
    session = Session()
    yield session
    session.close()

def test_basic_objects(session):

    event1 = Event(name="race1",location="usa",date="8/15/87",distance="50k")
    athleat1 = Athleat(first_name="jim",last_name="bob",age="37",overall_elo=2000)
    result = Result(place=1,time="0:30:00", event=event1, athleat=athleat1)
    session.add(event1)
    session.add(result)
    session.commit()

    #use statment select to get a list of row tuples
    stmnt = select(Event).where(Event.name == "race1")
    ev_row = session.execute(stmnt).first()
    print(f"row-> {ev_row}")
    ev_obj = ev_row[0]
    print(f"ev_obj-> {ev_obj}")

    #use session get for primary keys
    res_obj = session.get(Result,(1,1))
    ath_res = session.get(Athleat,1)

    assert ev_obj.name == "race1"
    assert res_obj.place == 1
    assert res_obj.event_id == 1
    assert ath_res.age == 37
    assert res_obj.athleat.elo_50k == 1000