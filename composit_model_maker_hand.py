#!/usr/bin/env python3
# Сборка композитных моделей из заданного списка

import tensorflow as tf
import modelMaker as d
import Amplifier as m
import uuid

data = d.ModelMaker()

print("Start composite model making ....")

model_base_name = "weights_b25_150_"
source_path = '/models/archive/models/gpu/'
#source_path = '/models/archive/complex/tmp/'
out_log = "complex/tmp/checker"
model_archive_path = '/models/archive/complex/best/'


# Сборка модели из листа, запись лога и сохранение моделей в dst каталог
def model_complex_builder(file_list, prefix):

    amplifier = m.Amplifier()
    models = []
    for i in range(len(file_list)):
        # Load models
        model_tmp = data.model_loader(file_list[i], source_path)
        model_tmp._name = "functional_03" + str(i)
        models.append(model_tmp)

    print("------------------- Build model----------")
    model_layers = []
    input_layer_1 = tf.keras.layers.Input(shape=(24,), name=str(uuid.uuid4()))
    for i in range(len(models)):
        model_layers.append(models[i](input_layer_1))
    output = tf.keras.layers.add(model_layers, name=str(uuid.uuid4()))
    output_2 = amplifier(output)
    model = tf.keras.models.Model(inputs=input_layer_1, outputs=[output_2])
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

    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file_list, "Complex model 1 level. Big sensitive.", False, out_log)

file_list = ['weights_b25_150_30', 'weights_b25_150_86', 'weights_b25_150_104', 'weights_b25_150_16', 'weights_b25_150_103']
model_complex_builder(file_list, '07')