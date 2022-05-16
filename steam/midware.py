import requests
import json
import numpy as np

class DataTransfer:
    def __init__(self, url, modelName):
        self.url = url
        self.modelName = modelName

    def initModel(self, units):
        modelConf = {}
        for i in range(1, len(units)):
            modelConf["dense" + str(i)] = (units[i - 1], units[i])
        requests.get("{}/initGrad/{}/{}".format(self.url, self.modelName, json.dumps(modelConf)))

    def upload(self, layerName, position, grad):
        html = requests.get("{}/putGrad/{}/{}/{}/{}".format(self.url, self.modelName, layerName, position, grad.tolist()))
        text = html.text
        return np.array(json.loads(text), dtype=np.float64)
    
    def download(self, layerName):
        html = requests.get("{}/getGrad/{}/{}".format(self.url, self.modelName, layerName))
        text = html.text
        return np.array(json.loads(text), dtype=np.float64)
