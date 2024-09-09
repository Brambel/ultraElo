#!/bin/python3

import configparser
from contextlib import asynccontextmanager
import datetime
import os
import time
import pika
from fastapi import FastAPI, Request, status
import uvicorn


connection = None
rabbit_configs = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # establish the connection
    global connection
    global rabbit_configs

    config = configparser.ConfigParser()
    config.read("config.ini")
    config.sections()
    rabbit_configs = config['rabbit']

    host = 'rabbit-rabbitmq'
    port = rabbit_configs['port']
    user = os.environ.get("RABBIT_USER")
    pwd = os.environ.get("RABBIT_PWD")

    print(f"{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}, host: {host}")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port,socket_timeout=None,
                                  credentials=pika.PlainCredentials(user, pwd), heartbeat=60)
    )
    yield
    # Clean up the connection
    if connection:
        connection.close()

app = FastAPI(lifespan=lifespan)


@app.post("/data")
async def data(request: Request):
    try:
        incoming = await request.json()
        print(f"{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}, {incoming}")
        data = incoming['count']
        push_to_queue(data)

        return {"message":"success"},status.HTTP_200_OK

    except Exception as e:
        print(f"Error sending: {e}")
        return {"message":"internal error"},status.HTTP_500_INTERNAL_SERVER_ERROR

@app.post("/command")
async def command(request: Request):
    try:
        incoming = await request.json()
        print(incoming)
        command = incoming['command']
        if 'stop' in command:
            push_command(command)
            return {"message":"success, shutting down worker"}, status.HTTP_200_OK
        else:
            return {"message":"success, shutting down"},status.HTTP_401_UNAUTHORIZED

    except Exception as e:
        print(f"Error sending: {e}")
        return {"message":"internal error"},status.HTTP_500_INTERNAL_SERVER_ERROR

def push_to_queue(count):
    global connection
    global rabbit_configs

    print(f"recived: {count}")

    channel = connection.channel()
    channel.queue_declare(queue=rabbit_configs['work_queue'])
    prop = pika.BasicProperties(headers={"id":int(time.time() * 1000)})
    channel.basic_publish(exchange='', routing_key=rabbit_configs['work_queue'],
                           properties=prop,body=count)

def push_command(command):
    global connection
    global rabbit_configs

    print(f"recived: {command}")

    channel = connection.channel()
    channel.queue_declare(queue=rabbit_configs['command_queue'])
    channel.basic_publish(exchange='', routing_key=rabbit_configs['command_queue'], body="shutdown")



if __name__ == "__main__":

    print(f"{datetime.datetime.now().strftime("%m/%d %H:%M:%S")}, host: {os.environ.get("RABBITMQ_HOST")}")
    uvicorn.run(app,host="0.0.0.0",port=8000)