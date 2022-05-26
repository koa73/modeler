#!/usr/bin/env python3
# Сборка композитных моделей первого уровня

import tensorflow as tf
import modelMaker as d
import Binary as b
import uuid
import sys

data = d.ModelMaker()

print("Start composite model making ....")

model_base_name = "weights_b500_c1_"
source_path = '/models/archive/models/b500_150_f1/'
model_archive_path = '/models/archive/complex/500_3/'
out_log = "complex/500_3/checker"


if (len(sys.argv) < 3):
    print("Argument not found ")
    exit(0)


# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b500_2395', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b500_2395', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b500_2395', '2D')

# Сборка модели из листа, запись лога и сохранение моделей в dst каталог
def model_complex_builder(file_list):

    models = []
    for i in range(len(file_list)):
        # Load models
        model_tmp = data.model_loader(file_list[i], source_path)
        model_tmp._name = "functional_00" + str(i)
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
    #print(model.summary())

    # Get predict data
    y_up_pred = model.predict([X_up])
    y_none_pred = model.predict([X_none])
    y_down_pred = model.predict([X_down])

    print("------------------- Check model----------")
    prefix = str(data.get_next_file_index(model_archive_path))
    check = data.check_single_model(y_up_pred, y_none_pred, y_down_pred,  file_list,
                                    model_base_name + prefix +" Complex model 1 level. Big sensitive.", False, out_log)

    # Save model by condition
    if float(check[2]) > 0.75 and float(check[3]) == 0:
        data.save_conf(model, prefix, model_archive_path + model_base_name)  # Запись конфигурации
        model.save(data.get_file_dir() + model_archive_path + model_base_name + prefix + ".h5")


array = d.create_uniq_names(0, 105, offset=int(sys.argv[1]), step=int(sys.argv[2]), pat='weights_b500_616_')

for file_list in array:
    try:
        model_complex_builder(file_list)
    except Exception:
        pass