import requests
import json
import pandas as pd
import numpy as np
import math

def lossFuncMSE(y_pred):
	mse = (1 / X.shape[0]) * ((y_pred - y) ** 2).sum()
	return mse

def lossFuncMAE(y_pred):
	mae = (1 / X.shape[0]) * (abs(y_pred - y)).sum()
	return mae

def lossFuncR2(y_pred):
	r2 = 1 - (((y_pred - y) ** 2).sum() / ((y - y_pred.mean()) ** 2).sum())
	return r2

def gradFunc():
	pParam = [0 for i in range(len(param))]
	t = 0
	for i in range(len(param)):
		t += param[i] * X.iloc[: , i]
	t = 2 * (t + bias - y) / X.shape[0]
	for i in range(len(pParam)):
		pParam[i] = (t * X.iloc[: , i]).mean()
	pBias = t.mean()
	pParam.append(pBias)
	return pParam

data = json.loads(open("zhengqi_A.txt", 'r').read())
data = np.array(data)
df = pd.DataFrame(data=data)

X = df.iloc[:,:-1]
y = df.iloc[:,-1]

localEpoch = -1

while localEpoch < 70001:
	s = requests.get("http://127.0.0.1:8000/getParam", headers={'Connection': 'close'}).text
	l, globalEpoch = json.loads(s)
	if globalEpoch == localEpoch:
		continue
	localEpoch = globalEpoch
	print("=== {}".format(localEpoch))
	param = l[:-1]
	bias = l[-1]
	y_pred = (X * param).sum(axis=1) + bias
	mse = lossFuncMSE(y_pred)
	rmse = math.sqrt(mse)
	mae = lossFuncMAE(y_pred)
	r2 = lossFuncR2(y_pred)
	print("MSE: {}".format(mse))
	print("RMSE: {}".format(rmse))
	print("MAE: {}".format(mae))
	print("R2: {}".format(r2))
	pParam = gradFunc()
	httpS = "http://127.0.0.1:8000/putParam/{}/{}/{}".format(json.dumps(pParam), 'A', globalEpoch)
	requests.get(httpS)
