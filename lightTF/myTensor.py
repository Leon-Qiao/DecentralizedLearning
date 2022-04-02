import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import fock.layers as layers
import matplotlib.pyplot as plt


num_epochs = 500
batch_size = 128
learning_rate = 0.0003

class DataLoader:
    def __init__(self):
        self.zhengqi_train = pd.read_table('./zhengqi_train.txt',encoding='utf-8')
        #self.zhengqi_test = pd.read_table('./zhengqi_test.txt',encoding='utf-8')
        self.X = np.array(self.zhengqi_train.drop(['target'], axis = 1))
        self.y = np.array(self.zhengqi_train.target)
        self.mmX = MinMaxScaler()
        #self.mmY = MinMaxScaler()
        self.X = self.mmX.fit_transform(self.X)
        #self.y = self.mmY.fit_transform(self.y.reshape(-1, 1))
        self.y = self.y.reshape(-1, 1)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.3, random_state=0)
    def get_batch(self, batch_size=0, mode='train'):
        if mode == 'train':
            index = np.random.randint(0, len(self.y_train), batch_size)
            return self.X_train[index], self.y_train[index]
        if mode == 'test':
            return self.X_test, self.y_test

class MLP:
    def __init__(self):
        self.dense1 = layers.Dense(units=128, activation='Relu')
        self.dense2 = layers.Dense(units=64, activation='Relu')
        self.dense3 = layers.Dense(units=1)
    def __call__(self, x):
        x = self.dense1(x)
        x = self.dense2(x)
        x = self.dense3(x)
        return x
    def gradient(self, gradChain, learning_rate):
        gradChain = self.dense3.backward(gradChain, learning_rate)
        gradChain = self.dense2.backward(gradChain, learning_rate)
        gradChain = self.dense1.backward(gradChain, learning_rate)

if __name__ == '__main__':
    model = MLP()
    data_loader = DataLoader()
    l = []
    for epoch_index in range(num_epochs):
        X, y = data_loader.get_batch(batch_size=batch_size)
        #X = np.array([[2, 3, 4],[7,8,9]])
        #y = np.array([[4], [5]])
        y_pred = model(X)
        loss = np.mean(np.square(y - y_pred), axis=0)
        model.gradient(y_pred - y, learning_rate)
        print(loss)
        l.append(loss)
    x = [i for i in range(len(l))]
    plt.plot(x, l)
    plt.show()


