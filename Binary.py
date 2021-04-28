#!/usr/bin/env python3

import tensorflow as tf


class Binary(tf.keras.layers.Layer):

    def __init__(self, k, name=None, **kwargs):
        super(Binary, self).__init__(name=name)
        self.k = k
        super(Binary, self).__init__(**kwargs)

    def get_config(self):
        config = super(Binary, self).get_config()
        config.update({"k": self.k})
        return config

    def call(self, inputs, **kwargs):
        return tf.math.multiply(tf.one_hot(tf.math.argmax(inputs, axis=1), tf.shape(inputs)[1]),
                                tf.one_hot(self.k, tf.shape(inputs)[1]))
