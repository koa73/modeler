#!/usr/bin/env python3
# Проверка данных моделей, если соответствуют заданным параметрам перенос в каталог out

import modelMaker as d
from shutil import copyfile
import re
import os

data = d.ModelMaker()

source_path = '/models/archive/'
#source_files_path = source_path + 'models/b500_150/'
source_files_path = source_path + 'complex/500_2/'
output_dir = data.get_file_dir() + source_path + 'models/x/'
#source_log_name = 'models_DB.csv'
source_log_name = 'checker_log.csv'

files, comments = data.read_file_db_to_list(source_path + source_log_name)

# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b500_2395', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b500_2395', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b500_2395', '2D')

idx = 0
for i, file in enumerate(files):

    #model = data.model_loader(file, source_files_path)
    model = data.model_loader('weights_b500_c2_'+str(i), source_files_path)

    y_up_pred = model.predict([X_up])
    y_none_pred = model.predict([X_none])
    y_down_pred = model.predict([X_down])

    check = data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file, comments[i], False)
    '''
    if float(check[2]) > 0.4 and float(check[3]) < 20:

        new_file = re.sub("\d+_\d+$", '150_' + str(idx), file)
        copyfile(data.get_file_dir() + source_files_path + file + ".json", output_dir + new_file + ".json")
        copyfile(data.get_file_dir() + source_files_path + file + ".h5", output_dir + new_file + ".h5")
        idx += 1
        data.write_log_file(check, new_file, comments[i], "models_DB")
    '''

