#!/usr/bin/env python3
# Сборка композитных моделей из заданного списка

import tensorflow as tf
import modelMaker as d
import Bynary as b
import uuid

data = d.ModelMaker()

print("Start composite model making ....")

model_base_name = "weights_b25_150_"
#source_path = '/models/archive/models/gpu/'
source_path = '/models/archive/complex/1/'
out_log = "complex/tmp/checker"
model_archive_path = '/models/archive/complex/best/'


# Сборка модели из листа, запись лога и сохранение моделей в dst каталог
def model_complex_builder(file_list, prefix):
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
        binary_layer.append(b.Binary(name=str(uuid.uuid4()), idx=0))
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

    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file_list, "Complex model 1 level. Big sensitive.",
                            False, out_log)

#[('11', 40), ('28', 34), ('16', 33), ('29', 20), ('15', 15), ('5', 14), ('19', 13), ('12', 11), ('8', 11), ('27', 10), ('22', 10), ('3', 9), ('24', 9), ('21', 9), ('25', 7), ('10', 7), ('20', 7), ('2', 4), ('13', 4), ('4', 3), ('23', 2), ('30', 2), ('9', 2)]
#[('11', 114), ('16', 108), ('28', 92), ('29', 77), ('15', 65), ('22', 50), ('5', 50), ('19', 50), ('12', 49), ('3', 47), ('8', 46), ('10', 42), ('24', 41), ('20', 36), ('21', 36), ('23', 30), ('27', 30), ('25', 24), ('2', 17), ('13', 16), ('9', 13), ('7', 12), ('1', 11), ('30', 10), ('26', 10), ('4', 9), ('18', 5), ('17', 2)]


file_list = ["weights_b25_150_11", "weights_b25_150_28", "weights_b25_150_16", "weights_b25_150_29", "weights_b25_150_15", "weights_b25_150_19", "weights_b25_150_12",  "weights_b25_150_20"
    ]#,"weights_b25_150_8", "weights_b25_150_27", "weights_b25_150_24", "weights_b25_150_25", "weights_b25_150_9"]
# file_list = ['weights_b25_150_30', 'weights_b25_150_86', 'weights_b25_150_104', 'weights_b25_150_16', 'weights_b25_150_103']
model_complex_builder(file_list, '11')
