from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class Zone2(Base):
    """ Zone 2 """

    __tablename__ = "zone2"

    id = Column(Integer, primary_key=True)
    player_id = Column(String(250), nullable=False)
    ranking = Column(String(250), nullable=False)
    num_player_total = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(String(100), nullable=False) 


    def __init__(self, player_id, ranking, num_player_total, timestamp):
        """ Initializes a zone 2 queue status """
        self.player_id = player_id
        self.ranking = ranking
        self.num_player_total = num_player_total
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a zone 2 queue """
        dict = {}
        dict['id'] = self.id
        dict['player_id'] = self.player_id
        dict['ranking'] = self.ranking
        dict['num_player_total'] = self.num_player_total
        dict['timestamp'] = self.timestamp

        return dict