#!/bin/python3

import configparser
import datetime
import json
import os
import pika
#from db_manager import Db_manager

config = None
db = None

def process_athleat_result(ch, method, prop, body):
    global db

    data = json.load(body)
    result_map = build_athleat_result_data
    db.add_athleat_result(result_map)


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
    event_map = None
    required_keys = {'firstname','lastname','participant_id','age','gender', 'place', 'time'}
    if set(required_keys).issubset(data.keys()):
        #get all the info
        event_map = {'first_name':data['firstname'],'last_name':data['lastname'],
                     'ultrasignup_id':data['participant_id'], 'age':data['age'],
                     'gender':data['gender'], 'place':data['place']}
        #convert strings to correct data types
        event_map['time'] = int(data['time'])

    return event_map


def command_callback(ch, method, prop, body):
    decoded = body.decode("utf-8")
    print(f"recived shutdown from user\n{decoded}\n")
    if 'shutdown' in decoded:
        ch.stop_consuming()

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

if __name__ == "__main__":
    main()