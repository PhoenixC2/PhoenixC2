package types

type Module struct {
	Name              string   `json:"name"`
	Admin             bool     `json:"admin"`
	Language          string   `json:"language"`
	Code_type         string   `json:"code_type"`
	Execution_methods []string `json:"execution_methods"`
}