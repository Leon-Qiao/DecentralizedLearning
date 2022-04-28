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

	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/gateway"
	
	"github.com/gin-gonic/gin"
	"net/http"
)

func main() {
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
		"org3.example.com",
		"connection-org3.yaml",
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

	
	router.GET("/createmodel/:modelNumber/:modelName", func(c *gin.Context) {
		var result []byte
		modelNumber := c.Param("modelNumber")
        	modelName := c.Param("modelName")
        	
        	result, err = contract.SubmitTransaction("CreateModel", modelNumber, modelName)
		if err != nil {
			fmt.Printf("Failed to submit transaction: %s\n", err)
			os.Exit(1)
		}
		fmt.Println(string(result))
		
		c.String(http.StatusOK, string(result))
	})
	

	router.GET("/querymodel/:modelNumber", func(c *gin.Context) {
		var result []byte
		modelNumber := c.Param("modelNumber")
		
		result, err = contract.EvaluateTransaction("QueryModel", modelNumber)
		if err != nil {
			fmt.Printf("Failed to evaluate transaction: %s\n", err)
			os.Exit(1)
		}
		fmt.Println(string(result))
		
		c.String(http.StatusOK, string(result))
	})
	
	router.GET("/modifymodel/:modelNumber/:Param", func(c *gin.Context) {
		var result []byte
		modelNumber := c.Param("modelNumber")
		Param := c.Param("Param")
		_, err = contract.SubmitTransaction("ModifyModel", modelNumber, Param)
		if err != nil {
			fmt.Printf("Failed to submit transaction: %s\n", err)
			os.Exit(1)
		}

		result, err = contract.EvaluateTransaction("QueryModel", modelNumber)
		if err != nil {
			fmt.Printf("Failed to evaluate transaction: %s\n", err)
			os.Exit(1)
		}
		fmt.Println(string(result))
		
		c.String(http.StatusOK, string(result))
	})

	
	router.Run(":8002")
}

func populateWallet(wallet *gateway.Wallet) error {
	credPath := filepath.Join(
		"..",
		"..",
		"test-network",
		"organizations",
		"peerOrganizations",
		"org3.example.com",
		"users",
		"User1@org3.example.com",
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

	identity := gateway.NewX509Identity("Org3MSP", string(cert), string(key))

	err = wallet.Put("appUser", identity)
	if err != nil {
		return err
	}
	return nil
}
