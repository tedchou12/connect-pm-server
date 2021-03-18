import mysql.connector
from .config import config

class db :
    def __init__(self) :
        obj_config = config()
        self.config = {'host': obj_config.params['mysql_host'],
                       'user': obj_config.params['mysql_user'],
                       'pass': obj_config.params['mysql_pass'],
                       'port': obj_config.params['mysql_port'],
                       'db'  : obj_config.params['mysql_db']}
        self.cnx = mysql.connector.connect(user=self.config['user'], port=self.config['port'], password=self.config['pass'], host=self.config['host'], database=self.config['db'])

    def select(self, query, data) :
        cursor = self.cnx.cursor()

        cursor.execute(query, data)
        # print(cursor.statement)
        columns = [column[0] for column in cursor.description]
        list = []
        for obj in cursor.fetchall() :
            row = {}
            counter = 0
            for item in obj :
                row[columns[counter]] = item
                counter = counter + 1
            list.append(row)

        cursor.close()
        # cnx.close()

        return list

    def insert(self, query, data) :
        cursor = self.cnx.cursor()

        cursor.execute(query, data)
        self.cnx.commit()
        cursor.close()
        # cnx.close()

        return cursor.lastrowid

    def update(self, query, data) :
        cursor = self.cnx.cursor()

        cursor.execute(query, data)
        self.cnx.commit()
        cursor.close()
        # cnx.close()

        return True

    def delete(self, query, data) :
        cursor = self.cnx.cursor()

        cursor.execute(query, data)
        self.cnx.commit()
        cursor.close()
        # cnx.close()

        return True
