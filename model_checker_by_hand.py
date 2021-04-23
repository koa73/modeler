#!/usr/bin/env python3
# Проверка качества моделей в каталоге

import modelMaker as d

data = d.ModelMaker()

source_path = '/models/archive/complex/4/'
comment_in_log = ""
pattern_file_name = 'weights_b25_150_'
output_log = "complex/4/check_complex"

# Load test data
X_down, y_down = data.get_check_data('test', 'DOWN_b38', '2D')
X_up, y_up = data.get_check_data('test', 'UP_b38', '2D')
X_none, y_none = data.get_check_data('test', 'NONE_b38', '2D')

for i in range(70, 71):

    file_mame = pattern_file_name + str(i)
    model = data.model_loader(file_mame, source_path)

    y_up_pred = model.predict([X_up])
    y_none_pred = model.predict([X_none])
    y_down_pred = model.predict([X_down])

    data.check_single_model(y_up_pred, y_none_pred, y_down_pred, file_mame, comment_in_log, False, output_log)