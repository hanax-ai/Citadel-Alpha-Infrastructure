# Install vLLM from pip:
pip install vllm

# Load and run the model:
vllm serve "MILVLG/imp-v1-3b"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "MILVLG/imp-v1-3b",
		"prompt": "Once upon a time,",
		"max_tokens": 512,
		"temperature": 0.5
	}'