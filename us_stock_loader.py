import cx_Oracle
import logging
import requests
import os
from pathlib import Path
from datetime import datetime, timedelta

# TwelveDate test script for getting stocks list from exchanges
#
oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']
#oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin"
#oracle_db = "db3_high"
oracle_config_dir = "/usr/local/src/instantclient_21_1/network/admin/clone_db"
oracle_db = "db31c_high"
api_key = os.environ['API_KEY']
log_path = os.environ['LOG_PATH']

exchange_list = ['NYSE', 'NASDAQ', 'AMEX']
exchange = {'NYSE': 'XNYS', 'NASDAQ': 'XNAS', 'AMEX': 'XASE'}
# , 'NYSE ARCA':'ARCX'}
exchange_key = dict((v, k) for k, v in exchange.items())

stock_type_list = ['CS', 'PFD']
ticker_list = {}


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1", config_dir=oracle_config_dir)
        connection = cx_Oracle.connect(oracle_login, oracle_password, oracle_db)
        return connection

    except cx_Oracle.Error as ex:
        print(ex)
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
        return False
        # logging.info('DB Error : '+str(ex))


def insert_to_db_table(bars):
    try:
        count = 0
        for row in bars:
            if db_connect:
                '''
                query = "INSERT INTO %s_STOCKS VALUES ('%s', to_date('%s'), %f, %f, %f, %f, %f)" % \
                        (row['ex'], row['T'], datetime.fromtimestamp(row['t'] / 1000).strftime('%d-%b-%Y'), row['o'],
                         row['h'], row['l'], row['c'], row['v'])
                '''
                query = "CALL INSERT_INTO_STOCKS('%s_STOCKS','%s', to_date('%s'), %f, %f, %f, %f, %f)" % \
                        (row['ex'], row['T'], datetime.fromtimestamp(row['t'] / 1000).strftime('%d-%b-%Y'), row['o'],
                         row['h'], row['l'], row['c'], row['v'])

                cursor = db_connect.cursor()
                cursor.execute(query)
                db_connect.commit()
            count += 1
            print(row['ex'])
        if len(bars) == count:
            return "Successful complete. All " + str(count) + " was inserted to DB."
        else:
            return "Not good result. Was inserted " + str(count) + " rows."
    except cx_Oracle.Error as ex:
        logging.info('DB Error : ' + str(ex))
        exit(1)


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
            print(stock_exchange_name, end=", ")
            print(stock_type)
            output = get_tickers(stock_exchange_name, stock_type)
            if len(output) == 0:
                logging.info("----- Error : " + stock_exchange_name + " didn't receive tickers ----")
            count = 0
            for row in output:
                result[row['ticker']] = exchange_key[row['primary_exchange']]
                if 'type' in row:
                    if insert_to_dictionary(exchange_key[row['primary_exchange']], row['ticker'],row['name'],row['type']):
                        count += 1
            if count > 0:
                logging.info('Into dictionary ' + stock_exchange_name + ' was inserted %s rows' % count)
    return result


def get_tickers_from_db(t_type):
    try:
        if db_connect:
            query = f"SELECT trim(a.symbol), 'NASDAQ' t from nasdaq_dict a WHERE type = '{t_type}' " \
                    "UNION SELECT trim(b.symbol),'NYSE' FROM nyse_dict b WHERE type = '{t_type}' " \
                    "UNION SELECT trim(c.symbol), 'AMEX' FROM amex_dict c WHERE type = '{t_type}'"\
                .format(t_type=t_type)

            cursor = db_connect.cursor()
            cursor.execute(query)

            query_resp = cursor.fetchall()
            result = {}
            for row in query_resp:
                result[row[0]]=row[1]
            logging.info('Received ' + str(len(result)) + ' tickers from DB ')
            return result

    except cx_Oracle.Error as ex:
        logging.info('get_tickers_from_db : ' + str(ex))


def get_daily_bars(date):
    url = "https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date}?adjusted=true&apiKey={key}" \
        .format(date=date, key=api_key)
    r = requests.get(url)
    data = r.json()
    if data['status'] == 'OK' or data['status'] == 'DELAYED':
        result = []
        for row in data['results']:
            if row['T'] in ticker_list:
                row['ex'] = ticker_list[row['T']]
                result.append(row)
        return result
    else:
        return []


def get_current_date(offset=0):
    return (datetime.today() + timedelta(offset)).strftime('%Y-%m-%d')


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        filename=log_path + Path(__file__).stem + '.log',
                        level=logging.INFO)
    db_connect = connect()
    #ticker_list = get_tickers_list()
    ticker_list = []
    if len(ticker_list) == 0:
        ticker_list = get_tickers_from_db(stock_type_list[0])

    #logging.info('%d Tickers for getting data'%len(ticker_list))

    # Set date offset if necessary
    bars = get_daily_bars(get_current_date(-1))
    if len(bars) > 0:
        result_str = insert_to_db_table(bars)
        logging.info(result_str)
    else:
        logging.info('>> Unsuccessful result. Bars data is empty')
        exit(1)

