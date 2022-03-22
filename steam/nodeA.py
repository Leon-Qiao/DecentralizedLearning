import pandas as pd
import numpy as np
import time
import math
import json
import requests

learning_rate = 0.03

def initParam(modelID1, modelID2):
	modifyUrl = "http://127.0.0.1:8000/modifymodel/"
	l1 = [0 for i in range(X.shape[1] // 2)]
	s1 = json.dumps(l1)
	html = requests.get(url = "{}{}/{}".format(modifyUrl, modelID1, s1))
	l2 = [0 for i in range(X.shape[1] // 2 + X.shape[1] % 2 + 1)]
	s2 = json.dumps(l2)
	html = requests.get(url = "{}{}/{}".format(modifyUrl, modelID2, s2))

def getParam(modelID1, modelID2):
	queryUrl = "http://127.0.0.1:8000/querymodel/"
	html1 = requests.get(url = queryUrl + modelID1)
	html2 = requests.get(url = queryUrl + modelID2)
	param1 = json.loads(json.loads(html1.text)["param"])
	param2 = json.loads(json.loads(html2.text)["param"])
	return param1 + param2

def putParam(param, modelID):
	modifyUrl = "http://127.0.0.1:8000/modifymodel/"
	s = json.dumps(param)
	html = requests.get(url = "{}{}/{}".format(modifyUrl, modelID, s))

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
	hParam = param[: len(param) // 2]
	pParam = [0 for i in range(len(hParam))]
	t = 0
	for i in range(len(param)):
		t += param[i] * X.iloc[: , i]
	t = 2 * (t + bias - y) / X.shape[0]
	for i in range(len(pParam)):
		pParam[i] = (t * X.iloc[: , i]).mean()
	for i in range(len(pParam)):
		hParam[i] -= learning_rate * pParam[i]
	return hParam

data = json.loads(open("zhengqi_A.txt", 'r').read())
data = np.array(data)
df = pd.DataFrame(data=data)
X = df.iloc[:,:-1]
y = df.iloc[:,-1]

html = requests.get(url = "http://127.0.0.1:8000/querymodel/MODEL0")
if len(json.loads(html.text)["param"]) < 1:
	initParam("MODEL0", "MODEL1")

st = int(round(time.time() * 1000))
epoch = 0

for i in range(70001):
	t = time.time()
	print("=== {} === {}".format(epoch, int(round(t * 1000)) - st))
	epoch += 1
	xparam = getParam("MODEL0", "MODEL1")
	param = xparam[:-1]
	bias = xparam[-1]
	y_pred = (X * param).sum(axis=1) + bias
	mse = lossFuncMSE(y_pred)
	rmse = math.sqrt(mse)
	mae = lossFuncMAE(y_pred)
	r2 = lossFuncR2(y_pred)
	lossDic = {"MSE": mse, "RMSE": rmse, "MAE": mae, "R2": r2}
	requests.get(url = "http://127.0.0.1:8002/putLoss/A/" + json.dumps(lossDic))
	print("MSE: {}".format(mse))
	print("RMSE: {}".format(rmse))
	print("MAE: {}".format(mae))
	print("R2: {}".format(r2))
	param = gradFunc()
	putParam(param, "MODEL0")

