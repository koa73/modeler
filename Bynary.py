#!/usr/bin/env python3

import tensorflow as tf


class Binary(tf.keras.layers.Layer):

    def __init__(self, trainable=True, name=None, dtype=None, dynamic=False, **kwargs):
        self.idx = kwargs.get('idx', 1)
        super().__init__(trainable, name, dtype, dynamic)

    def call(self, inputs, **kwargs):
        return tf.math.multiply(tf.one_hot(tf.math.argmax(inputs, axis=1), tf.shape(inputs)[1]),
                                tf.one_hot(self.idx, tf.shape(inputs)[1]))
