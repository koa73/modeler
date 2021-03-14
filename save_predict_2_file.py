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
model3 = data.model_loader(model_3_name, source_path)

y_up_pred_1 = data.convert_to_simple_shape(model1.predict([X_up]))
y_up_pred_2 = data.convert_to_simple_shape(model2.predict([X_up]))
y_up_pred_3 = data.convert_to_simple_shape(model3.predict([X_up]))

y_none_pred_1 = data.convert_to_simple_shape(model1.predict([X_none]))
y_none_pred_2 = data.convert_to_simple_shape(model2.predict([X_none]))
y_none_pred_3 = data.convert_to_simple_shape(model3.predict([X_none]))


y_down_pred_1 = data.convert_to_simple_shape(model1.predict([X_down]))
y_down_pred_2 = data.convert_to_simple_shape(model2.predict([X_down]))
y_down_pred_3 = data.convert_to_simple_shape(model3.predict([X_down]))

y_up_pred = y_up_pred_1+y_up_pred_2+y_up_pred_3
y_none_pred = y_none_pred_1+y_none_pred_2+y_none_pred_3
y_down_pred = y_down_pred_1+y_down_pred_2+y_down_pred_3

data.check_single_model(y_up_pred, y_none_pred, y_down_pred, str('TMP TEST'), "UP concatinate from gpu dir", False)

y_pred_test = np.zeros(shape=(y_up.shape[0], 3), dtype=int)     # Сюда положим результаты прогона X_up моделями up, none, down

diff = 0
same = 0

for i in range(0, y_up_pred_1.shape[0]):

    if (y_up_pred_1[i, 0] == 1 and  y_up_pred_2[i, 0] == 1 and y_up_pred_3[i, 0] == 1):
        same +=1

    elif (y_up_pred_1[i, 0] == 1 or  y_up_pred_2[i, 0] == 1 or y_up_pred_3[i, 0] == 1):

        diff +=1
        print([y_up_pred_1[i, 0], y_up_pred_2[i, 0], y_up_pred_3[i, 0]])

    y_pred_test[i] = [y_up_pred_1[i, 0], y_up_pred_2[i, 0], y_up_pred_3[i, 0]]

'''
for i in range(0, y_up_pred.shape[0]):
    print(y_up_pred[i])
'''
print ("------ "+str(i)+"\n")
print("====== Save predicted data ======\n")
print("Same : "+str(same)+" ,Diff : "+str(diff) + " Summ : "+str(same+diff))
np.savetxt(data.get_file_dir() + output_file, y_pred_test, delimiter=';', header='up_UP;up_NONE;up_DOWN;none_UP;none_NONE;'
                                                                         'none_DOWN;down_UP;down_NONE;down_DOWN')