#!/usr/bin/env python3
# Сборка композитных моделей из заданного списка

import tensorflow as tf
import modelMaker as d
import uuid

data = d.ModelMaker()

print("Start composite model making ....")

model_base_name = "weights_b25_150_"
source_path = '/models/archive/models/gpu/'
model_archive_path = '/models/archive/complex/3/'

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
    output = tf.keras.layers.add(model_layers)
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

    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file_list, "Complex model 1 level. Big sensitive.", False, "complex/3/checker")
# список моделей для сборки
array = [['weights_b25_150_16', 'weights_b25_150_92', 'weights_b25_150_103'],
['weights_b25_150_25', 'weights_b25_150_30', 'weights_b25_150_86'],
['weights_b25_150_25', 'weights_b25_150_85', 'weights_b25_150_86'],
['weights_b25_150_26', 'weights_b25_150_30', 'weights_b25_150_86'],
['weights_b25_150_28', 'weights_b25_150_30', 'weights_b25_150_86'],
['weights_b25_150_28', 'weights_b25_150_83', 'weights_b25_150_87'],
['weights_b25_150_28', 'weights_b25_150_85', 'weights_b25_150_86'],
['weights_b25_150_30', 'weights_b25_150_31', 'weights_b25_150_86'],
['weights_b25_150_30', 'weights_b25_150_83', 'weights_b25_150_89'],
['weights_b25_150_30', 'weights_b25_150_85', 'weights_b25_150_86'],
['weights_b25_150_30', 'weights_b25_150_86', 'weights_b25_150_104'],
['weights_b25_150_31', 'weights_b25_150_85', 'weights_b25_150_92'],
['weights_b25_150_31', 'weights_b25_150_92', 'weights_b25_150_95'],
['weights_b25_150_41', 'weights_b25_150_86', 'weights_b25_150_88'],
['weights_b25_150_43', 'weights_b25_150_86', 'weights_b25_150_96'],
['weights_b25_150_60', 'weights_b25_150_86', 'weights_b25_150_86'],
['weights_b25_150_67', 'weights_b25_150_86', 'weights_b25_150_86'],
['weights_b25_150_72', 'weights_b25_150_86', 'weights_b25_150_86'],
['weights_b25_150_74', 'weights_b25_150_86', 'weights_b25_150_86']]

i = 0
for file_list in array:
    i += 1
    model_complex_builder(file_list, str(i))
