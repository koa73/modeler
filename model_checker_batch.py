#!/usr/bin/env python3
# Объединение предрасчитаннных моделей  и проверка на тестовых данных

import modelMaker as d
import numpy as np
import sys

data = d.ModelMaker()

if (len(sys.argv) < 3):
    print("Argument not found ")
    exit(0)

source_path = '/models/archive/complex/2/'
#source_path = '/models/archive/models/gpu/'
#source_path = '/data/models/archive/complex/'
comment_in_log = "UP complex leve 2 check"

# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')


def check_models(file_list):
    y_up_pred = np.zeros(y_up.shape, dtype=float)
    y_none_pred = np.zeros(y_up.shape, dtype=float)
    y_down_pred = np.zeros(y_up.shape, dtype=float)

    for i in range(len(file_list)):
        # Load test model
        model = data.model_loader(file_list[i], source_path)
        # Make prediction =====================
        y_up_pred = ((model.predict([X_up])) + y_up_pred)
        y_none_pred = ((model.predict([X_none])) + y_none_pred)
        y_down_pred = ((model.predict([X_down])) + y_down_pred)

    # input(y_up_pred.shape)
    # data.check_single_model(y_up_pred_test, y_none_pred_test, y_down_pred_test, "", "", False)
    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, str(file_list), comment_in_log, False, "check_complex")

#15, 111
di = d.create_dictionary(1, 20)

i, start, offset = 0, int(sys.argv[1]), int(sys.argv[2])

for key in di:
    i += 1
    if i <= start:
        continue
    else:
        check_models(di[key])
    if i == start + offset:
        break