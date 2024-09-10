import json
import os
import pytest
from worker.worker import build_athleat_result_data


#db = Db_manager()

def test_build_athleat_result_data():
    path = os.path.split(__file__)[0]
    file = os.path.join(path,'resources/athleats.json')
    result_map = []
    print(path)
    print(file)
    with open(file, 'r') as file:
        data = json.load(file)
        for blob in data:
            result_map.append(build_athleat_result_data(blob))

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

    assert len(entry2) == 7
    assert len(entry3) == 7

