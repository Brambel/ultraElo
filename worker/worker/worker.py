#!/bin/python3

import configparser
import datetime
from functools import reduce
import json
import os
import time
from typing import Counter
import pika

config = None
table = None
engine = None

def process(ch, method, prop, body):

    num = int(body)
    #check if we have this int he db
    result = find_item(num)
    if result:
        data = json.dumps(result)
    else:
        calc_time = time.time_ns()
        #do work
    ch.basic_ack(delivery_tag=method.delivery_tag)
    #this is where we would send the message back to the user
    print(f"{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}, {data}")

def notify_user(n, dic):
    s = ""
    for key,val in dic.items():
        s+=f"{key}"
        if val > 1:
            s+=f"^{val}, "
        else:
            s+=","

    print(f"the factors for {n}: {s}")

def build_athleat_result_data(data):
    raw_map = json.load(data)
    event_map = None
    required_keys = {'firstname','lastname','participant_id','age','gender', 'place', 'time'}
    if set(required_keys).issubset(raw_map.keys()):
        event_map = {'first_name':raw_map['firstname'],'last_name':raw_map['lastname'],
                     'ultrasignup_id':raw_map['participant_id'], 'age':raw_map['age'],
                     'gender':raw_map['gender'], 'place':raw_map['place'],'time':raw_map['time']}
    return event_map


def command_callback(ch, method, prop, body):
    decoded = body.decode("utf-8")
    print(f"recived shutdown from user\n{decoded}\n")
    if 'shutdown' in decoded:
        ch.stop_consuming()

def main():
    global config

    #load configs
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.sections()
    rabbit_configs = config['rabbit']
    #setup db connection
    connect_db()

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
                           on_message_callback=process)
    channel.basic_consume(queue=rabbit_configs['command_queue'],
                           on_message_callback=command_callback)
    
    channel.start_consuming()

if __name__ == "__main__":
    main()