import json
import os
import pytest
from worker.worker import scraper

path = os.path.split(__file__)[0]
scraper.set_logger()

def test_build_athleat_result_data():   
    file = os.path.join(path,'resources/athleats.json')
    result_map = []

    with open(file, 'r') as file:
        data = json.load(file)
        for blob in data:
            result_map.append(scraper.build_athleat_result_data(blob, {'distance':"10k",'name':"fake race time",'year':2024}))

    entry1 = result_map[0]
    entry2 = result_map[1]
    entry3 = result_map[2]

    assert entry1['first_name'] == 'Samuel'
    assert entry1['last_name'] == 'Ongaki'
    assert entry1['age'] == 40
    assert entry1['ultrasignup_id'] == 2274270
    assert entry1['gender'] == 'M'
    assert entry1['place'] == 1
    assert entry1['time'] == 12602000

    assert len(entry2) == 10
    assert len(entry3) == 10

def test_parse_event_page(html_cont=None):
    if not html_cont:
        file = os.path.join(path,'resources/eventResponse.html')
        with open(file, 'r') as f:
            html_cont = f.read()

    event_map = scraper.parse_event_page(html_cont)
    assert event_map['distance'] == "10k"
    assert event_map['name'] == "Jewel of the Valley"
    assert event_map['year'] == "2023"

def test_parse_event_page_bad_data():
    assert scraper.parse_event_page("<head></head>") == None


def test_build_athleat_bad_data():
    #missing parts of blob
    assert not scraper.build_athleat_result_data({"firstname": "bob"}, {'distance':"10k",'name':"fake race time",'year':2024})
    
    #missing parts of event
    file = os.path.join(path,'resources/athleats.json')

    with open(file, 'r') as file:
        data = json.load(file)
        assert not scraper.build_athleat_result_data(data[0], {})

def test_retrieve_event_page():
    result = scraper.retrieve_event_page(99406)
    assert result
    test_parse_event_page(result)

    