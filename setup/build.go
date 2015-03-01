package main

import (
	"database/sql"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"gopkg.in/yaml.v2"
	"io/ioutil"
	"os"
	"runtime"
)

var DATA_PATH string
var DB_PATH string
var SCHEMA_PATH string

//allows use of all cores
func init() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	DATA_PATH = "."
	SCHEMA_PATH = DATA_PATH + "/a.yaml"
	DB_PATH = DATA_PATH + "/db"
}

type Schema struct {
	Columns   map[string][][]string
	Relations map[string][][]string
}

func main() {
	//load yaml
	//see http://godoc.org/gopkg.in/yaml.v2
	schema_file, err := ioutil.ReadFile(SCHEMA_PATH)
	if err != nil {
		fmt.Errorf("error: %v", err)
		panic(err)
	}
	schema := Schema{}
	err = yaml.Unmarshal([]byte(string(schema_file)), &schema)
	if err != nil {
		fmt.Errorf("error: %v", err)
		panic(err)
	}

	//remove old db
	os.Remove(DB_PATH)

	//connect to db
	//see https://github.com/mattn/go-sqlite3/blob/master/_example/simple/simple.go
	//and http://godoc.org/github.com/mattn/go-sqlite3#SQLiteConn.Begin
	db, err := sql.Open("sqlite3", DB_PATH)
	if err != nil {
		fmt.Errorf("error: %v", err)
		panic(err)
	}
	defer db.Close() //puts on stack for execution after function returns

	//load tables
	tx, err := db.Begin()
	if err != nil {
		fmt.Errorf("error: %v", err)
		panic(err)
	}

	for k, v := range schema.Columns {
		cmd := fmt.Sprintf("CREATE TABLE %s\n\t(\n", k)
		for i, a := range v {
			cmd += fmt.Sprintf("\t\t%s\t\t%s", a[0], a[1])
			if i < len(v)-1 {
				cmd += ",\n"
			}
		}
		if len(schema.Relations[k]) > 0 {
			cmd += ",\n"
		}
		for _, k := range schema.Relations[k] {
			cmd += fmt.Sprintf("\t\tFOREIGN KEY(%s)\tREFERENCES %s(%s)\n", k[0], k[1], k[0])
		}
		cmd += "\t)"

		fmt.Println(cmd)

		_, err = tx.Exec(cmd)
		if err != nil {
			fmt.Errorf("error: %v", err)
			panic(err)
		}
	}
	tx.Commit()
}
