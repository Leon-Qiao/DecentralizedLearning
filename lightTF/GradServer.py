from fastapi import FastAPI
import json

models = {}

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/initGrad/{ModelName}/{Frame}")
async def init_grad(ModelName, Frame):
    Frame = json.loads(Frame)
    models[ModelName] = {}
    for k, v in Frame.items():
        models[ModelName][k] = [[0 for i in range(v[1])] for j in range(v[0])]

@app.get("/putGrad/{ModelName}/{LayerName}/{Position}/{grad}")
async def put_grad(ModelName, LayerName, Position: int, grad):
    grad = json.loads(grad)
    models[ModelName][LayerName][Position: Position + len(grad)] = grad
    return models[ModelName][LayerName]

@app.get("/getGrad/{ModelName}/{LayerName}")
async def get_grad(ModelName, LayerName):
    return models[ModelName][LayerName]