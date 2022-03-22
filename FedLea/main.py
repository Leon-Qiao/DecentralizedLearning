from fastapi import FastAPI
import json

app = FastAPI()

learningRate = 0.03

epoch = 0

peerNumber = 2

globalParam = [0 for i in range(39)]

epochDict = {}

@app.get("/")
async def root():
	return {"message": "Hello World"}

@app.get("/putParam/{param}/{id}/{epo}")
async def putParam(param, id, epo: int):
	if id not in epochDict and epo == epoch:
		temp = json.loads(param)
		epochDict[id] = temp
	if peerNumber == len(epochDict):
		FedAVG()

@app.get("/getParam")
async def getParam():
	return globalParam, epoch

def FedAVG():
	global epoch
	l = [0 for i in range(39)]
	for item in epochDict:
		for i in range(len(l)):
			l[i] += epochDict[item][i]
	for i in range(len(l)):
		l[i] /= peerNumber
		globalParam[i] -= learningRate * l[i]
	epochDict.clear()
	epoch += 1
    

