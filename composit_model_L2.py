#!/usr/bin/env python3
# Сборка композитных моделей из заданного списка

import tensorflow as tf
import modelMaker as d
import Binary as b
import uuid
import sys

data = d.ModelMaker()

print("Start composite model making ....")

model_base_name = "weights_b500_616_c2"
#source_path = '/models/archive/complex/500_1/'
#model_archive_path = '/models/archive/complex/500_2/'
#out_log = "complex/500_2/checker"
source_path = '/models/archive/complex/500_3/'
model_archive_path = '/models/archive/complex/500_4/'
out_log = "complex/500_4/checker"


# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b500_2395', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b500_2395', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b500_2395', '2D')


# Модель с кастомным бинарным слоем
def model_complex_binary_builder(file_list, prefix):
    models = []
    for i in range(len(file_list)):
        # Load models
        model_tmp = data.model_loader(file_list[i], source_path)
        model_tmp._name = "functional_04" + str(i)
        models.append(model_tmp)

    print("------------------- Build model----------")
    in_layers = []
    out_layers = []
    binary_layer = []
    input_layer_1 = tf.keras.layers.Input(shape=(24,), name=str(uuid.uuid4()))

    for i in range(len(models)):
        in_layers.append(models[i](input_layer_1))
        # idx of output which must be amplified 0-UP, 1-NONE, 2-DOWN
        binary_layer.append(b.Binary(2, name=str(uuid.uuid4())))
        out_layers.append(binary_layer[i](in_layers[i]))

    output = tf.keras.layers.add(out_layers, name=str(uuid.uuid4()))
    model = tf.keras.models.Model(inputs=input_layer_1, outputs=[output])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    #
    print(model.summary())

    data.save_conf(model, prefix, model_archive_path + model_base_name)  # Запись конфигурации
    model.save(data.get_file_dir() + model_archive_path + model_base_name + prefix + ".h5")

    # Load test data
    X_down, y_down = data.get_check_data('test', 'DOWN_b500_2395', '2D')
    X_up, y_up = data.get_check_data('test', 'UP_b500_2395', '2D')
    X_none, y_none = data.get_check_data('test', 'NONE_b500_2395', '2D')

    # Get predict data
    y_up_pred = model.predict([X_up])
    y_none_pred = model.predict([X_none])
    y_down_pred = model.predict([X_down])

    print("------------------- Check model----------")
    check = data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file_list, "Complex model 2 level. Big sensitive.",
                            False, out_log)
    print(check)

# список моделей для сборки
#{'weights_b500_c1_3696': 35.0, 'weights_b500_c1_1297': 34.0, 'weights_b500_c1_1852': 34.0, 'weights_b500_c1_1357': 32.0, 'weights_b500_c1_1718': 32.0, 'weights_b500_c1_2853': 32.0, 'weights_b500_c1_3238': 32.0, 'weights_b500_c1_913': 31.0, 'weights_b500_c1_1534': 30.0, 'weights_b500_c1_2565': 30.0, 'weights_b500_c1_3260': 30.0, 'weights_b500_c1_287': 29.0, 'weights_b500_c1_1504': 29.0, 'weights_b500_c1_1648': 29.0, 'weights_b500_c1_1912': 29.0, 'weights_b500_c1_2338': 29.0, 'weights_b500_c1_2914': 29.0, 'weights_b500_c1_267': 28.0, 'weights_b500_c1_2597': 28.0, 'weights_b500_c1_3796': 28.0, 'weights_b500_c1_3848': 28.0, 'weights_b500_c1_3862': 28.0, 'weights_b500_c1_3893': 28.0, 'weights_b500_c1_1927': 27.0, 'weights_b500_c1_1988': 27.0, 'weights_b500_c1_2083': 27.0, 'weights_b500_c1_3755': 27.0, 'weights_b500_c1_3837': 27.0, 'weights_b500_c1_3880': 27.0, 'weights_b500_c1_92': 26.0, 'weights_b500_c1_1511': 26.0, 'weights_b500_c1_2623': 26.0, 'weights_b500_c1_942': 25.0, 'weights_b500_c1_1994': 25.0, 'weights_b500_c1_2857': 25.0, 'weights_b500_c1_3849': 25.0, 'weights_b500_c1_3868': 25.0, 'weights_b500_c1_3884': 25.0, 'weights_b500_c1_15': 24.0, 'weights_b500_c1_2604': 23.0, 'weights_b500_c1_3885': 23.0, 'weights_b500_c1_3850': 22.0}
#array = [['weights_b500_c1_3696', 'weights_b500_c1_1297', 'weights_b500_c1_1852', 'weights_b500_c1_1357', 'weights_b500_c1_1718', 'weights_b500_c1_2853', 'weights_b500_c1_3238', 'weights_b500_c1_913', 'weights_b500_c1_1534', 'weights_b500_c1_2565', 'weights_b500_c1_3260', 'weights_b500_c1_287', 'weights_b500_c1_1504', 'weights_b500_c1_1648', 'weights_b500_c1_1912', 'weights_b500_c1_2338', 'weights_b500_c1_2914', 'weights_b500_c1_267', 'weights_b500_c1_2597', 'weights_b500_c1_3796', 'weights_b500_c1_3848', 'weights_b500_c1_3862', 'weights_b500_c1_3893', 'weights_b500_c1_1927', 'weights_b500_c1_1988', 'weights_b500_c1_2083', 'weights_b500_c1_3755', 'weights_b500_c1_3837', 'weights_b500_c1_3880', 'weights_b500_c1_92', 'weights_b500_c1_1511', 'weights_b500_c1_2623', 'weights_b500_c1_942', 'weights_b500_c1_1994', 'weights_b500_c1_2857', 'weights_b500_c1_3849', 'weights_b500_c1_3868', 'weights_b500_c1_3884', 'weights_b500_c1_15', 'weights_b500_c1_2604', 'weights_b500_c1_3885', 'weights_b500_c1_3850']]
#array = [['weights_b500_c1_3696', 'weights_b500_c1_1297', 'weights_b500_c1_1357', 'weights_b500_c1_1718', 'weights_b500_c1_3238', 'weights_b500_c1_3260', 'weights_b500_c1_1504', 'weights_b500_c1_3796', 'weights_b500_c1_3848', 'weights_b500_c1_92', 'weights_b500_c1_1511',  'weights_b500_c1_2857', 'weights_b500_c1_15']]
array = [[
'weights_b500_c1_5689','weights_b500_c1_3064','weights_b500_c1_5445','weights_b500_c1_4470','weights_b500_c1_4242',
'weights_b500_c1_5691','weights_b500_c1_3047','weights_b500_c1_420','weights_b500_c1_55', 'weights_b500_c1_5505',
'weights_b500_c1_5740',
]]

#

i = data.get_next_file_index(model_archive_path)

for file_list in array:
    try:
        model_complex_binary_builder(file_list, str(i))
        i += 1
    except Exception as ex:
        print(ex)
        pass
