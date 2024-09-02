#!/bin/python3

import configparser
import datetime
from functools import reduce
import json
import time
from typing import Counter
import pika
from sqlalchemy import JSON, BigInteger, Column, DateTime, Integer, MetaData, Row, Table, create_engine

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
    print(data)

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
    #print(data)
    return data

def get_prime_roots(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

def command_callback(ch, method, prop, body):
    decoded = body.decode("utf-8")
    print(f"recived shutdown from user\n{decoded}\n")
    if 'shutdown' in decoded:
        ch.stop_consuming()

#db code
def create_table_if_none():
    global config
    global table
    global engine

    metadata = MetaData()
    db_config = config['db']

    #set table structure
    table = Table(db_config['table'], metadata,
                  Column('id', BigInteger, primary_key=True),
                  Column('number', Integer),
                  Column('factors', JSON),
                  Column('cost', Integer),
                  Column('calculation_date', DateTime))
    
    metadata.create_all(engine)

def insert_item(data):
    global engine
    global table

    with engine.connect() as conn:
        result = conn.execute(table.insert(), data)
        conn.commit()
        print(f"rowCount: {result.rowcount}")

def find_item(num):
    global engine
    global table

    with engine.connect() as conn:
        result = conn.execute(table.select().where(table.c['number']==num)).fetchone()
    if result:
        return json.dumps(result._asdict(), indent=4, sort_keys=True, default=str)
    return None

def connect_db():
    global config
    global engine

    db_config = config['db']
    usr = db_config['user']
    pw = db_config['password']
    h = db_config['host']
    p = db_config['port']
    n = db_config['name']
    engine = create_engine(f"postgresql://{usr}:{pw}@{h}:{p}/{n}", echo=True)
    create_table_if_none()

def main():
    global config

    #load configs
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.sections()

    #setup db connection
    connect_db()

    rabbit_configs = config['rabbit']
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbit_configs['host'], port=rabbit_configs['port'])
    )

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