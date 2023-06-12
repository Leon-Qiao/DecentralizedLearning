# DecentralizedLearning

## Prerequisite

### Hyperledger Fabric

An [installation tutorial video](https://www.bilibili.com/video/BV1g3411h71Z) available but in Chinese.

Or

Follow the [official doc](https://hyperledger-fabric.readthedocs.io/en/latest/getting_started.html) of the Hyperledger Fabric.

## Start

### Startup Fabric network

Copy **chaincode/fabai/go/** and **fabai/** files from this project to your newly installed Fabric.

Make sure you are in **fabai/** directory

``./startFabric.sh``

### Startup first blockchain node

Open a new terminal window

Make sure you are in **fabai/go/** directory

``go run fabaiAPI_org1.go``

### Startup second blockchain node

Open a new terminal window

Make sure you are in **fabai/go2/** directory

``go run fabaiAPI_org2.go``

### Startup Grad Server

Open a new terminal window

Make sure you are in **steam/** directory

``uvicorn GradServer:app --port 8003 --reload``

### Run first AI-training node

Open a new terminal window

Make sure you are in **steam/** directory

``python myTensor-A.py``

### Run second AI-training node

Open a new terminal window

Make sure you are in **steam/** directory

``python myTensor-B.py``

## Visualization

### Startup Loss Server

Open a new terminal window

Make sure you are in **steam/** directory

``uvicorn lossServer:app --port 8004 --reload``

### Startup website

Open a new terminal window

Make sure you are in **pyecharts_django_demo/** directory

``python manage.py runserver 127.0.0.1:8005``

Open a browser and visit 127.0.0.1:8005
