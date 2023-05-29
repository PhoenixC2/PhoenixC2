package communication

import (
	"encoding/json"
	"io"
	"net/http"
	"strings"
)

var Url string
var UserAgent string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78"

func SetUrl(url string) {
	Url = url
}

func SetUserAgent(userAgent string) {
	UserAgent = userAgent
}

func createRequest(method string, route string) (req *http.Request, err error) {
	req, err = http.NewRequest(method, Url+route, nil)
	if err != nil {
		return
	}
	req.Header.Set("User-Agent", UserAgent)
	return
}

func GetRequest(route string) (response *http.Response, err error) {
	req, err := createRequest("GET", route)
	if err != nil {
		return
	}
	client := &http.Client{}
	response, err = client.Do(req)
	return
}

func PostRequest(route string, data map[string]interface{}) (response *http.Response, err error) {
	req, err := createRequest("POST", route)
	if err != nil {
		return
	}
	req.Header.Set("Content-Type", "application/json")

	jsonData, err := json.Marshal(data)

	if err != nil {
		return
	}

	req.Body = io.NopCloser(strings.NewReader(string(jsonData)))
	client := &http.Client{}
	response, err = client.Do(req)

	return
}
