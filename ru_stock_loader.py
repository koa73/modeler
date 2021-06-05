import logging
from datetime import datetime
import os
import cx_Oracle
import csv

service_login = os.environ['SERVICE_LOGIN']
service_password = os.environ['SERVICE_PASSWORD']
oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']

stage_value = [
    'Login page loaded', 'Logged to site', 'Download form found', 'Download parameters were setted',
    'Download button was clicked']

global db_connect


# Get cvv file with end of day data
def get_file(stock_exchange_name, end_date: str = None) -> str:
    downloaded_file = './download/eod-equities.csv'
    return downloaded_file


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1",
                                     config_dir="/usr/local/src/instantclient_21_1/network/admin")
        connection = cx_Oracle.connect(oracle_login, oracle_password, "db202105041827_tp")
        return connection

    except cx_Oracle.Error as ex:
        logging.info('DB connection Error : ' + str(ex))


def insert_to_db_table(file_name, stock_exchange):
    try:
        with open(file_name, newline='', encoding="cp1251", errors='ignore') as f:
            rows = csv.DictReader(f, delimiter=';', quotechar='|')
            for row in rows:
                if db_connect:
                    if row['BOARDID'] == 'TQBR' and int(row['VOLUME']) > 0:
                        date_rw = datetime.strptime(row['TRADEDATE'], '%d.%m.%Y').strftime('%d-%b-%Y')

                        query_1 = "INSERT INTO %s_STOCKS VALUES ('%s', to_date('%s'), %f, %f, %f, %f, %f)" % \
                                (stock_exchange, row['SECID'], date_rw, float(row['OPEN'].replace(',','.')),
                                 float(row['HIGH'].replace(',','.')), float(row['LOW'].replace(',','.')),
                                 float(row['CLOSE'].replace(',','.')), float(row['VOLUME'].replace(',','.')))
                        query_2 = "INSERT INTO %s_DICT VALUES ('%s', '%s')" % \
                                (stock_exchange, row['SECID'], row['SHORTNAME'])

                        print(query_2)

                        cursor = db_connect.cursor()
                        cursor.execute(query_1)
                        db_connect.commit()
            f.close()

    except FileNotFoundError:
        logging.info("Can't read received file : " + file_name)

    except cx_Oracle.Error as ex:
        logging.info('DB Error : ' + str(ex))

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s', filename=__file__.replace('.py', '.log'),
                        level=logging.INFO)
    db_connect = connect()
    for stock_exchange_name in ['MOEX']:
        try:
            logging.info('----------------- ' + stock_exchange_name + ' start download data ------------------')
            while True:
                received_file = get_file(stock_exchange_name)
                if "".__eq__(received_file):
                    print('Unsuccessful result')
                    logging.info('>> ' + stock_exchange_name + ' Unsuccessful result')
                else:
                    insert_to_db_table(received_file, stock_exchange_name)
                    #os.remove(received_file)
                    break
        except Exception as ex:
            logging.info('>> ' + stock_exchange_name + ' : ' + str(ex))
