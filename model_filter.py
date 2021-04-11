#!/usr/bin/env python3
# Проверка данных моделей, если соответствуют заданным параметрам перенос в каталог out

import modelMaker as d
from shutil import copyfile
import re

data = d.ModelMaker()

source_path = '/models/archive/'
source_files_path = source_path + 'models/gpu_1/'
source_log_name = 'models_DB.csv'
output_dir = data.get_file_dir() + source_path + 'models/gpu_0/'

output_log = "complex/best/check_complex"

# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')


files, comments = data.read_file_db_to_list(source_path + source_log_name)

check = []
idx = 0
for i, file in enumerate(files):

    model = data.model_loader(file, source_files_path)

    y_up_pred = model.predict([X_up])
    y_none_pred = model.predict([X_none])
    y_down_pred = model.predict([X_down])

    check = data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file, comments[i], False)

    if ((float(check[2]) > 1.2 and float(check[3]) < 20) or (float(check[3]) == 0 and check[0] > 5)):
        new_file = re.sub("\d+$", str(idx), file)
        copyfile(data.get_file_dir() + source_files_path+ file + ".json", output_dir + new_file + ".json")
        copyfile(data.get_file_dir() + source_files_path + file + ".h5", output_dir + new_file + ".h5")
        idx += 1
        data.write_log_file(check, new_file, comments[i], "models_DB")
