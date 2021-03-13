#!/usr/bin/env python3

import tensorflow as tf


class Amplifier(tf.keras.layers.Layer):

    def __init__(self):
        super(Amplifier, self).__init__()
        # pattern 2D matrix
        self.f = tf.constant([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]], dtype='float32')

    def call(self, inputs, training=None, mask=None):
        # return index of max value
        x = tf.math.argmax(inputs, axis=None, output_type=tf.dtypes.int32, name=None)
        # get factor from f constant as 1D matrix form
        y = tf.reshape(tf.slice(self.f, [x, 0], [1, 3]), [3])
        # multiply input on the pattern matrix
        return tf.math.multiply(inputs, y)
