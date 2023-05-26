package types

type Task struct {
	ID      int                    `json:"id"`
	Name    string                 `json:"name"`
	Action  string                 `json:"action"`
	Args    map[string]interface{} `json:"args"`
	Output  interface{}            `json:"output"`
	Success bool                   `json:"success"`
}