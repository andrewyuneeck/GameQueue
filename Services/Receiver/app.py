import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
import datetime
import json
import yaml
import os.path
import logging
import logging.config
import requests
from pykafka import KafkaClient, SslConfig


with open('app_conf.yml', 'r') as f:     
    app_config = yaml.safe_load(f.read())
    url1 = app_config["zone1"]["url"]
    url2 = app_config["zone2"]["url"]
    hostname = app_config["events"]["hostname"]
    port = str(app_config["events"]["port"])
    config_topic = app_config["events"]["topic"]
    keys = list(app_config.keys())

with open('log_conf.yml', 'r') as f:     
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
# logging.basicConfig(filename='app.log',
#                     level=logging.INFO)
# MAX_EVENT = 10
# events = []

def report_number_player_zone1(body):

    # url = app_config["eventstore"]["url"]+"/queue/zone1"
    # headers = {'Content-type': 'application/json'}
    zone1_player_id = body["player_id"]
    logger.info(f"Received event zone1 request with a unique id  of {zone1_player_id}")
    # r = requests.post(url, json=body, headers=headers)

    client = KafkaClient(hosts=hostname+":"+port)
    topic = client.topics[config_topic]
    producer = topic.get_sync_producer()
    msg = { "type": "zone1",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body
            }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event zone1 response with player id {zone1_player_id}")
    

    return NoContent, 201

def report_number_player_zone2(body):

    # url = app_config["eventstore"]["url"]+"/queue/zone2"
    # headers = {'Content-type': 'application/json'}
    zone2_player_id = body["player_id"]
    logger.info(f"Received event zone2 request with a unique id  of {zone2_player_id}")
    # r = requests.post(url, json=body, headers=headers)

    client = KafkaClient(hosts=hostname+":"+port)
    topic = client.topics[config_topic]
    producer = topic.get_sync_producer()
    msg = { "type": "zone2",
            "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body
            }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info("Returned event zone2 response with player id {zone2_player_id}")
    

    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
