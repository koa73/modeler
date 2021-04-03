#!/usr/bin/env python3

import tensorflow as tf
import sys
import modelMaker as d
import itertools
import numpy as np
import time


data = d.ModelMaker()

dirPath = data.get_file_dir()+ "/models/tmp/"

print("Start model making ....")

if (len(sys.argv) < 2):
    print("Argument not found ")
    exit(0)

X_up, y_up = data.get_edu_data('edu','UP_'+sys.argv[1], '2D')
X_down, y_down = data.get_edu_data('edu','DOWN_'+sys.argv[1], '2D')
X_none, y_none = data.get_edu_data('edu','NONE_'+sys.argv[1], '2D')

class_weight = {0: 1., 1: 1.15, 2: 0.55}

X_train = np.concatenate((X_down, X_up), axis=0)
y_train = np.concatenate((y_down, y_none), axis=0)
X_train = np.concatenate((X_train, X_none), axis=0)
y_train = np.concatenate((y_train, y_none), axis=0)


def prepare_model():

    sec = str(time.time())
    input_layer_1 = tf.keras.layers.Input(shape=(24,), name='1' + sec)
    norma_layer = tf.keras.layers.LayerNormalization(axis=1, name='2' + sec)(input_layer_1)
    hidden_d2_dense = tf.keras.layers.Dense(12, activation='tanh', name='3' + sec)(norma_layer)
    hidden_d3_dense = tf.keras.layers.Dense(24, activation='tanh', name='4' + sec)(hidden_d2_dense)
    #hidden_d4_dense = tf.keras.layers.Dense(34, activation='tanh', name='5' + sec)(hidden_d3_dense)
    hidden_d5_dense = tf.keras.layers.Dense(6, activation='tanh', name='6' + sec)(hidden_d2_dense)
    output = tf.keras.layers.Dense(3, activation='softmax', name='7' + sec)(hidden_d5_dense)

    #
    model = tf.keras.models.Model(inputs=[input_layer_1], outputs=[output])
    #
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    #

    data.save_conf(model, sys.argv[1])  # Запись конфигурации скти для прерывания расчета

    # Сохранение модели с лучшими параметрами
    checkpointer = tf.keras.callbacks.ModelCheckpoint(monitor='accuracy',
                                                      filepath=dirPath + "weights_" + sys.argv[1] + ".h5",
                                                      verbose=1, save_best_only=True)
    # Уменьшение коэфф. обучения при отсутствии изменения ошибки в течении learn_count эпох
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='accuracy', factor=0.1, patience=5, min_lr=0.000001,
                                                     verbose=1)
    # Остановка при переобучении. patience - сколько эпох мы ждем прежде чем прерваться.
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', min_delta=0, patience=10, verbose=0,
                                                      mode='auto')
    if not (class_weight[1] > 1):
        print(model.summary())

    model.fit(X_train, y_train, class_weight=class_weight, validation_split=0.05, epochs=100,
              batch_size=10, verbose=1, shuffle=True, callbacks=[checkpointer, reduce_lr, early_stopping])

    return model


def seq(start, end, step):
    if step == 0:
        raise ValueError("step must not be 0")
    sample_count = int(abs(end - start) / step)
    return itertools.islice(itertools.count(start, step), sample_count)


for j in seq(1.0, 1.55, 0.05):

    for i in seq(3.25, 3.55, 0.05):

        print("----------------  Start new loop with value : " + str(j))
        # Тренировка сети Set 0 -UP, 1-None, 2-Down
        class_weight[1] = j

        model = prepare_model()

        # ===================== Data load =========================

        X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
        X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
        X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')

        # ===================== Make prediction =====================

        y_up_pred_test = model.predict([X_up])
        y_none_pred_test = model.predict([X_none])
        y_down_pred_test = model.predict([X_down])

        # ====================== Check model =========================

        data.check_single_model(y_up_pred_test, y_none_pred_test, y_down_pred_test, sys.argv[1],
                                "DOWN model short period ----- fix 1/"+str(j)+"/0.55")
