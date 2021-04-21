#!/usr/bin/env python3
# Фильтрация данных из checker_log файла по заданным условиям
# Тройка лучших max Sensitive, min Relative_Error, Both parameters

import modelMaker as d
import csv

data = d.ModelMaker()

path = data.get_file_dir() + '/models/logs/gpu_2/'
#file_name = path + 'check_01_log.csv'
#file_name = path + 'filter_100_Errors_log.csv'
file_name = path + 'checker_1_log.csv'
count = 0

try:
    r1 = ['', '0', '0', '100', '0', '', '']
    r2 = ['', '0', '0', '100', '0', '', '']
    r3 = ['','0','0','100','0','','']

    with open(file_name, newline='') as f:
        next(f)
        rows = csv.reader(f, delimiter=';', quotechar='|')
        for row in rows:
            try:
                if (float(r1[4]) <= float(row[4])):
                    r1 = row
                if (float(r2[3]) >= float(row[3])):
                    r2 = row
                if ((float(r3[4]) <= float(row[4])) and (float(r3[3]) >= float(row[3]))):
                    r3 = row
            except IndexError:
                continue
            except ValueError:
                pass
    f.close()
    print(r1)
    print(r2)
    print(r3)

except FileNotFoundError:
    print("Can't open file : " + file_name)