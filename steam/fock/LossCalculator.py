import numpy as np

class LossCalculator:
    def __init__(self, batch_num):
        self.MSE = []
        self.RMSE = []
        self.MAE = []
        self.R2 = []
        self.temp_MSE = []
        self.temp_RMSE = []
        self.temp_MAE = []
        self.temp_R2 = []
        self.batch_num = batch_num
        self.temp_length = 0
        self.length = 0
    def evaluate(self, y, y_pred):
        mse = np.mean(np.square(y - y_pred), axis=0)[0]
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y - y_pred), axis=0)[0]
        r2 = 1 - np.sum(np.square(y_pred - y)) / np.sum(np.square(y - np.mean(y)))
        self.temp_MSE.append(mse)
        self.temp_RMSE.append(rmse)
        self.temp_MAE.append(mae)
        self.temp_R2.append(r2)
        self.temp_length += 1
        if self.length == self.batch_num:
            self.MSE.append(np.mean(self.temp_MSE))
            self.RMSE.append(np.mean(self.temp_RMSE))
            self.MAE.append(np.mean(self.temp_MAE))
            self.R2.append(np.mean(self.temp_R2))
            self.temp_MSE = []
            self.temp_RMSE = []
            self.temp_MAE = []
            self.temp_R2 = []
            self.temp_length = 0
            self.length += 1
        return mse, rmse, mae, r2
    def getLoss(self):
        return {"MSE": self.MSE, "RMSE": self.RMSE, "MAE": self.MAE, "R2": self.R2}