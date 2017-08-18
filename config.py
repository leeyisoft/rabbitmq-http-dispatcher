#!/usr/bin/env python
# encoding: utf-8

"""
 amqp://username:password@host:port/<virtual_host>[?query-string]
 you are using the default "/" virtual host, the value should be `%2f`.
 @link https://github.com/pika/pika/blob/master/pika/connection.py
"""
rabbitmq_config = 'amqp://dev:123456@192.168.2.212:5672/%2fdev'

sms_name = 'push.sms'
qq_name = 'push.qq'
wechat_name = 'push.wechat'

exchange_type = 'direct'
CONSUMERS = [
    {
        'exchange': '%s.exchange.%s' % (exchange_type, sms_name),
        'exchange_type': 'direct',
        'queue_name': 'queue.%s' % sms_name,
        'routing_key': 'routingkey.%s' % sms_name,
        'durable': True,
    },
    {
        'exchange': '%s.exchange.%s' % (exchange_type, qq_name),
        'exchange_type': 'direct',
        'queue_name': 'queue.%s' % qq_name,
        'routing_key': 'routingkey.%s' % qq_name,
        'durable': True,
    },
    {
        'exchange': '%s.exchange.%s' % (exchange_type, wechat_name),
        'exchange_type': 'direct',
        'queue_name': 'queue.%s' % wechat_name,
        'routing_key': 'routingkey.%s' % wechat_name,
        'durable': True,
    },
]
