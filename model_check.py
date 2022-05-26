#!/usr/bin/env python3
# Проверка модели

import modelMaker as d
from shutil import copyfile
import re
import os

data = d.ModelMaker()

source_path = '/models/archive/'
source_files_path = source_path + 'complex/5/'
source_log_name = 'checker_log.csv'


# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b500_2395', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b500_2395', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b500_2395', '2D')


model = data.model_loader('weights_b500_c3', source_files_path)

y_up_pred = model.predict([X_up])
y_none_pred = model.predict([X_none])
y_down_pred = model.predict([X_down])

check = data.check_single_model(y_up_pred, y_none_pred, y_down_pred, '', '', False)
print(check)

