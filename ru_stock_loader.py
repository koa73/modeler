import logging
from datetime import datetime
import os
import cx_Oracle
import requests
import json
from pathlib import Path

oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']

stage_value = [
    'Login page loaded', 'Logged to site', 'Download form found', 'Download parameters were setted',
    'Download button was clicked']

global db_connect


class CustomError(Exception):
    pass

# Get data from MOEX site
def get_current_value_from_site(ts):
    '''
    resp = requests.get('https://iss.moex.com/iss/engines/stock/markets/shares/boardgroups/57/'
                        'securities.jsonp?iss.meta=off&iss.json=extended&callback=angular.callbacks._s'
                        '&security_collection=3&sort_column=SHORTNAME&sort_order=asc&lang=ru&_=' + ts)
    '''
    resp = requests.get('https://iss.moex.com/iss/history/engines/stock/markets/shares/boardgroups/57/securities.jsonp?' \
    'security_collection=3&date=2021-06-03&start=240&limit=20' \
    '&iss.meta=off&iss.json=extended&callback=angular.callbacks._2c' \
    '&sort_column=VALUE&sort_order=desc&lang=ru&_='+ts)
    if resp:
        #resp_text = resp.text.replace('angular.callbacks._s(', '').replace(')', '')
        resp_text = resp.text.replace('angular.callbacks._2c(', '').replace(')', '')
        #return (json.loads(resp_text)[1])['marketdata']
        return (json.loads(resp_text)[1])['history']

    else:
        print(2)
        raise CustomError('Unsuccessful request code received :' + str(resp.status_code))


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1",
                                     config_dir="/usr/local/src/instantclient_21_1/network/admin")
        connection = cx_Oracle.connect(oracle_login, oracle_password, "db202105041827_tp")
        return connection

    except cx_Oracle.Error as ex:
        logging.info('DB connection Error : ' + str(ex))


def insert_to_db_table(stock_exchange):

    ts = int(datetime.now().timestamp() * 1000)
    rows = get_current_value_from_site(str(ts))

    for row in rows:
        if db_connect:
            # date_rw = datetime.strptime(row['TRADEDATE'], '%d.%m.%Y').strftime('%d-%b-%Y')
            date_rw = '03-JUN-2021'
            #date_rw = datetime.today().strftime('%d-%b-%Y')
            if row['VALUE'] > 0:
                query_1 = "INSERT INTO %s_STOCKS VALUES ('%s', to_date('%s'), %f, %f, %f, %f, %f)" % \
                          (stock_exchange, row['SECID'], date_rw, row['OPEN'], row['HIGH'], row['LOW'], row['CLOSE'],
                           row['VALUE'])
                print(query_1)
                cursor = db_connect.cursor()
                cursor.execute(query_1)
                db_connect.commit()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s', filename=__file__.replace('.py', '.log'),
                        level=logging.INFO)
    db_connect = connect()
    for stock_exchange_name in ['MOEX']:
        try:
            logging.info('----------------- ' + stock_exchange_name + ' start download data ------------------')
            insert_to_db_table(stock_exchange_name)
            logging.info('----------------- Data loaded successfully ------------------')

        except cx_Oracle.Error as ex:
            logging.info('DB Error : ' + str(ex))
            exit(1)

        except Exception as ex:
            logging.info('>> ' + stock_exchange_name + ' : ' + str(ex))
            exit(1)