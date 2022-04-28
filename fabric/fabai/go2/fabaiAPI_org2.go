/*
Copyright 2020 IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
*/

package main

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strconv"

	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/gateway"
	
	"github.com/gin-gonic/gin"
	"net/http"
)

func main() {
	
	ModelList := map[string]string{"steam": "MODEL0"}
	
	os.Setenv("DISCOVERY_AS_LOCALHOST", "true")
	wallet, err := gateway.NewFileSystemWallet("wallet")
	if err != nil {
		fmt.Printf("Failed to create wallet: %s\n", err)
		os.Exit(1)
	}

	if !wallet.Exists("appUser") {
		err = populateWallet(wallet)
		if err != nil {
			fmt.Printf("Failed to populate wallet contents: %s\n", err)
			os.Exit(1)
		}
	}

	ccpPath := filepath.Join(
		"..",
		"..",
		"test-network",
		"organizations",
		"peerOrganizations",
		"org1.example.com",
		"connection-org1.yaml",
	)

	gw, err := gateway.Connect(
		gateway.WithConfig(config.FromFile(filepath.Clean(ccpPath))),
		gateway.WithIdentity(wallet, "appUser"),
	)
	if err != nil {
		fmt.Printf("Failed to connect to gateway: %s\n", err)
		os.Exit(1)
	}
	defer gw.Close()

	network, err := gw.GetNetwork("mychannel")
	if err != nil {
		fmt.Printf("Failed to get network: %s\n", err)
		os.Exit(1)
	}

	contract := network.GetContract("fabai")
	
	router := gin.Default()
	
	router.GET("/queryallmodels", func(c *gin.Context) {
		var result []byte
		
		result, err := contract.EvaluateTransaction("QueryAllModels")
		if err != nil {
			fmt.Printf("Failed to evaluate transaction: %s\n", err)
			os.Exit(1)
		}
		fmt.Println(string(result))
		
		c.String(http.StatusOK, string(result))
	})

	
	router.GET("/initGrad/:ModelName/:Frame", func(c *gin.Context) {
		var result []byte
		modelName := c.Param("ModelName")
        	frame := c.Param("Frame")
        	
        	ModelList[modelName] = "MODEL" + strconv.Itoa(len(ModelList))
        	
        	result, err = contract.SubmitTransaction("CreateModel", ModelList[modelName], modelName, frame)
		if err != nil {
			fmt.Printf("Failed to submit transaction: %s\n", err)
			os.Exit(1)
		}
		fmt.Println(string(result))
		
		c.String(http.StatusOK, string(result))
	})
	

	router.GET("/getGrad/:ModelName/:LayerName", func(c *gin.Context) {
		var result []byte
		modelName := c.Param("ModelName")
		layerName := c.Param("LayerName")
		
		result, err = contract.EvaluateTransaction("getGrad", ModelList[modelName], layerName)
		if err != nil {
			fmt.Printf("Failed to evaluate transaction: %s\n", err)
			os.Exit(1)
		}
		fmt.Println(string(result))
		
		c.String(http.StatusOK, string(result))
	})
	
	router.GET("/putGrad/:ModelName/:LayerName/:Position/:grad", func(c *gin.Context) {
		var result []byte
		modelName := c.Param("ModelName")
		layerName := c.Param("LayerName")
		position := c.Param("Position")
		grad := c.Param("grad")
		result, err = contract.SubmitTransaction("putGrad", ModelList[modelName], layerName, position, grad)
		if err != nil {
			fmt.Printf("Failed to submit transaction: %s\n", err)
			os.Exit(1)
		}

		fmt.Println(string(result))
		
		c.String(http.StatusOK, string(result))
	})

	
	router.Run(":8001")
}

func populateWallet(wallet *gateway.Wallet) error {
	credPath := filepath.Join(
		"..",
		"..",
		"test-network",
		"organizations",
		"peerOrganizations",
		"org1.example.com",
		"users",
		"User1@org1.example.com",
		"msp",
	)

	certPath := filepath.Join(credPath, "signcerts", "cert.pem")
	// read the certificate pem
	cert, err := ioutil.ReadFile(filepath.Clean(certPath))
	if err != nil {
		return err
	}

	keyDir := filepath.Join(credPath, "keystore")
	// there's a single file in this dir containing the private key
	files, err := ioutil.ReadDir(keyDir)
	if err != nil {
		return err
	}
	if len(files) != 1 {
		return errors.New("keystore folder should have contain one file")
	}
	keyPath := filepath.Join(keyDir, files[0].Name())
	key, err := ioutil.ReadFile(filepath.Clean(keyPath))
	if err != nil {
		return err
	}

	identity := gateway.NewX509Identity("Org1MSP", string(cert), string(key))

	err = wallet.Put("appUser", identity)
	if err != nil {
		return err
	}
	return nil
}
