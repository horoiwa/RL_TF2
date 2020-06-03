import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import tensorflow as tf
import tensorflow.keras.layers as kl


class QNetwork(tf.keras.Model):

    def __init__(self, action_space, lr=0.001):

        super(QNetwork, self).__init__()

        self.action_space = action_space

        self.dense1 = kl.Dense(128, activation="relu", name="dense1",
                               kernel_initializer="he_normal")

        self.dense2 = kl.Dense(128, activation="relu", name="dense2",
                               kernel_initializer="he_normal")

        self.out = kl.Dense(action_space, name="output",
                            kernel_initializer="he_normal")

        self.optimizer = tf.keras.optimizers.Adam(lr=lr)

        self.loss_func = tf.losses.Huber()

    @tf.function
    def call(self, x):
        x = self.dense1(x)
        x = self.dense2(x)
        out = self.out(x)
        return out

    @tf.function
    def huber_loss(self, errors, weights):
        errors = errors * weights
        is_smaller_error = tf.abs(errors) < 1.0
        squared_loss = tf.square(errors) * 0.5
        linear_loss = tf.abs(errors) - 0.5

        return tf.where(is_smaller_error, squared_loss, linear_loss)

    def predict(self, states):
        states = np.atleast_2d(states).astype(np.float32)
        return self(states).numpy()

    def update(self, states, selected_actions, target_values, weights):

        with tf.GradientTape() as tape:
            selected_actions_onehot = tf.one_hot(selected_actions,
                                                 self.action_space)

            selected_action_values = tf.reduce_sum(
                self(states) * selected_actions_onehot, axis=1, keepdims=True)

            td_errors = target_values - selected_action_values

            loss = tf.reduce_mean(self.huber_loss(td_errors, weights))

        grads = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.trainable_variables))

        return td_errors.numpy().flatten()


if __name__ == "__main__":
    states = np.array([[-0.10430691, -1.55866031, 0.19466207, 2.51363456],
                       [-0.10430691, -1.55866031, 0.19466207, 2.51363456],
                       [-0.10430691, -1.55866031, 0.19466207, 2.51363456]])
    states.astype(np.float32)
    actions = [0, 1, 1]
    target_values = [1, 1, 1]
    qnet = QNetwork(action_space=2)
    pred = qnet.predict(states)

    print(pred)

    qnet.update(states, actions, target_values)
