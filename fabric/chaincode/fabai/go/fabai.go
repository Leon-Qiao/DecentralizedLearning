/*
SPDX-License-Identifier: Apache-2.0
*/

package main

import (
        "encoding/json"
        "fmt"
        "strconv"

        "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract provides functions for managing a book
type SmartContract struct {
        contractapi.Contract
}

// Book describes basic details of what makes up a book


type Model struct {
	Name    string  `json:"name"`
	Param   string  `json:"param"`
}

// QueryResult structure used for handling result of query
type QueryResult struct {
        Key    string `json:"Key"`
        Record *Model
}

// InitLedger adds a base set of books to the ledger
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
        models := []Model{
        	Model{Name: "steam1",
        	Param: "",},
        	Model{Name: "steam2",
        	Param: "",},
        }

        for i, model := range models {
                modelAsBytes, _ := json.Marshal(model)
                err := ctx.GetStub().PutState("MODEL"+strconv.Itoa(i), modelAsBytes)

                if err != nil {
                        return fmt.Errorf("Failed to put to world state. %s", err.Error())
                }
        }

        return nil
}

// CreateBook adds a new book to the world state with given details
func (s *SmartContract) CreateModel(ctx contractapi.TransactionContextInterface, modelNumber string, name string) error {
        model := Model{
                Name:      name,
	        Param:     "",
        }

        modelAsBytes, _ := json.Marshal(model)

        return ctx.GetStub().PutState(modelNumber, modelAsBytes)
}

// QueryBook returns the book stored in the world state with given id
func (s *SmartContract) QueryModel(ctx contractapi.TransactionContextInterface, modelNumber string) (*Model, error) {
        modelAsBytes, err := ctx.GetStub().GetState(modelNumber)
        if err != nil {
                return nil, fmt.Errorf("Failed to read from world state. %s", err.Error())
        }

        if modelAsBytes == nil {
                return nil, fmt.Errorf("%s does not exist", modelNumber)
        }

        model := new(Model)
        _ = json.Unmarshal(modelAsBytes, model)

        return model, nil
}

// QueryAllBooks returns all books found in world state
func (s *SmartContract) QueryAllModels(ctx contractapi.TransactionContextInterface) ([]QueryResult, error) {
        startKey := ""
        endKey := ""

        resultsIterator, err := ctx.GetStub().GetStateByRange(startKey, endKey)

        if err != nil {
                return nil, err
        }
        defer resultsIterator.Close()

        results := []QueryResult{}

        for resultsIterator.HasNext() {
                queryResponse, err := resultsIterator.Next()

                if err != nil {
                        return nil, err
                }

                model := new(Model)
                _ = json.Unmarshal(queryResponse.Value, model)


                queryResult := QueryResult{Key: queryResponse.Key, Record: model}
                results = append(results, queryResult)
        }

        return results, nil
}

// ChangeBookPrice updates the price field of book with given id in world state
func (s *SmartContract) ModifyModel(ctx contractapi.TransactionContextInterface, modelNumber string, sParam string) error {
	modiModel, err := s.QueryModel(ctx, modelNumber)

        if err != nil {
                return err
        }
        
        modiModel.Param = sParam
	
        modiModelAsBytes, _ := json.Marshal(modiModel)

        ctx.GetStub().PutState(modelNumber, modiModelAsBytes)
        return nil
}

func main() {

        chaincode, err := contractapi.NewChaincode(new(SmartContract))

        if err != nil {
                fmt.Printf("Error create fabai chaincode: %s", err.Error())
                return
        }

        if err := chaincode.Start(); err != nil {
                fmt.Printf("Error starting fabai chaincode: %s", err.Error())
        }
}
