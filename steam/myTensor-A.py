import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from fock import layers
from fock import LossCalculator
import midware
import requests
import json

num_epochs = 150
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
        self.X_train, self.X_vt, self.y_train, self.y_vt = train_test_split(self.X, self.y, test_size=0.4, random_state=0)
        self.X_vali, self.X_test, self.y_vali, self.y_test = train_test_split(self.X_vt, self.y_vt, test_size=0.5, random_state=0)
    def get_batch(self, batch_size=0, mode='train'):
        if mode == 'train':
            index = np.random.randint(0, len(self.y_train), batch_size)
            return self.X_train[index], self.y_train[index]
        if mode == 'test':
            return self.X_test, self.y_test
        if mode == 'validate':
            return self.X_vali, self.y_vali

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

if __name__ == '__main__':
    model = MLP(frame=(1, 2))
    data_loader = DataLoader()
    data_transfer = midware.DataTransfer("http://127.0.0.1:8000", "Steam_MLP")
    data_transfer.initModel([data_loader.X.shape[1], model.dense1.units, model.dense2.units, model.dense3.units])
    num_batch = data_loader.X_train.shape[0] // batch_size
    valiLossCalculator = LossCalculator(1)
    lossCalculator = LossCalculator(num_batch)
    for epoch_index in range(num_epochs):
        for batch in range(num_batch):
            X, y = data_loader.get_batch(batch_size=batch_size)
            #X = np.array([[2, 3, 4],[7,8,9]])
            #y = np.array([[4], [5]])
            y_pred = model(X)
            model.gradient(y_pred - y, learning_rate)
            lossCalculator.evaluate(y, y_pred)
        # lossDic = {"MSE": mse, "RMSE": rmse, "MAE": mae, "R2": r2}
        # requests.get(url = "http://127.0.0.1:8002/putLoss/A/" + json.dumps(lossDic))
        X_v, y_v = data_loader.get_batch(mode='validate')
        y_v_pred = model(X_v)
        valiLossCalculator.evaluate(y_v, y_v_pred)
    d = {"TrainLoss": lossCalculator.getLoss(), "ValidateLoss": valiLossCalculator.getLoss()}
    f = open('A.log', 'w')
    f.write(json.dumps(d))
    f.close()

    X_t, y_t = data_loader.get_batch(mode="test")
    testLossCalculator = LossCalculator(1)
    y_t_pred = model(X_t)
    testLossCalculator.evaluate(y_t, y_t_pred)
    print(testLossCalculator.getLoss())

