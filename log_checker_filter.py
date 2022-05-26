#!/usr/bin/env python3
# Фильтрация данных из checker_log файла по заданным условиям
# Выводит в лог списки удовлетворяющих условию моделей и их общее число

import modelMaker as d
import csv
import re
import collections

data = d.ModelMaker()

#path = data.get_file_dir() + '/models/logs/gpu_2/'
path = data.get_file_dir() + '/models/logs/complex/500_3/'
file_name = path + 'checker_log.csv'
output_log = 'short_log.csv'
count = 0
dict = {}
output_array = '['
try:
    with open(file_name, newline='') as f:
        next(f)
        rows = csv.reader(f, delimiter=';', quotechar='|')
        for row in rows:
            try:
                # row[3] - Rel_Error
                # row[1] - Hit
                #if (float(row[3]) <= 18  and int(row[1]) >= 99):
                if (float(row[2]) == 0 and int(row[1]) >= 80 ):
                    count +=1
                    output_array = output_array + ', ' +row[5]
                    d.write_log(path+output_log, row)

                    file_list = row[5].split(',')
                    for name in file_list:
                        num = re.findall(r"_(\d+)\']?$", name)
                        if num[0] in dict:
                            dict[num[0]] = dict[num[0]] + 1
                        else:
                            dict[num[0]] = 1
            except IndexError:
                continue
            except ValueError:
                pass
    f.close()
    print(count)
    print(sorted(dict.items(), key=lambda x: x[1], reverse=True))
    print(output_array+']')
except FileNotFoundError:
    print("Can't open file : " + file_name)