import cx_Oracle
import logging
import requests
import os
from pathlib import Path

# TwelveDate test script for getting stocks list from exchanges
#
oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']
oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin"
oracle_db = "db3_high"
#oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin/clone_db"
#oracle_db = "db31c_high"
api_key = os.environ['API_KEY']
log_path = os.environ['LOG_PATH']

exchange_list = ['NYSE', 'NASDAQ', 'AMEX']
exchange = {'NYSE': 'XNYS', 'NASDAQ': 'XNAS', 'AMEX': 'XASE'}
exchange_key = dict((v, k) for k, v in exchange.items())

stock_type_list = ['CS', 'PFD']
ticker_list = {}


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1", config_dir=oracle_config_dir)
        connection = cx_Oracle.connect(oracle_login, oracle_password, oracle_db)
        return connection

    except cx_Oracle.Error as ex:
        logging.info('DB connection Error : ' + str(ex))


def insert_to_dictionary(exchange, ticker, name, type):
    try:
        if db_connect:
            query = "INSERT INTO %s_DICT VALUES ('%s','%s','%s')" % \
                    (exchange, ticker, name.replace("'", "''"), type)
            cursor = db_connect.cursor()
            cursor.execute(query)
            db_connect.commit()
            return True
    except cx_Oracle.Error as ex:
        #logging.info('DB Error : '+str(ex))
        return False

# Get all tickers hat meet the condition (type & exchange)
def get_tickers(exchange_name, t_type):
    result = []

    try:
        url = 'https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&type={type}' \
              '&sort=ticker&order=asc&limit=1000&apiKey={key}&exchange={name}' \
            .format(name=exchange[exchange_name], key=api_key, type=t_type)

        while True:
            r = requests.get(url)
            data = r.json()
            if data['status'] == 'OK':
                result = result + data['results']
                if 'next_url' in data:
                    url = data['next_url'] + '&apiKey={key}'.format(key=api_key)
                else:
                    break

        return result

    except Exception as ex:
        logging.info('>> Unsuccessful request of ticker list from service.')
        return []


# Prepare dictionary for tickers with link to exchange name
def get_tickers_list():
    result = {}
    for stock_exchange_name in exchange_list:
        for stock_type in stock_type_list:
            output = get_tickers(stock_exchange_name, stock_type)
            if len(output) == 0:
                logging.info("----- Error : " + stock_exchange_name + " didn't receive tickers ----")
            else:
                logging.info("Received for %s %s tickers of type %s" % (stock_exchange_name, len(output), stock_type))
            count = 0

            for row in output:
                result[row['ticker']] = exchange_key[row['primary_exchange']]
                if 'type' in row:
                    if insert_to_dictionary(exchange_key[row['primary_exchange']], row['ticker'],row['name'],row['type']):
                        count += 1
            if count > 0:
                logging.info('Into dictionary ' + stock_exchange_name + ' was inserted %s rows' % count)
            else:
                logging.info('No one new ticker was loaded to dictionary.')



if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        filename=log_path + Path(__file__).stem + '.log',
                        level=logging.INFO)
    try:
        db_connect = connect()
        get_tickers_list()
    except Exception as ex:
        logging.info("Unsuccessful complete by reason : "+str(ex))

