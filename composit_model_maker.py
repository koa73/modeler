#!/usr/bin/env python3
# Сборка композитных моделей из заданного списка

import tensorflow as tf
import modelMaker as d
import Bynary as b
import uuid

data = d.ModelMaker()

print("Start composite model making ....")

model_base_name = "weights_b25_150_"
source_path = '/models/archive/models/gpu_1/'
#source_path = '/models/archive/complex/1/'
model_archive_path = '/models/archive/complex/5/'
out_log = "complex/5/checker"

# Сборка модели из листа, запись лога и сохранение моделей в dst каталог
def model_complex_builder(file_list, prefix):

    models = []
    for i in range(len(file_list)):
        # Load models
        model_tmp = data.model_loader(file_list[i], source_path)
        model_tmp._name = "functional_0" + str(i)
        models.append(model_tmp)

    print("------------------- Build model----------")
    model_layers = []
    input_layer_1 = tf.keras.layers.Input(shape=(24,), name=str(uuid.uuid4()))
    for i in range(len(models)):
        model_layers.append(models[i](input_layer_1))
    output_b = tf.keras.layers.add(model_layers)
    output = tf.keras.layers.Softmax()(output_b)
    model = tf.keras.models.Model(inputs=input_layer_1, outputs=[output])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    #
    print(model.summary())

    data.save_conf(model, prefix, model_archive_path+model_base_name)  # Запись конфигурации
    model.save(data.get_file_dir() + model_archive_path + model_base_name + prefix + ".h5")

    # Load test data
    X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
    X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
    X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')
    # Get predict data
    y_up_pred = model.predict([X_up, X_up, X_up])
    y_none_pred = model.predict([X_none, X_none, X_none])
    y_down_pred = model.predict([X_down, X_down, X_down])

    input(y_up_pred)

    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file_list, "Complex model 1 level. Big sensitive.",
                            False, out_log)

# Модель с кастомным бинарным слоем
def model_complex_binary_builder(file_list, prefix):
    models = []
    for i in range(len(file_list)):
        # Load models
        model_tmp = data.model_loader(file_list[i], source_path)
        model_tmp._name = "functional_03" + str(i)
        models.append(model_tmp)

    print("------------------- Build model----------")
    in_layers = []
    out_layers = []
    binary_layer = []
    input_layer_1 = tf.keras.layers.Input(shape=(24,), name=str(uuid.uuid4()))

    for i in range(len(models)):
        in_layers.append(models[i](input_layer_1))
        # idx of output which must be amplified 0-UP, 1-NONE, 2-DOWN
        binary_layer.append(b.Binary(name=str(uuid.uuid4()), idx=1))
        out_layers.append(binary_layer[i](in_layers[i]))

    output = tf.keras.layers.add(out_layers, name=str(uuid.uuid4()))
    model = tf.keras.models.Model(inputs=input_layer_1, outputs=[output])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    #
    print(model.summary())

    data.save_conf(model, prefix, model_archive_path + model_base_name)  # Запись конфигурации
    model.save(data.get_file_dir() + model_archive_path + model_base_name + prefix + ".h5")

    # Load test data
    X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
    X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
    X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')
    # Get predict data
    y_up_pred = model.predict([X_up, X_up, X_up])
    y_none_pred = model.predict([X_none, X_none, X_none])
    y_down_pred = model.predict([X_down, X_down, X_down])

    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file_list, "Complex model 2 level. Big sensitive.",
                            False, out_log)


# список моделей для сборки
'''
array = [['weights_b25_150_16', 'weights_b25_150_92', 'weights_b25_150_103']]
'''
#array = d.create_uniq_names(1, 32, 5, 0)
array = [['weights_b25_150_0', 'weights_b25_150_62', 'weights_b25_150_63'],
         ['weights_b25_150_0', 'weights_b25_150_62', 'weights_b25_150_63']]

i = data.get_next_file_index(model_archive_path)

for file_list in array:
    try:
        model_complex_builder(file_list, str(i))
        i += 1
    except Exception:
        pass
