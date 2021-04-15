#!/usr/bin/env python3
# Проверка данных моделей, если соответствуют заданным параметрам перенос в каталог out

import modelMaker as d
from shutil import copyfile
import re
import os

data = d.ModelMaker()

source_path = '/models/archive/'
source_files_path = source_path + 'models/gpu_1/'
output_dir = data.get_file_dir() + source_path + 'models/gpu_0/'

# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')

for i in range(0, 117):

    file = 'weights_b25_150_'+str(i)
    model = data.model_loader(file, source_files_path)

    y_up_pred = model.predict([X_up])
    y_none_pred = model.predict([X_none])
    y_down_pred = model.predict([X_down])

    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file, 'Down models', False)
