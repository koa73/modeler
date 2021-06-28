import cx_Oracle
import sqlite3
import uuid
import os
import logging
from datetime import datetime
from pathlib import Path


oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']
#oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin/clone_db"
oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin"
#oracle_db = "db202106201548_tp"
oracle_db = "db202106200141_tp"
archive_db = os.environ['ARCHIVE_DB']


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1", config_dir=oracle_config_dir)
        connection = cx_Oracle.connect(oracle_login, oracle_password, oracle_db)
        return connection

    except cx_Oracle.Error as ex:
        print(ex)
        logging.info('DB connection Error : ' + str(ex))


def get_archive_date():
    try:
        if db_connect:
            query = "SELECT trim(a.symbol), trim(ex_name), ((a.date_rw - DATE '1970-01-01')*24*60*60), a.pwr, a.last, " \
                    "((a.exp_date - DATE '1970-01-01')*24*60*60), a.open, a.high, a.low, a.close, a.volume, a.type " \
                    "FROM archive a WHERE a.moved = 0"
            cursor = db_connect.cursor()
            cursor.execute(query)
            query_resp = cursor.fetchall()
            return query_resp

    except cx_Oracle.Error as ex:
        logging.info('Get archive data error : ' + str(ex))
        exit(1)


def move_data_to_sqlite_db(row, table_name='history_model3'):
    try:
        cur = conn.cursor()
        query = "INSERT INTO %s VALUES ('%s', '%s', %d, %d, %f, %d, %f, %f, %f, %f, %d, '%s', '%s')" \
                %(table_name, row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8], row[9], row[10],
                  uuid.uuid5(uuid.NAMESPACE_DNS, row[0]+str(row[2])), row[11])
        cur.execute(query)
        conn.commit()
        cur.close()
        return True

    except sqlite3.Error as ex:
        logging.info('Access to Sqlite DB error : ' + str(ex))
        return False


def check_data_as_mived(symbol, date_rw):

    try:
        if db_connect:
            query = "UPDATE archive SET moved=1 WHERE symbol = '%s' " \
                    "AND date_rw='%s'" % (symbol, datetime.fromtimestamp(date_rw).strftime('%d-%b-%Y'))
            cursor = db_connect.cursor()
            cursor.execute(query)
            db_connect.commit()

    except cx_Oracle.Error as ex:
        logging.info("Can't check moved data : " + str(ex))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        filename='./log/' + Path(__file__).stem + '.log',
                        level=logging.INFO)
    db_connect = connect()
    conn = sqlite3.connect(archive_db)
    data = get_archive_date()
    count = len(data)
    for row in data:
        if move_data_to_sqlite_db(row):
            check_data_as_mived(row[0], row[2])
            count -= 1

    if count == 0:
        logging.info("All %d rows was moved."%len(data))
    else:
        logging.info("--- Error %d rows didn't moved to sqlite db" % count)




