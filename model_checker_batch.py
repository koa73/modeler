#!/usr/bin/env python3
# Объединение предрасчитаннных моделей  и проверка на тестовых данных

import modelMaker as d
import numpy as np
import sys

data = d.ModelMaker()

if (len(sys.argv) < 3):
    print("Argument not found ")
    exit(0)

#source_path = '/models/archive/complex/1/'
source_path = '/models/archive/models/gpu_1/'
#source_path = '/data/models/archive/complex/'
comment_in_log = "DOWN complex leve 3 check zero"

# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b500_2395', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b500_2395', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b500_2395', '2D')


def check_models(file_list):
    y_up_pred = np.zeros(y_up.shape, dtype=float)
    y_none_pred = np.zeros(y_up.shape, dtype=float)
    y_down_pred = np.zeros(y_up.shape, dtype=float)

    for i in range(len(file_list)):
        # Load test model
        model = data.model_loader(file_list[i], source_path)
        # Make prediction =====================
        y_up_pred = (model.predict([X_up]) + y_up_pred)
        y_none_pred = (model.predict([X_none]) + y_none_pred)
        y_down_pred = (model.predict([X_down]) + y_down_pred)

    return y_up_pred, y_none_pred, y_down_pred


array = d.create_uniq_names(0, 117, offset=int(sys.argv[1]), step=int(sys.argv[2]))

for file_list in array:

    y_up_pred, y_none_pred, y_down_pred = check_models(file_list)
    print(file_list)
    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, str(file_list), comment_in_log, False, "checker")
