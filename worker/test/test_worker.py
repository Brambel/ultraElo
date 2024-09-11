import json
import os
import pytest
from worker.worker.scraper import build_athleat_result_data, parse_event_page

path = os.path.split(__file__)[0]

def test_build_athleat_result_data():   
    file = os.path.join(path,'resources/athleats.json')
    result_map = []

    with open(file, 'r') as file:
        data = json.load(file)
        for blob in data:
            result_map.append(build_athleat_result_data(blob, {'distance':"10k",'name':"fake race time",'year':2024}))

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

def test_parse_event_page():
    file = os.path.join(path,'resources/eventResponse.html')
    with open(file, 'r') as f:
        html_cont = f.read()
    event_map = parse_event_page(html_cont)

    assert event_map['distance'] == "10k"
    assert event_map['name'] == "Jewel of the Valley"
    assert event_map['year'] == "2023"