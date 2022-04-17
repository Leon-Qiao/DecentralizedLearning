import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import fock.layers as layers
import matplotlib.pyplot as plt
import midware


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
    def __init__(self, frame=(1, 1)):
        self.dense1 = layers.Dense(units=128, activation='Relu', frame=frame)
        self.dense2 = layers.Dense(units=64, activation='Relu', frame=frame)
        self.dense3 = layers.Dense(units=1, frame=frame)
    def __call__(self, x):
        x = self.dense1(x)
        x = self.dense2(x)
        x = self.dense3(x)
        return x
    def gradient(self, gradChain, learning_rate):
        gradChain = self.dense3.backward(gradChain)
        dense3_grad = data_transfer.upload("dense3", self.dense3.BEGIN_INDEX, self.dense3.grad)
        self.dense3.adam.apply_gradients(dense3_grad, self.dense3.weight, learning_rate)
        
        gradChain = self.dense2.backward(gradChain)
        dense2_grad = data_transfer.upload("dense2", self.dense2.BEGIN_INDEX, self.dense2.grad)
        self.dense2.adam.apply_gradients(dense2_grad, self.dense2.weight, learning_rate)
        
        gradChain = self.dense1.backward(gradChain)
        dense1_grad = data_transfer.upload("dense1", self.dense1.BEGIN_INDEX, self.dense1.grad)
        self.dense1.adam.apply_gradients(dense1_grad, self.dense1.weight, learning_rate)

class LossCalculator:
    def __init__(self):
        self.MSE = []
        self.RMSE = []
        self.MAE = []
        self.R2 = []
        self.length = 0
    def calculate(self, y, y_pred):
        mse = np.mean(np.square(y - y_pred), axis=0)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y - y_pred), axis=0)
        r2 = 1 - np.sum(np.square(y_pred - y)) / np.sum(np.square(y - np.mean(y_pred)))
        self.MSE.append(mse)
        self.RMSE.append(rmse)
        self.MAE.append(mae)
        self.R2.append(r2)
        self.length += 1

if __name__ == '__main__':
    model = MLP(frame=(1, 2))
    data_loader = DataLoader()
    data_transfer = midware.DataTransfer("Steam_MLP")
    data_transfer.initModel([data_loader.X.shape[1], model.dense1.units, model.dense2.units, model.dense3.units])
    lossCalculator = LossCalculator()
    for epoch_index in range(num_epochs):
        X, y = data_loader.get_batch(batch_size=batch_size)
        #X = np.array([[2, 3, 4],[7,8,9]])
        #y = np.array([[4], [5]])
        y_pred = model(X)
        lossCalculator.calculate(y, y_pred)
        model.gradient(y_pred - y, learning_rate)
    x = [i for i in range(0, lossCalculator.length, 3)]
    plt.subplot(2, 2, 1)
    plt.plot(x, lossCalculator.MSE[::3], color='#403540', linewidth=1.0, linestyle='-')
    plt.ylabel('MSE误差', fontproperties="SimSun")
    plt.xlabel('训练轮次', fontproperties="SimSun")

    plt.subplot(2, 2, 2)
    plt.plot(x, lossCalculator.RMSE[::3], color='#566273', linewidth=1.0, linestyle='-')
    plt.ylabel('RMSE误差', fontproperties="SimSun")
    plt.xlabel('训练轮次', fontproperties="SimSun")

    plt.subplot(2, 2, 3)
    plt.plot(x, lossCalculator.MAE[::3], color='#c5a794', linewidth=1.0, linestyle='-')
    plt.ylabel('MAE误差', fontproperties="SimSun")
    plt.xlabel('训练轮次', fontproperties="SimSun")

    plt.subplot(2, 2, 4)
    plt.plot(x, lossCalculator.R2[::3], color='#927470', linewidth=1.0, linestyle='-')
    plt.ylabel('R2误差', fontproperties="SimSun")
    plt.xlabel('训练轮次', fontproperties="SimSun")

    plt.tight_layout()
    plt.show()



