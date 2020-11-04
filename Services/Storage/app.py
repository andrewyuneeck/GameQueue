import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from zone1 import Zone1
from zone2 import Zone2
import datetime
import json
import yaml
import os.path
import logging
import logging.config
import requests
import pymysql
from pykafka import KafkaClient, SslConfig
from threading import Thread
from pykafka.common import OffsetType

with open('app_conf.yml', 'r') as f:     
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:     
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
# logging.basicConfig(filename='app.log',
#                     level=logging.INFO)

DB_ENGINE = create_engine('mysql+pymysql://%s:%s@%s:%d/%s' % (app_config["datastore"]["user"],
                                        app_config["datastore"]["password"],
                                        app_config["datastore"]["hostname"],
                                        app_config["datastore"]["port"],
                                        app_config["datastore"]["db"]))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info("Hostname:%s, Port:%d" % (app_config["datastore"]["hostname"], app_config["datastore"]["port"]))


def report_number_player_zone1(body):
    """ Get Zone1 player queue status """

    session = DB_SESSION()

    qone = Zone1(body['player_id'],
                 body['ranking'],
                 body['num_player_total'],
                 body['timestamp'])

    session.add(qone)

    session.commit()
    session.close()
    logger.debug("Stored zone1 player requests with a unique id of %s" % body['player_id'])
    return NoContent, 201

def get_number_player_zone1(timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(timestamp_datetime)

    readings = session.query(Zone1).filter(Zone1.date_created >= timestamp_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Zone 1 players after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200

def report_number_player_zone2(body):
    """ Get Zone2 player queue status """

    session = DB_SESSION()

    qtwo = Zone2(body['player_id'],
                 body['ranking'],
                 body['num_player_total'],
                 body['timestamp'])

    session.add(qtwo)

    session.commit()
    session.close()
    logger.debug("Stored zone2 player requests with a unique id of %s" % body['player_id'])
    return NoContent, 201

def get_number_player_zone2(timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(timestamp_datetime)

    readings = session.query(Zone2).filter(Zone2.date_created >= timestamp_datetime)

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Zone 2 players after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200

def process_messages():
    #Process event messages
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                            app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[app_config["events"]["topic"]]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group='event_group',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "zone1": # Change this to your event type
            report_number_player_zone1(payload)
        elif msg["type"] == "zone2":
            report_number_player_zone2(payload)
        # Commit the new message as being read
        consumer.commit_offsets()




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    tl = Thread(target=process_messages)
    tl.setDaemon(True)
    tl.start()
    app.run(port=8090)
