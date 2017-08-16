# rabbitmq-http-dispatcher

An simple consumer, dispatch messages to http server.

First, it's a daemon, read `config.py` and start a lot of consumers.

Then, each consumer get message from rabbitmq, dispatch to a http api, and get http response, read the status code to decide if it's necessary send `ack` to rabbitmq.

```

    MQ    ->    http-dispatcher   ->    http api

```


# dependency

1. pika
2. the `daemon.py` is from [python-daemon](https://github.com/serverdensity/python-daemon) and make a little change.
   thanks to serverdensity

# 支持Python3了
调整了些代码，在Python3.6下面能够抱起来了
```
pip3 install requests
pip3 install pika
pip3 install psutil

// 修改一些配置之后
python3 run.py start ./logs > ./logs/process.log
python3 run.py stop ./logs > ./logs/process.log
```



