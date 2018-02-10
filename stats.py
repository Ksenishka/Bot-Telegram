import sqlite3
from datetime import datetime

class SimpleDbManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.table = "actions"

    def __del__(self):
        self.conn.close()

    def initialize(self):
        c = self.conn.cursor()
        c.execute(
        """
        CREATE TABLE IF NOT EXISTS {}(user text, time datetime, category text, subcategory text)
        """.format(self.table)
        )
        self.conn.commit()

    def add_record(self, user, category, subcategory=""):
        dt = datetime.now()
        c = self.conn.cursor()
        c.execute(
        """
        INSERT INTO {} VALUES('{}', '{}', '{}', '{}')
        """.format(self.table, user, dt, category, subcategory))
        self.conn.commit()

sent_msg = 0
def update_sent_msg():
    global sent_msg
    sent_msg += 1
    print('sent_msg={}'.format(sent_msg))

drop_msg = 0
def update_drop_msg():
    global drop_msg
    drop_msg += 1
    print('drop_msg={}'.format(drop_msg))
