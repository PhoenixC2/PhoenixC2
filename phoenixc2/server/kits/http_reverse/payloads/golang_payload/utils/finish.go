package utils

import (
	"net/http"
	types "golang_payload/types"
	com "golang_payload/communication"
)

func Finish(task types.Task, output any, success bool) (res *http.Response, err error){
	// Create json payload
	payload := map[string]interface{}{
		"output": output,
		"success": success,
	}
	if err != nil {
		return
	}

	// Send the payload
	res, err = com.PostRequest("/finish/"+task.Name, payload)

	if err != nil || res.StatusCode != http.StatusOK {
		return
	}

	defer res.Body.Close()

	return
}