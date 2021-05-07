import logging
import time
import os

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime

service_login = os.environ['SERVICE_LOGIN']
service_password = os.environ['SERVICE_PASSWORD']

stage_value = [
    'Login page loaded', 'Logged to site', 'Download form found', 'Download parameters were setted',
    'Download button was clicked']


def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var elements = document.querySelector('downloads-manager')
        .shadowRoot.querySelector('#downloadsList')
        .items
        if (elements.every(e => e.state === 'COMPLETE'))
        return elements.map(e => e.filePath || e.file_path || e.fileUrl || e.file_url);
        """)


# Get cvv file with end of day data
def get_file(end_Date) -> str:
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')
    options.add_experimental_option("prefs",
                                    {"download.default_directory": "/home/oleg/PycharmProjects/modeler/download"})
    #options.add_argument('--headless')
    #options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    stage = 0  # Login page loaded
    file_path = ''
    try:
        driver.get('http://www.eoddata.com/products/services.aspx')
        login_form = driver.find_element_by_id('aspnetForm')

        if login_form is not None:

            driver.find_element_by_id('ctl00_cph1_ls1_txtEmail').send_keys(service_login)
            driver.find_element_by_id('ctl00_cph1_ls1_txtPassword').send_keys(service_password)
            driver.find_element_by_id('ctl00_cph1_ls1_btnLogin').click()

            stage += 1  # Logged to site
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'ctl00_cph1_ls1_lnkLogOut')))

            driver.get('http://www.eoddata.com/products/services.aspx')

            stage += 1  # Download form found
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'ctl00_cph1_dd1_cboExchange')))

            stage += 1  # Download parameters were setted
            Select(driver.find_element_by_id('ctl00_cph1_dd1_cboExchange')). \
                select_by_visible_text("New York Stock Exchange")
            Select(driver.find_element_by_id('ctl00_cph1_dd1_cboDataFormat')).select_by_visible_text("Standard CSV")
            Select(driver.find_element_by_id('ctl00_cph1_dd1_cboPeriod')).select_by_visible_text("End of Day")
            end_date = driver.find_element_by_id('ctl00_cph1_dd1_txtEndDate')
            end_date.clear()
            end_date.send_keys(end_Date)

            time.sleep(10)
            stage += 1  # Download button was clicked
            driver.find_element_by_id('ctl00_cph1_dd1_btnDownload').click()
            time.sleep(100)
            file_path = WebDriverWait(driver, 10).until(every_downloads_chrome)

            logging.info(stage_value[0])
        else:
            logging.info('Unsuccess result')

    except Exception as e:
        logging.info('Cancelled on stage : "' + stage_value[stage] + '", reason : ' + str(e))

    finally:
        return file_path


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s', filename='us_stock_loaded.log',
                        level=logging.INFO)
    # get_file(str(datetime.today().strftime("%d/%m/%Y")))
    file_path = get_file('05/05/2021')
    print(file_path)
