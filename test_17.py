import os
from datetime import datetime
import requests
import json


class CustomError(Exception):
    pass


def get_current_value_from_site(ts):

    resp = requests.get('https://iss.moex.com/iss/engines/stock/markets/shares/boardgroups/57/'
                        'securities.jsonp?iss.meta=off&iss.json=extended&callback=angular.callbacks._s'
                        '&security_collection=3&sort_column=SHORTNAME&sort_order=asc&lang=ru&_=' + ts)
    if resp:
        resp_text = resp.text.replace('angular.callbacks._s(', '').replace(')', '')
        return (json.loads(resp_text)[1])['marketdata']

    else:
        raise CustomError('Unsuccessful request code received :' + str(resp.status_code))



if __name__ == '__main__':
    ts = int(datetime.now().timestamp()*1000)
    #ts = 1622753527
    date_rw = datetime.today().strftime('%d-%b-%Y')
    print(date_rw)


