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
        count = Counter(get_prime_roots(int(body)))
        cost = int(time.time_ns()) - calc_time
        #format output msg
        notify_user(num,count)

        #save in db
        data = format_data(prop.headers, num, count, cost)
        insert_item(data)
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

def format_data(header, n, fact, cost):
    data ={
        'id': header['id'],
        'number': n,
        'factors': {},
        'cost': int(cost),
        'calculation_date': datetime.datetime.now()
    }
    data['factors'] = json.loads(json.dumps(fact))
    return data


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