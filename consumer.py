#!/usr/bin/env python
# encoding: utf-8

"""
消费者

http://pika.readthedocs.org/en/latest/examples/asynchronous_consumer_example.html
http://pika.readthedocs.org/en/latest/examples/blocking_consume.html

daemon
https://github.com/gmr/rejected
https://github.com/serverdensity/python-daemon
http://slaytanic.blog.51cto.com/2057708/742049
https://docs.python.org/2/library/multiprocessing.html daemon
"""
import os
import time
import pika
import logging
import traceback
from pika.exceptions import AMQPConnectionError

from multiprocessing import Pool


try:
    from .daemon import Daemon
except Exception as e:
    from daemon import Daemon

logger_name = 'rabbit_consumer'

class Consumer(object):
    connection = None
    channel = None

    """
    消费者, 从消息队列中取出, 处理
    """
    def __init__(self, rabbitmq_config):
        """
        """
        self.connection = pika.BlockingConnection(
            pika.URLParameters(rabbitmq_config)
        )
        self.channel = self.connection.channel()
        self.exchange_name = None
        self.queue_name = None

    def start_consuming(self, callback_func, auto_ack=False):
        """
        """
        self.channel.basic_consume(self.queue_name, callback_func
            , auto_ack=auto_ack
        )
        self.channel.start_consuming()

    def stop_consuming(self):
        """
        """
        self.channel.stop_consuming()

    def close(self):
        """
        停止
        """
        logging.getLogger(logger_name).info(f"pid[{os.getpid()}] clone consumer begin......")
        self.connection.close()

    def declare_exchange(self, exchange_type, exchange_name, durable=True, auto_delete=False):
        """
        定义一个exchange
        """
        self.exchange_name = exchange_name
        self.channel.exchange_declare(exchange=exchange_name
            , exchange_type=exchange_type
            , durable=durable
            , auto_delete=auto_delete
        )

    def declare_queue(self, queue_name, routing_key="*", durable=True, auto_delete=False):
        """
        定义一个queue
        """
        self.queue_name = queue_name
        self.channel.queue_declare(
            queue=self.queue_name
            , durable=durable
            , auto_delete=auto_delete)
        rklist = routing_key if type(routing_key)==list else [routing_key]
        for rk in rklist:
            self.channel.queue_bind(
                exchange=self.exchange_name
                , queue=self.queue_name
                , routing_key=rk
            )

class ConsumerHandler(object):
    """
    消费者处理hander
    """
    config = {}
    rabbitmq_config = ''
    consumer = None

    def __init__(self, config, rabbitmq_config=None):
        """
        初始化
        """
        self.config = config
        self.rabbitmq_config = rabbitmq_config if rabbitmq_config else config.get('rabbitmq_config')

    def init_consumer(self, config):
        """
        初始化 consumer
        """
        print('init_consumer ', time.time())
        exchange_type = config.get('exchange_type')
        exchange = config.get('exchange')
        queue_name = config.get('queue_name')
        routing_key = config.get('routing_key', '*')
        durable = config.get('durable', True)
        auto_delete = config.get('auto_delete', False)

        self.consumer = Consumer(self.rabbitmq_config)
        self.consumer.declare_exchange(exchange_type, exchange, durable, auto_delete)
        self.consumer.declare_queue(queue_name, routing_key, durable, auto_delete)

    def run(self, callback_func):
        while True:
            try:
                if self.consumer is None:
                    self.init_consumer(self.config)
                self.consumer.start_consuming(callback_func=callback_func)
            except AMQPConnectionError as e:
                # 设置 self.consumer = None 会重新连接
                self.consumer = None
            except Exception as e:
                print('=== STEP ERROR INFO START')
                traceback.print_exc()
                print('=== STEP ERROR INFO END')
                raise e

class ConsumerDispatcher():

    def setup_consumer(self, kwargs, callback_func):
        """
        初始化一个consumer, 并开始处理消息

        """
        logging.getLogger(logger_name).info(f"pid[{os.getpid()}] setup consumer begin......")
        try:
            handler = ConsumerHandler(kwargs)
            handler.run(callback_func)
        except Exception as e:
            print('=== STEP ERROR INFO START')
            traceback.print_exc()
            print('=== STEP ERROR INFO END')

        logging.getLogger(logger_name).info(f"pid[{os.getpid()}] setup consumer end......\n")

    def start(self, consumers, rabbitmq_config, callback_func):
        """
        对Pool对象调用join()方法会等待所有子进程执行完毕，调用join()之前必须先调用close()，调用close()之后就不能继续添加新的Process了。
        """
        p = Pool(len(consumers))
        # logging.getLogger(logger_name).info("pid[%s] run consumers: %s" % (os.getpid(), consumers))
        for item in consumers:
            item.update({'rabbitmq_config': rabbitmq_config})
            p.apply_async(self.setup_consumer, args=(item, callback_func,))

        p.close()
        p.join()

class ConsumerDispatcherDaemon(Daemon):

    def run(self, dispatcher, consumers, rabbitmq_config, callback_func):
        dispatcher.start(consumers, rabbitmq_config, callback_func)

    def restart(self, dispatcher, consumers, rabbitmq_config, callback_func):
        """
        Restart the daemon
        """
        self.stop()
        self.start(dispatcher, consumers, rabbitmq_config, callback_func)


# TODO:问题, 如何进行流量控制
# TODO: 如果我们想一次只吐一条消息, 当其它消费者连上来时, 还可以并行处理, 简单地把 ack 打开就可以了(默认就是打开的).
# 再考虑一下细节. 当有多个消费者连上时, 它是从队列一次取一条消息, 还是一次取多条消息(这样至少可以改善性能).
# 这可以通过配置 channel 的 qos 相关参数实现
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()
# channel.queue_declare(queue='A')
# channel.basic_qos(prefetch_count=2)

# def callback(ch, method, properties, body):
    # import time
    # time.sleep(10)
    # print body
    # ch.basic_ack(delivery_tag = method.delivery_tag)

# channel.basic_consume(on_message_callback=callback, queue='A', auto_ack=False)
# channel.start_consuming()

# TODO: 提取时进行消息确认
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()
# r = channel.basic_get(queue='A', auto_ack=False) #0
# print r[-1], r[0].delivery_tag
# #channel.basic_ack(delivery_tag=r[0].delivery_tag)
# channel.basic_reject(delivery_tag=r[0].delivery_tag)

# 一次确认多条
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()
# r = channel.basic_get(queue='A', auto_ack=False) #0
# r = channel.basic_get(queue='A', auto_ack=False) #1
# r = channel.basic_get(queue='A', auto_ack=False) #2
# channel.basic_nack(delivery_tag=r[0].delivery_tag, multiple=True)

# import requests
# import json

# def callback(ch, method, properties, body):

    # print " [x] %r" % (body,)
    # # 1. 操作成功, 只要http没有500

    # print "TRACK ================= ", json.loads(body)


    # r = requests.get("http://www.baidu.com")

    # if r.status_code == 200:
        # print "TRACK ================= success"
        # ch.basic_ack(delivery_tag=method.delivery_tag)
    # else:
        # print "TRACK ================= fail"

    # # 2. 操作失败, 这个会导致rabbitmq收到后, 再次将消息发出.....
    # # ch.basic_reject(delivery_tag=method.delivery_tag)

    # # 3. 如果不操作, 那么这个消息将不会消失, 也不会立即分派


# # TODO: consumer变成多进程的
# if __name__ == '__main__':
    # print ' [*] Waiting for logs. To exit press CTRL+C'

    # exchange_name = "INCOME_ACTION"
    # queue_name = "ALL_ACTION"
    # con = Consumer("localhost")

    # con.declare_exchange(exchange_name, durable=True)
    # con.declare_queue(exchange_name, callback, queue_name, routing_key='ACTION.#', durable=True, auto_ack=False)
    # # con.declare_queue(exchange_name, callback, queue_name, routing_key='*', durable=True, auto_ack=False)

    # con.start_consuming()
