package utils

import (
	"golang_payload/comms"
	types "golang_payload/types"
	"net/http"
)

func Finish(task types.Task, output any, success bool) (res *http.Response, err error) {
	// Create json payload
	payload := map[string]interface{}{
		"output":  output,
		"success": success,
	}
	if err != nil {
		return
	}

	// Send the payload
	res, err = comms.PostRequest("/finish/"+task.Name, payload)

	if err != nil || res.StatusCode != http.StatusOK {
		return
	}

	defer res.Body.Close()

	return
}
