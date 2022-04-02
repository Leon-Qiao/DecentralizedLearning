import numpy as np

class Adam:
    Beta1 = 0.9
    Beta2 = 0.99
    epislon = 1e-8
    def __init__(self):
        self.m = 0
        self.v = 0
        self.t = 0
    def apply_gradients(self, grads, vars, lr):
        self.t += 1
        self.m = Adam.Beta1 * self.m + (1 - Adam.Beta1) * grads
        self.v = Adam.Beta2 * self.v + (1 - Adam.Beta2) * grads**2
        m_h = self.m / (1 - Adam.Beta1**self.t)
        v_h = self.v / (1 - Adam.Beta2**self.t)
        vars -= lr * m_h / (v_h**0.5 + Adam.epislon)