import logging
import sys
import time
import os
import cx_Oracle
import csv

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

service_login = os.environ['SERVICE_LOGIN']
service_password = os.environ['SERVICE_PASSWORD']
oracle_login = os.environ['ORACLE_LOGIN']
oracle_password = os.environ['ORACLE_PASSWORD']

stage_value = [
    'Login page loaded', 'Logged to site', 'Download form found', 'Download parameters were setted',
    'Download button was clicked']

global db_connect


def wait_for_downloads(download_path):

    max_delay = 30
    interval_delay = 0.5
    total_delay = 0
    file = ''
    done = False
    while not done and total_delay < max_delay:
        files = [f for f in os.listdir(download_path) if f.endswith('.crdownload')]
        if not files and len(file) > 1:
            done = True
        if files:
            file = files[0]
        time.sleep(interval_delay)
        total_delay += interval_delay
    if not done:
        logging.error("File(s) couldn't be downloaded")
        return ""
    else:
        return download_path + '/' + file.replace(".crdownload", "")


# Get cvv file with end of day data
def get_file(stock_exchange_name,  end_date:str = None) -> str:

    url_path = 'http://www.eoddata.com/products/services.aspx'
    download_path = '/home/oleg/PycharmProjects/modeler/download'

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')
    options.add_experimental_option("prefs", {"download.default_directory": download_path})
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("window-size=1920,1080")
    options.add_argument("--blink-settings=imagesEnabled=false")
    #driver = webdriver.Chrome(options=options)

    driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub',
                              desired_capabilities=options.to_capabilities())

    stage = 0  # Login page loaded

    try:

        stock_exchange_dict = {
            'NYSE': "New York Stock Exchange",
            'NASDAQ': "NASDAQ Stock Exchange"
        }

        driver.get(url_path)
        login_form = driver.find_element_by_id('aspnetForm')

        if login_form is not None:

            driver.find_element_by_id('ctl00_cph1_ls1_txtEmail').send_keys(service_login)
            driver.find_element_by_id('ctl00_cph1_ls1_txtPassword').send_keys(service_password)
            driver.find_element_by_id('ctl00_cph1_ls1_btnLogin').click()

            stage += 1  # Logged to site
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'ctl00_cph1_ls1_lnkLogOut')))

            driver.get(url_path)

            stage += 1  # Download form found
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'ctl00_cph1_dd1_cboExchange')))

            stage += 1  # Download parameters were setted
            Select(driver.find_element_by_id('ctl00_cph1_dd1_cboExchange')). \
                select_by_visible_text(stock_exchange_dict[stock_exchange_name])
            Select(driver.find_element_by_id('ctl00_cph1_dd1_cboDataFormat')).select_by_visible_text("Standard CSV")
            Select(driver.find_element_by_id('ctl00_cph1_dd1_cboPeriod')).select_by_visible_text("End of Day")

            if end_date is not None:
                driver.find_element_by_id('ctl00_cph1_dd1_txtEndDate').clear()
                time.sleep(1)
                driver.find_element_by_id('ctl00_cph1_dd1_txtEndDate').click()
                driver.find_element_by_id('ctl00_cph1_dd1_txtEndDate').send_keys(end_date)

            stage += 1  # Download button was clicked
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'ctl00_cph1_dd1_btnDownload'))).click()
            time.sleep(1)
            downloaded_file = wait_for_downloads(download_path)

            logging.info(stage_value[0])
            return downloaded_file

        else:
            logging.info('--> Unsuccessful result')

    except Exception as ex:
        logging.info('Cancelled on stage : "' + stage_value[stage] + '", reason : ' + str(ex))

    return ""


def connect():
    try:
        cx_Oracle.init_oracle_client(lib_dir="/usr/local/src/instantclient_21_1",
                                 config_dir="/usr/local/src/instantclient_21_1/network/admin")
        connection = cx_Oracle.connect(oracle_login, oracle_password, "db202105041827_tp")
        return connection

    except cx_Oracle.Error as ex:
        logging.info('DB connection Error : '+str(ex))


def insert_to_db_table(file_name, stock_exchange):

    try:
        with open(file_name, newline='') as f:
            rows = csv.DictReader(f, delimiter=',', quotechar='|')
            for row in rows:
                if db_connect:
                    query = "INSERT INTO %s_STOCKS VALUES ('%s', to_date('%s'), %f, %f, %f, %f, %f)" % \
                            (stock_exchange, row['Symbol'], row['Date'], float(row['Open']), float(row['High']),
                             float(row['Low']), float(row['Close']), float(row['Volume']))

                    print(query)
                    #cursor = db_connect.cursor()
                    #cursor.execute(query)
                    #db_connect.commit()
            f.close()

    except FileNotFoundError:
        logging.info("Can't read received file : "+file_name)

    except cx_Oracle.Error as ex:
        logging.info('DB Error : '+str(ex))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s', filename='/var/log/'+Path(__file__).stem+'.log',
                        level=logging.INFO)
    db_connect = connect()
    for stock_exchange_name in ['NYSE']:
        try:
            logging.info('----------------- ' + stock_exchange_name + ' start download data ------------------')
            while True:
                #received_file = get_file(stock_exchange_name, '06/01/2021')
                received_file = get_file(stock_exchange_name)
                #received_file = './download/'+stock_exchange_name+'_20210604.csv'
                if "".__eq__(received_file):
                    print('Unsuccessful result')
                    logging.info('>> ' + stock_exchange_name + ' Unsuccessful result')
                else:
                    insert_to_db_table(received_file, stock_exchange_name)
                    os.remove(received_file)
                    break
        except Exception as ex:
            logging.info('>> ' + stock_exchange_name + ' : ' + str(ex))


