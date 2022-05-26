#!/usr/bin/env python3

import tensorflow as tf
import sys
import modelMaker as d
import itertools
import numpy as np
import time
import logging

data = d.ModelMaker()

dirPath = data.get_file_dir()+ "/models/tmp/"
model_file_name = 'weights_b500_150_51'
model_path = '/home/oleg/PycharmProjects/modeler/models/archive/reteach/in/'
log_path = './log/'

print("Start model making ....")

if (len(sys.argv) < 2):
    print("Argument not found ")
    exit(0)

X_up, y_up = data.get_edu_data('edu','UP_'+sys.argv[1], '2D')
X_down, y_down = data.get_edu_data('edu','DOWN_'+sys.argv[1], '2D')
X_none, y_none = data.get_edu_data('edu','NONE_'+sys.argv[1], '2D')

class_weight = {0: 0.4, 1: 1.0, 2: 1.0}

X_train = np.concatenate((X_down, X_up), axis=0)
y_train = np.concatenate((y_none, y_up), axis=0)
X_train = np.concatenate((X_train, X_none), axis=0)
y_train = np.concatenate((y_train, y_none), axis=0)

def remake_model():
    print("\n >>>>>>> Load file : " + model_path + model_file_name + ".json  .....\n")
    json_file = open(model_path + model_file_name + ".json", "r")
    model_json = json_file.read()
    json_file.close()
    model = d.tf.keras.models.model_from_json(model_json)
    print("\n >>>>>>> Load file : " + model_path + model_file_name + ".h5  .....\n")
    model.load_weights(model_path + model_file_name + ".h5")
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    data.save_conf(model, sys.argv[1])  # Запись конфигурации для прерывания расчета

    # Сохранение модели с лучшими параметрами
    checkpointer = d.tf.keras.callbacks.ModelCheckpoint(monitor='accuracy',
                                                      filepath=dirPath + "weights_" + sys.argv[1] + ".h5",
                                                      verbose=1, save_best_only=True)
    # Уменьшение коэфф. обучения при отсутствии изменения ошибки в течении learn_count эпох
    reduce_lr = d.tf.keras.callbacks.ReduceLROnPlateau(monitor='accuracy', factor=0.1, patience=5, min_lr=0.000001,
                                                     verbose=1)
    # Остановка при переобучении. patience - сколько эпох мы ждем прежде чем прерваться.
    early_stopping = d.tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', min_delta=0, patience=10, verbose=0,
                                                      mode='auto')
    if not (class_weight[1] > 1):
        print(model.summary())

    model.fit(X_train, y_train, class_weight=class_weight, validation_split=0.01, epochs=100,
              batch_size=10, verbose=1, shuffle=True, callbacks=[checkpointer, reduce_lr, early_stopping])

    return model


def seq(start, end, step):
    if step == 0:
        raise ValueError("step must not be 0")
    sample_count = int(abs(end - start) / step)
    return itertools.islice(itertools.count(start, step), sample_count)


try:
    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        filename='./log/model_maker.log')

    for j in seq(0.3910, 0.4, 0.0001):
        print("----------------  Start new loop with value : " + str(j))
        for i in seq(1, 10, 1):
            logging.info("----------------  Start new loop with value class_weight: %s, iteration : %s " % (str(j),
                                                                                                            str(i)))
            # Тренировка сети Set 0 -UP, 1-None, 2-Down
            class_weight[0] = j

            model = remake_model()

            # ===================== Data load =========================

            X_down, y_down = data.get_check_data('test', 'DOWN_b500_2395', '2D')
            X_up, y_up = data.get_check_data('test', 'UP_b500_2395', '2D')
            X_none, y_none = data.get_check_data('test', 'NONE_b500_2395', '2D')

            # ===================== Make prediction =====================

            y_up_pred_test = model.predict([X_up])
            y_none_pred_test = model.predict([X_none])
            y_down_pred_test = model.predict([X_down])

            # ====================== Check model =========================

            data.check_single_model(y_up_pred_test, y_none_pred_test, y_down_pred_test, sys.argv[1],
                                    "UP model short period ----- fix %s/%s/%s/" % (str(j),str(class_weight[1]),str(class_weight[2])))

            print("UP model short period ----- fix %s/%s/%s/\n\n" % (str(j),str(class_weight[1]),str(class_weight[2])))

except Exception as ex:
    logging.info('>> Unsuccessful result. Script stopped : ' + str(ex))
    exit(1)