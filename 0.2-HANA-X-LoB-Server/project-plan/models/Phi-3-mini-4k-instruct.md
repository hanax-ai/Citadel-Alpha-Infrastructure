# Install vLLM from pip:
pip install vllm

# Load and run the model:
vllm serve "microsoft/Phi-3-mini-4k-instruct"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "microsoft/Phi-3-mini-4k-instruct",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'