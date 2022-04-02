import numpy as np
import fock.optimizers as optimizers
import math

class Dense:
    def __init__(self, units, activation=None):
        self.units = units
        self.activation = activation
        self.weight = None
        self.x = None
        self.cell = None
        self.grad = None
        self.adam = optimizers.Adam()
    def __call__(self, input):
        self.x = input.copy()
        if self.weight is None:
            fan_in = self.x.shape[-1]
            fan_out = self.units
            limit = math.sqrt(6 / (fan_in + fan_out))
            self.weight = np.random.uniform(-limit, limit, size=(fan_in, fan_out))
            #self.weight = np.ones(shape=(self.x.shape[-1], self.units), dtype=np.float64)
        self.cell = np.dot(self.x, self.weight)
        if self.activation is not None:
            if self.activation == 'Sigmoid':
                self.cell = 1 / (1 + np.exp(-self.cell))
            if self.activation == 'Tahn':
                self.cell = (np.exp(self.cell) - np.exp(-self.cell)) / (np.exp(self.cell) + np.exp(-self.cell))
            if self.activation == 'Relu':
                self.cell[self.cell <= 0] = 0
        return self.cell

    def backward(self, gradChain, lr):
        if self.activation == "Sigmoid":
            gradChain *= self.cell * (1 - self.cell)
        if self.activation == "Tahn":
            gradChain *= (1 - self.cell**2)
        if self.activation=="Relu":
            self.cell[self.cell <= 0] = 0
            self.cell[self.cell > 0] = 1
            gradChain = gradChain * self.cell
        self.grad = np.dot(self.x.T, gradChain) / gradChain.shape[0] * 2
        gradChain = np.dot(gradChain, self.weight.T)
        #self.weight -= lr * self.grad
        self.adam.apply_gradients(self.grad, self.weight, lr)
        return gradChain

