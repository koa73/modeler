#!/usr/bin/env python3

import csv
import os
from datetime import datetime
import numpy as np
from shutil import copyfile
import tensorflow as tf


def create_dictionary(first, last):
    arr = []
    for i in range(first, last):
        arr.append(i)

    d = {}
    pat = 'weights_b25_150_'
    for a in arr:
        for b in arr:
            for c in arr:
                # Remove any doubles
                #if ((a == b) or (b == c) or (a == c)):
                #    continue
                if ((a == b == c)):
                    continue
                d[str(sorted([a, b, c]))] = [pat + str(c), pat + str(b), pat + str(a)]
    return d


def write_log(name, data_list):
    filename = name
    if os.path.exists(filename):
        append_write = 'a'  # append if already exists
    else:
        append_write = 'w'  # make a new file if not

    with open(filename, append_write, newline='') as csv_out_file:
        output = csv.writer(csv_out_file, delimiter=';')

        if (append_write == 'w'):
            output.writerow(['Date', 'Hit', 'Mistake', 'Rel_Error', 'Sensetive', 'Model', 'Comment'])

        output.writerow(data_list)

    csv_out_file.close()


class ModelMaker:
    __fileDir = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, testPrefix='') -> None:
        super().__init__()
        self.testPrefix = testPrefix

    def model_loader(self, prefix, path=''):
        if not path:
            input_dir = self.__fileDir + '/models/archive/models/'
        else:
            input_dir = self.__fileDir + path
        print("\n >>>>>>> Load file : " + input_dir + prefix + ".json  .....\n")
        json_file = open(input_dir + prefix + ".json", "r")
        model_json = json_file.read()
        json_file.close()
        model = tf.keras.models.model_from_json(model_json)
        print("\n >>>>>>> Load file : " + input_dir + prefix + ".h5  .....\n")
        model.load_weights(input_dir + prefix + ".h5")
        model.trainable = False
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        return model

    def get_check_data(self, type: str, caseName: str, shape='3D'):

        data_path = self.__fileDir + '/data/test/cases/binary/'
        return self.__get_data(type, caseName, data_path, shape)

    def get_edu_data(self, type: str, caseName: str, shape='3D'):
        data_path = self.__fileDir + '/data/'
        return self.__get_data(type, caseName, data_path, shape)

    def __get_data(self, type: str, casename: str, data_path: str, shape) -> object:
        """
        :return: X, y numpy arrays
        :rtype: object
        """
        _list = ['X', 'y']
        result = []

        for i in _list:
            with open(data_path + type + '_' + i + '_' + casename + '.npy', 'rb') as fin:
                result.append(np.load(fin))

        if (shape == '2D'):
            result[0] = result[0].reshape(result[0].shape[0], -1)

        print(' >>>> Loaded ' + type + ' data case ' + casename + ' shape X/y :' + str(result[0].shape) + ' '
              + str(result[1].shape))
        return result[0], result[1]

    def get_file_dir(self):
        return self.__fileDir

    def save_conf(self, model, prefix, path="/models/tmp/weights_"):
        """
        :param prefix:
        :param path:
        :param model:
        :return: Null
        """
        json_file = open(self.__fileDir + path + prefix + ".json", "w")
        json_file.write(model.to_json())
        json_file.close

    # Нахождение индекса максимального элемента
    # Если два максимума, тогда возвращается 0
    def __get_max_index(self, vector):

        convert_dict = {0: 1, 1: 0, 2: -1}
        winner = np.argwhere(vector == np.amax(vector))
        if (winner.size > 1):
            return 0
        else:
            return convert_dict[winner[0][0]]

    def __sum_check_results(self, vector):
        up = 0
        none = 0
        down = 0
        for i in range(vector.shape[0]):
            max_index = self.__get_max_index(vector[i])
            if (max_index == 0):
                none += 1
            elif (max_index == 1):
                up += 1
            elif (max_index == -1):
                down += 1
        print("\nUP:\t" + str(up) + "\nNONE:\t" + str(none) + "\nDOWN:\t" + str(down) + "\n")
        return up, none, down

    # Находит максимум в массиве (n, 3 ) и конвертирует в форму 1./0. [0., 0. , 0.]
    def convert_to_simple_shape(self, np_array):
        result = []
        for i in range(np_array.shape[0]):
            winner = np.argwhere(np_array[i] == np.amax(np_array[i]))
            if (winner.size > 1):
                result.append([0., 1., 0.])
            else:
                z = np.zeros(3, dtype=float)
                z[winner[0][0]] = 1.
                result.append(z)

        return np.array(result).astype(np.float32)

    # Check single model
    def check_single_model(self, y_UP, y_NONE, y_DOWN, model, comment='', need_archive=True, output_file_name = 'cheker'):

        all_errors = 0
        print("------------------------------------ \n")
        print(">>> Check Up case (shape " + str(y_UP.shape) + "): ")
        up_, none, down = self.__sum_check_results(y_UP)
        all_errors += abs(down)

        print(">>> Check None case shape(" + str(y_NONE.shape) + ") : ")
        up, none, down = self.__sum_check_results(y_NONE)
        all_errors = all_errors + abs(down) + up

        print(">>> Check Down case shape(" + str(y_DOWN.shape) + ") : ")
        up, none, down = self.__sum_check_results(y_DOWN)
        all_errors = all_errors + up

        try:
            k1 = (up_ + abs(down)) / (y_UP.shape[0] + y_DOWN.shape[0]) * 100
        except ZeroDivisionError:
            k1 = 1000
        try:
            k2 = (1 - (1 - all_errors / (up_ + abs(down)))) * 100

        except ZeroDivisionError:
            k2 = 1000

        print(">>>> Hit : " + str(up_ + abs(down)) + "\t Mistake : " + str(all_errors) +
              "\t Sensitive : " + "%.4f" % k1 + " %\t Relevant_Error : " + "%.4f" % k2 + " %\n")

        if need_archive:
            self.__archive_model_data(up_ + abs(down), all_errors, k1, k2, model, comment)
        else:
            self.__write_log_file(up_ + abs(down), all_errors, "%.4f" % k1, "%.4f" % k2, model, comment, output_file_name)

        # return up_+abs(down), all_errors, "%.4f" % k1, "%.4f" % k2

    def read_file_db_to_list(self, input_file):
        try:
            result_list = []
            with open(self.__fileDir + input_file, newline='') as f:

                rows = csv.reader(f, delimiter=';', quotechar='|')

                for row in rows:
                    try:
                        result_list.append(row[5].replace(".h5", ""))
                    except IndexError:
                        continue
            f.close()
            return result_list

        except FileNotFoundError:
            print("Can't open file : " + input_file)

    def __write_log_file(self, hit, mistake, sensetive, error, about_models, additional_info, name="models"):

        date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        output_dir = self.__fileDir + "/models/logs/"
        filename = output_dir + name + "_log.csv"

        write_log(filename, [date_time, hit, mistake, error, sensetive, about_models, additional_info])

    def __archive_model_data(self, hit, mistake, sensetive, error, prefix, comment):

        dateTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        outputDir = self.__fileDir + "/models/"
        filename = self.__fileDir + "/models/archive/logs/" + 'models_DB.csv'
        model_name = "weights_" + prefix

        if os.path.exists(filename):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        try:
            file_count = len([name for name in os.listdir(outputDir + 'models')
                              if os.path.isfile(os.path.join(outputDir + 'models', name))]) / 2

            copyfile(self.__fileDir + "/models/tmp/" + model_name + ".json",
                     outputDir + "archive/models/" + model_name + "_" + str(int(file_count)) + ".json")

            copyfile(self.__fileDir + "/models/tmp/" + model_name + ".h5",
                     outputDir + "archive/models/" + model_name + "_" + str(int(file_count)) + ".h5")

            with open(filename, append_write, newline='') as csv_out_file:
                output = csv.writer(csv_out_file, delimiter=';')
                if (append_write == 'w'):
                    output.writerow(['Date', 'Hit', 'Mistake', 'Rel_Error', 'Sensetive', 'Model', 'Comment'])

                output.writerow(
                    [dateTime, hit, mistake, error, sensetive, model_name + "_" + str(int(file_count)) + ".h5",
                     comment])
            csv_out_file.close()

        except FileNotFoundError:
            print("Error can't write file")
