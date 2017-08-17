#!/usr/bin/env python
# encoding: utf-8

"""
 amqp://username:password@host:port/<virtual_host>[?query-string]
 you are using the default "/" virtual host, the value should be `%2f`.
 @link https://github.com/pika/pika/blob/master/pika/connection.py
"""
rabbitmq_config = 'amqp://dev:123456@192.168.2.212:5672/%2fdev'

queue_name = 'push.sms'
exchange_type = 'direct'
CONSUMERS = [
    {
        'exchange': '%s.exchange.%s' % (exchange_type, queue_name),
        'exchange_type': 'direct',
        'queue_name': 'queue.%s' % queue_name,
        'routing_key': 'routingkey.%s' % queue_name,
        'durable': True,
    }
]
