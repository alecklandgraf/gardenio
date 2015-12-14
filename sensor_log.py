from datetime import datetime
from elasticsearch_dsl import DocType, String, Date, Integer, Float
from elasticsearch_dsl.connections import connections

# Define a default Elasticsearch client
connections.create_connection(hosts=['192.168.1.122:9876'])

WEEKDAYS = ('Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun')

class SensorLog(DocType):
    sensor_name = String(index='not_analyzed')
    temperature = Float()
    moisture = Integer()
    light = Integer()
    timestamp = Date()
    # timeparts for fast queries and aggs later, calculated during save
    day_of_week = String(index='not_analyzed')  # Mon-Fri
    day_of_year = Integer() # 1-366
    day_of_month = Integer() # 1-31
    week_of_year = Integer()  # 1-53
    month = Integer()  # 1-12 === Jan-Dec
    year = Integer()
    hour = Integer()
    minute = Integer()

    class Meta:
        index = 'sensor_log'

    def save(self, ** kwargs):
        self.day_of_week = WEEKDAYS[self.timestamp.weekday()]
        self.day_of_year = self.timestamp.timetuple().tm_yday
        self.day_of_month = self.timestamp.day
        self.week_of_year = self.timestamp.isocalendar()[1]
        self.month = self.timestamp.month
        self.year = self.timestamp.year
        self.hour = self.timestamp.hour
        self.minute = self.timestamp.minute
        return super(SensorLog, self).save(** kwargs)

    def is_published(self):
        return datetime.now() < self.published_from

# create the mappings in elasticsearch
def create_index():
    SensorLog.init()
