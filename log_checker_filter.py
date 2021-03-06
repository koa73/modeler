#!/usr/bin/env python3
# Фильтрация данных из checker_log файла по заданным условиям

import modelMaker as d
import csv

data = d.ModelMaker()

path = data.get_file_dir() + '/models/logs/'
file_name = path + 'check_01_log.csv'
output_log = 'filter_100_Errors_log.csv'
count = 0

try:
    #result = []
    with open(file_name, newline='') as f:
        next(f)
        rows = csv.reader(f, delimiter=';', quotechar='|')
        for row in rows:
            try:
                if (float(row[3]) <= 18  and int(row[1]) >= 99):
                    count +=1
                    d.write_log(path+output_log, row)
                    print(row[5]+',')
                    #result.append(row[5])
            except IndexError:
                continue
            except ValueError:
                pass
    f.close()
    print(count)
    #print(result)

except FileNotFoundError:
    print("Can't open file : " + file_name)