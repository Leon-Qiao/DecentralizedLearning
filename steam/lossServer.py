from fastapi import FastAPI
import json

app = FastAPI()

loss = {"A": [], "B": []}

@app.get("/")
async def root():
	return {"message": "Hello World"}

@app.get("/putLoss/{peer}/{content}")
async def putLoss(peer, content):
	loss[peer].append(json.loads(content))

@app.get("/getLoss/{peer}/{position}")
async def getLoss(peer, position: int):
	return loss[peer][position:]

