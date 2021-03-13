#!/usr/bin/env python3
# Запись предсказанных значений в csv file

import modelMaker as d
import numpy as np

data = d.ModelMaker()

source_path = '/models/archive/models/gpu/'
model_1_name = "weights_b25_150_18"
model_2_name = "weights_b25_150_43"
model_3_name = "weights_b25_150_74"
output_file = "/models/logs/compare.csv"

# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')

model1 = data.model_loader(model_1_name, source_path)
model2 = data.model_loader(model_2_name, source_path)
model3 = data.model_loader(model_2_name, source_path)

y_up_pred_1 = data.convert_to_simple_shape(model1.predict([X_up]))
y_up_pred_2 = data.convert_to_simple_shape(model2.predict([X_up]))
y_up_pred_3 = data.convert_to_simple_shape(model2.predict([X_up]))

y_pred_test = np.zeros(shape=(y_up.shape[0], 2), dtype=int)     # Сюда положим результаты прогона X_up моделями up, none, down

diff = 0
same = 0

for i in range(0, y_up_pred_1.shape[0]):
    if (y_up_pred_1[i, 0] == 1 and  y_up_pred_2[i, 0] == 1 and y_up_pred_3[i, 0] == 1):
        same +=1
    if (y_up_pred_1[i, 0] == 1 or  y_up_pred_2[i, 0] == 1 or y_up_pred_3[i, 0] == 1):
        diff +=1
    y_pred_test[i] = [y_up_pred_1[i, 0], y_up_pred_2[i, 0]]

print("====== Save predicted data ======\n")
print("Same : "+str(same)+" ,Diff : "+str(diff) + " Summ : "+str(same+diff))
np.savetxt(data.get_file_dir() + output_file, y_pred_test, delimiter=';', header='up_UP;up_NONE;up_DOWN;none_UP;none_NONE;'
                                                                         'none_DOWN;down_UP;down_NONE;down_DOWN')