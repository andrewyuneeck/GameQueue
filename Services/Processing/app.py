import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import yaml
import os.path
import logging
import logging.config
import requests
import pymysql
from apscheduler.schedulers.background import BackgroundScheduler

with open('app_conf.yml', 'r') as f:     
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:     
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

BASE_URL = app_config["eventstore"]["url"]
DATA_FILE = app_config["datastore"]["filename"]
DEFAULT_STATS = {"num_requests_zone1": 0, "num_requests_zone2": 0, "num_most_players_rank_zone1": 0, "num_most_players_rank_zone2": 0, "timestamp": "2020-10-15T14:58:38Z"}


def populate_stats():
    # periodically update stats
    logger.info("Periodically update stats")

    datetime_string = datetime.now()
    now = datetime_string.strftime("%Y-%m-%dT%H:%M:%SZ")

    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                stats = json.loads(f.read())
                last_datetime = stats["timestamp"]
                requests_zone1_date = requests.get(BASE_URL + "/queue/zone1?timestamp=" + last_datetime)
                requests_zone1 = requests_zone1_date.json()
                requests_zone2_date = requests.get(BASE_URL + "/queue/zone2?timestamp=" + last_datetime)
                requests_zone2 = requests_zone2_date.json()
                num_requests_zone1 = len(requests_zone1)
                num_requests_zone2 = len(requests_zone2)
                total_requests = num_requests_zone1 + num_requests_zone2
                logger.info(f"{total_requests} requests received!")

                if num_requests_zone1 != 0:
                    zone1_ranking = [i["ranking"] for i in requests_zone1]
                    num_bronze_zone1 = zone1_ranking.count("Bronze")
                    num_silver_zone1 = zone1_ranking.count("Silver")
                    num_gold_zone1 = zone1_ranking.count("Gold")
                    num_platinum_zone1 = zone1_ranking.count("Platinum")
                    num_diamond_zone1 = zone1_ranking.count("Diamond")
                    num_master_zone1 = zone1_ranking.count("Master")
                    rank_layer_zone1 = [num_bronze_zone1, num_silver_zone1, num_gold_zone1, num_platinum_zone1, num_diamond_zone1, num_master_zone1]
                    stats["num_most_players_rank_zone1"] = max(rank_layer_zone1)
                    stats["num_requests_zone1"] += num_requests_zone1
                
                if num_requests_zone2 != 0:
                    zone2_ranking = [i["ranking"] for i in requests_zone2]
                    num_bronze_zone2 = zone2_ranking.count("Bronze")
                    num_silver_zone2 = zone2_ranking.count("Silver")
                    num_gold_zone2 = zone2_ranking.count("Gold")
                    num_platinum_zone2 = zone2_ranking.count("Platinum")
                    num_diamond_zone2 = zone2_ranking.count("Diamond")
                    num_master_zone2 = zone2_ranking.count("Master")
                    rank_layer_zone2 = [num_bronze_zone2, num_silver_zone2, num_gold_zone2, num_platinum_zone2, num_diamond_zone2, num_master_zone2]
                    stats["num_most_player_rank_zone2"] = max(rank_layer_zone2)
                    stats["num_requests_zone2"] += num_requests_zone2
                
                stats["timestamp"] = now

                with open(DATA_FILE, "w") as f:
                    f.write(json.dumps(stats))
                    logger.debug(f"Stats: {stats}")
            except:
                logger.error("Error!")
    else:
        with open(DATA_FILE, "w") as f:
            f.write(json.dumps(DEFAULT_STATS))
            logger.debug("Stats: {DEFAULT_STATS}")
    logger.info("End of Periodic stats")

def get_stats():
    logger.info("Getting API")
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            stats = json.loads(f.read())
            logger.debug(f"stats: {stats}")
            logger.info("The request has completed")
            return stats, 200
    else:
        logger.error("data.json does not exist")
        return "Statistics do not exist", 404


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
     # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)