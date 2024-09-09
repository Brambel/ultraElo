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

def test_data_entry(session):

    event1 = Event(name="race1",location="usa",date="8/15/87",distance="50k")
    #result = Result(place=1,time="0:30:00")
    #athleat1 = Athleat(first_name="jim",last_name="bob",age="37",overall_elo=2000)
    #athleat2 = Db_manager.Athleat(athleat_id=2,first_name="foo",last_name="bar",age="22",overall_elo=1000)

    session.add(event1)
    print(session.new)
    #session.add(result)
    #session.add(athleat1)
    session.commit()

    stmnt = select(Event).where(Event.name == "race1")
    ev = session.execute(stmnt).first()
    print(f"ev: {str(ev)}")
    #res = session.query(Result).get(result.place)
    #ath = session.querry(Athleat).get(athleat1.athleat_id)
    event_obj=ev._mapping['Event']
    assert "race1" == event_obj.name
    #assert res.place == 1
    #assert res.athleat.athleat_id == athleat1.athleat_id