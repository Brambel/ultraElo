#!/bin/python3

class raw_event_results():
    def __init__(self, event_map):
        self.athleat_maps = []

        self._distance = event_map['distance']
        self._name = event_map['name']
        self._year = event_map['year'] 
        self._loc = event_map['location']

    def add_athleat_result(self, map):
        if map:
            self.athleat_maps.append(map)
    
    def get_distance(self):
        return self._distance
    
    def get_name(self):
        return self._name
    
    def get_year(self):
        return self._year
    
    def get_location(self):
        return self._loc