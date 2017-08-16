#!/usr/bin/env python
# encoding: utf-8


RABBITMQ_CONFIG = {
        "host": "192.168.2.212",
        "username": "admin",
        "password": "123456"
}

queue_name='queue.push.sms'
CONSUMERS = [
        {
            "exchange": "ACTION",
            "queue": queue_name,
        }
        ]


# "http_url": "http://127.0.0.1/test2/",
