import logging
import os
import sys
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal as D, ROUND_DOWN
import modelMaker as d

data = d.ModelMaker()

model_path = os.environ['MODEL_PATH']
log_path = os.environ['LOG_PATH']

dirPath = data.get_file_dir()+ "/models/tmp/"
set_name = "b500_616"
model_file_name = 'weights_b500_150_37'

X_up, y_up = data.get_edu_data('edu','UP_'+set_name, '2D')
X_down, y_down = data.get_edu_data('edu','DOWN_'+set_name, '2D')
X_none, y_none = data.get_edu_data('edu','NONE_'+set_name, '2D')

class_weight = {0: 0.4, 1: 1.0, 2: 1.0}

X_train = np.concatenate((X_down, X_up), axis=0)
y_train = np.concatenate((y_none, y_up), axis=0)
X_train = np.concatenate((X_train, X_none), axis=0)
y_train = np.concatenate((y_train, y_none), axis=0)


def model_loader():
    print("\n >>>>>>> Load file : " + model_path + model_file_name + ".json  .....\n")
    json_file = open(model_path + model_file_name + ".json", "r")
    model_json = json_file.read()
    json_file.close()
    model = d.tf.keras.models.model_from_json(model_json)
    print("\n >>>>>>> Load file : " + model_path + model_file_name + ".h5  .....\n")
    model.load_weights(model_path + model_file_name + ".h5")
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    data.save_conf(model, 'x_re_teach')  # Запись конфигурации сути для прерывания расчета

    # Сохранение модели с лучшими параметрами
    checkpointer = d.tf.keras.callbacks.ModelCheckpoint(monitor='accuracy',
                                                      filepath=dirPath + "weights_" + 'x_re_teach' + ".h5",
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
              batch_size=25, verbose=1, shuffle=True, callbacks=[checkpointer, reduce_lr, early_stopping])

    return model

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(message)s',
                        filename=log_path + Path(__file__).stem + '.log',
                        level=logging.INFO)

    old_model = model_loader()