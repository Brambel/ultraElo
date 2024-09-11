#!/bin/python3

import configparser
import datetime
import json
import logging
import os
import re
import sys
import pika

from worker.worker.db_manager import Db_manager
from lxml import html
#from db_manager import Db_manager

config = None
db = None
logger = None

def process_athleat_result(ch, method, prop, body):
    global db

    data = json.load(body)
    result_map = build_athleat_result_data
    db.add_athleat_result(result_map)


    ch.basic_ack(delivery_tag=method.delivery_tag)
    #this is where we would send the message back to the user
    print(f"{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}, {data}")

def parse_event_page(event_page):
    root = html.fromstring(event_page)
    try:
        distance = root.xpath("//a[@class='event_selected_link']")[0].text
        name = root.xpath('//h1[@class="event-title"]')[0].text
        raw_year = root.xpath('//span[@class="event-date"]')[0].text
        year = re.search('(\d{4})', raw_year).group(1)
        return {'distance':distance.lower(),'name':name,'year':year}
    except Exception as e: 
        logger.error("failed to parse event page,%s",repr(e))
    return None

def build_athleat_result_data(data, event_data):
    #parse the event page first
    event_map = None
    required_keys = {'firstname','lastname','participant_id','age','gender', 'place', 'time'}
    if set(required_keys).issubset(data.keys()):
        #get all the info
        event_map = {'first_name':data['firstname'],'last_name':data['lastname'],
                     'ultrasignup_id':data['participant_id'], 'age':data['age'],
                     'gender':data['gender'], 'place':data['place']}
        event_map['time'] = int(data['time'])
    else:
        logger.error("result is missing keys: %s",[item for item in required_keys if item not in data.keys()])
        return None
    
    #convert strings to correct data types 
    if set({'distance','name','year'}).issubset(event_data.keys()):        
        event_map['distance'] = event_data['distance']
        event_map['event_name'] = event_data['name']
        event_map['year'] = event_data['year']
    else:
        logger.error("event is missing keys: %s",[item for item in {'distance','name','year'} if item not in event_data.keys()])
        return None
    return event_map


def command_callback(ch, method, prop, body):
    decoded = body.decode("utf-8")
    print(f"recived shutdown from user\n{decoded}\n")
    if 'shutdown' in decoded:
        ch.stop_consuming()

def set_logger():
        global logger
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

        # set up logging to console
        
        # set a format which is simpler for console use
        formatter = logging.Formatter('[%(asctime)s] %(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
        logger = logging.getLogger(__name__)


def main():
    global config
    global db
    
    #load configs
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.sections()
    rabbit_configs = config['rabbit']

    #connect to rabbit
    host = 'rabbit-rabbitmq'
    port = rabbit_configs['port']
    user = os.environ.get("RABBIT_USER")
    pwd = os.environ.get("RABBIT_PWD")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port,socket_timeout=None,
                                  credentials=pika.PlainCredentials(user, pwd),heartbeat=60))

    channel = connection.channel()
    channel.queue_declare(queue=rabbit_configs['work_queue'])
    channel.queue_declare(queue=rabbit_configs['command_queue'])
    channel.basic_consume(queue=rabbit_configs['work_queue'],
                           on_message_callback=process_athleat_result)
    channel.basic_consume(queue=rabbit_configs['command_queue'],
                           on_message_callback=command_callback)
    
    #setup db connection
    db = Db_manager(config)

    channel.start_consuming()

def init():
    set_logger()

if __name__ == "__main__":
    main()
