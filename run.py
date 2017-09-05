#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
import time
import logging

import requests
from consumer import Consumer
from consumer import ConsumerHandler
from consumer import ConsumerDispatcherDaemon

from config import CONSUMERS
from config import rabbitmq_config


# logger_name 在 consumer.py里面硬编码了，如果要调试consumer的启动过程，请设置为 rabbit_consumer
logger_name = 'rabbit_consumer'


def _logger_init(logger_name, logger_path, logger_level):
    """
    日志初始化
    """
    formatter = logging.Formatter('[%(asctime)s]-[%(name)s]-[%(levelname)s]:  %(message)s')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)
    fh = logging.FileHandler(logger_path)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def callback_func(ch, method, properties, body):

    """
    回调方法
    """
    params = {"message": body}
    try:
        # if self.http_method == 'GET':
        #     r = requests.get(self.http_url, params=params, timeout=60)
        # elif self.http_method == 'POST':
        #     r = requests.post(self.http_url, data=params, timeout=60)
        # else:
        #     return
        logging.getLogger(logger_name).info("pid[%s] ok: receive - %s" % (os.getpid(), body) )

    except Exception as e:
        # import traceback
        # traceback.print_exc()
        logging.getLogger(logger_name).error("pid[%s] ERROR: exception happend when callback - %s" % (os.getpid(), str(e)) )
    else:
        time.sleep(5)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # logging.getLogger("sms_rabbit_consumer").error("pid[%s] ERROR: http return error url[%s] message[%s]" % (os.getpid(), self.http_url, body))
        # if r.status_code == 200:
            # ch.basic_ack(delivery_tag=method.delivery_tag)
        # else:
        #     logging.getLogger("sms_rabbit_consumer").error("pid[%s] ERROR: http return error url[%s] message[%s]" % (os.getpid(), self.http_url, body))


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print( "ERROR: Wrong options for  run.py [start|stop|restart] DATA_PATH")
        sys.exit(1)

    cmd = sys.argv[1]
    data_dir = sys.argv[2]

    if not os.path.exists(data_dir):
        print( "ERROR: pid_idr [%s] not exists!" % data_dir)
        sys.exit(1)

    pid_path = os.path.join(data_dir, 'consumer_dispatcher.pid')
    log_path = os.path.join(data_dir, 'consumer_dispatcher.log')

    _logger_init(logger_name, log_path, logging.INFO)

    dispatcher = ConsumerDispatcher()
    cdd = ConsumerDispatcherDaemon(pid_path)
    if cmd == "start":
        cdd.start(dispatcher, CONSUMERS, rabbitmq_config, callback_func)
    elif cmd == 'stop':
        cdd.stop()
    elif cmd == 'restart':
        cdd.restart(dispatcher, CONSUMERS, rabbitmq_config, callback_func)
    else:
        print( "run.py [start|stop|restart] DATA_PATH")
        sys.exit(1)


