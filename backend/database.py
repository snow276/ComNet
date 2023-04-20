import pymysql as mysql
import yaml
import json
from logger import Logger
import re
from utils import trilateration, smooth_avg

class MySQLDatabase():
    def __init__(self, args, logger) -> None:
        self.args = args
        self.logger = logger

    def connect(self):
        self.db = mysql.connect(host=self.args['host'], user=self.args['user'], passwd=self.args['passwd'], db=self.args['db'])
        self.cursor = self.db.cursor()
        self.logger.log(f"Connected to database {self.args['db']}")
        
    def close(self):
        self.logger.log(f"Closed connection to database {self.args['db']}")
        self.db.close()
        
    def table_exists(self, table_name):
        sql = "show tables;"
        self.cursor.execute(sql)
        tables = [self.cursor.fetchall()]
        table_list = re.findall('(\'.*?\')',str(tables))
        table_list = [re.sub("'",'',each) for each in table_list]
        if table_name in table_list:
            return True
        else:
            return False

    def create_table(self, inplace=True):
        if not inplace: # 不重写表
            if self.table_exists(self.args['table']):
                self.logger.log(f"Table {self.args['table']} already exists")
                return
            
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.args['table']}")
        
        VARCHAR = "VARCHAR(100)"
        sql = f"""CREATE TABLE {self.args['table']} (
                ID {VARCHAR} NOT NULL,
                MMAC {VARCHAR} NOT NULL,
                RATE {VARCHAR},  
                TIME {VARCHAR},
                LAT {VARCHAR},
                LON {VARCHAR},
                MAC {VARCHAR},
                RSSI {VARCHAR},
                RNG {VARCHAR} NOT NULL,
                RSSI1 {VARCHAR},
                RSSI2 {VARCHAR},
                RSSI3 {VARCHAR},
                RSSI4 {VARCHAR},
                RSSI5 {VARCHAR} )""" # RNG is for RANGE (RANGE is a reserved word)
            
        self.cursor.execute(sql)
        self.logger.log(f"Table {self.args['table']} created")
    
    def filter_insert(self, json_data, mmac):
        if json_data['mmac'] != mmac:
            return
        sql = f"""INSERT INTO {self.args['table']} (ID, MMAC, RATE, TIME, LAT, LON , MAC, RSSI, RNG, RSSI1, RSSI2, RSSI3, RSSI4, RSSI5) \
            VALUES ({json_data['id']}, {json_data['mmac']}, {json_data['rate']}, {json_data['time']}, {json_data['lat']}, {json_data['lon']}, {json_data['mac']}, {json_data['rssi']}, {json_data['range']}, {json_data['rssi1']}, {json_data['rssi2']}, {json_data['rssi3']}, {json_data['rssi4']}, {json_data['rssi5']});"""
        self.logger.log(f"Inserting data into {self.args['table']}: {sql}")
        self.cursor.execute(sql)
        self.db.commit()
        # TODO: add utility functions (may support real-time localization)
        
        
    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def execute(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
    
    
if __name__ == "__main__":
    logger = Logger()
    with open("../config.yml", 'r') as stream:
        try:
            args = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.echo(exc)
    
    database = MySQLDatabase(args, logger)
    database.create_table()