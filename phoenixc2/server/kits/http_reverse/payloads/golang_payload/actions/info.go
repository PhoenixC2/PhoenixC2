package actions

import (
	"os"
	"os/user"
	"runtime"
	types "golang_payload/types"
	utils "golang_payload/utils"
)

func SystemInfo() (data map[string]interface{}) {
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

	data = map[string]interface{}{

		"hostname":     hostname,
		"os":           runtime.GOOS,
		"architecture": runtime.GOARCH,
		"user":         username,
		"admin":        false,
	}

	return
}

func SystemInfoFromTask(task types.Task) {
	utils.Finish(task, SystemInfo(), true)
}