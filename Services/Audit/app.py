import connexion
from connexion import NoContent
import json
import yaml
import logging
import logging.config
import requests
from pykafka import KafkaClient, SslConfig
from threading import Thread
from pykafka.common import OffsetType

with open('app_conf.yml', 'r') as f:     
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:     
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_number_player_zone1(index):
    """ Get Zone1 Status Stats"""
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=500)
    logger.info("Retrieving Zone1 stats at index %d" % index)
    count = 0
    # zone1_stats = None
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg["type"] == "zone1":
            if count == index:
                zone1_stats = msg["payload"]
                return zone1_stats, 200
            count +=1
        # Find the event at the index you want and
        # return code 200
        # i.e., return event, 200
    logger.error("Could not find Zone1 report at index %d" % index)
    return { "message": "Not Found"}, 404


def get_number_player_zone2(index):
    """ Get Zone2 Status Stats"""
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=500)
    logger.info("Retrieving Zone2 stats at index %d" % index)
    count = 0
    # zone2_stats = None
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        if msg["type"] == "zone2":
            if count == index:
                zone2_stats = msg["payload"]
                return zone2_stats, 200
            count +=1
        # Find the event at the index you want and
        # return code 200
        # i.e., return event, 200
    logger.error("Could not find Zone2 report at index %d" % index)
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
