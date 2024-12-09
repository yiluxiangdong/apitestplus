# -*- encoding:utf-8 -*-
#E:\sunwoda\common\kafkaUtil.py
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from common.commomUtil import read
kafkaconf = read(r'../config/base.yaml')['db_kafka']
bootstrap_servers = [f'{kafkaconf["host"]}:{kafkaconf["port"]}']
class kafkaUtil:
    def __init__(self,topic):
        self.topic = topic


    def consumers(self):
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        for i in range(10):
            message = 'Message {}'.format(i)
            future = self.producer.send(self.topic, bytes(message, 'utf-8'))
            try:
                record_metadata = future.get(timeout=10)
                print('Message {} sent to partition {} with offset {}'.format(message, record_metadata.partition,
                                                                              record_metadata.offset))
            except KafkaError as e:
                print('Failed to send message {}: {}'.format(message, e))

        self.consumer = KafkaConsumer(self.topic, bootstrap_servers=bootstrap_servers, auto_offset_reset='earliest',
                                 enable_auto_commit=True, group_id='my-group', max_poll_records=10)

        while True:
            messages = self.consumer.poll(timeout_ms=1000)
            if not messages:
                continue
            for topic_partition, records in messages.items():
                for record in records:
                    print(record.value.decode('utf-8'))

    def __del__(self):
        self.producer.close()
        self.consumer.close()



if __name__ == '__main__':
    kfk = kafkaUtil('mytest')
    kfk.consumers()

