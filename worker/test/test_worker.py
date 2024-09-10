import json
import pytest
from worker.worker import build_athleat_result_data

def test_build_athleat_result_data():
    with open('resources/athleats.json', 'r') as file:
        data = json.load(file)
    print(data)

    assert False