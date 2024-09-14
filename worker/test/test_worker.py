import json
import os
import pytest
from worker.worker import scraper

path = os.path.split(__file__)[0]
scraper.set_logger()

def test_build_athleat_result_data(data=None):   
    file = os.path.join(path,'resources/athleats.json')
    result_map = []
    
    if not data:
        with open(file, 'r') as file:
            data = json.load(file)

    for blob in data:
        result_map.append(scraper.build_athleat_result_data(blob))

    entry1 = result_map[0]
    entry2 = result_map[1]
    entry3 = result_map[2]

    assert entry1['first_name'] == 'Benjamin'
    assert entry1['last_name'] == 'Velasquez'
    assert entry1['age'] == 30
    assert entry1['ultrasignup_id'] == 2306958
    assert entry1['gender'] == 'M'
    assert entry1['place'] == 1
    assert entry1['time'] == 2954488

    assert len(entry2) == 7
    assert len(entry3) == 7

def test_parse_event_page(html_cont=None):
    if not html_cont:
        file = os.path.join(path,'resources/eventResponse.html')
        with open(file, 'r') as f:
            html_cont = f.read()

    event_map = scraper.parse_event_page(html_cont)
    assert event_map['distance'] == "10k"
    assert event_map['name'] == "Jewel of the Valley"
    assert event_map['year'] == "2023"
    assert event_map['location'] == "Yakima, WA"

def test_parse_event_page_bad_data():
    assert scraper.parse_event_page("<head></head>") == None


def test_build_athleat_bad_data():
    #missing parts of blob
    assert not scraper.build_athleat_result_data({"firstname": "bob"})

def test_retrieve_event_page():
    id = 99406
    result = scraper.retrieve_event_page(id)
    assert result
    test_parse_event_page(result)

def test_retrieve_result_page():
    id = 99406
    result = scraper.retrieve_athleat_page(id)

    assert result 

    test_build_athleat_result_data(result)