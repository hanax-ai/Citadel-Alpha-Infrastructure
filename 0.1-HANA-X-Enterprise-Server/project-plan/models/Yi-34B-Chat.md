# Install vLLM from pip:
pip install vllm

# Load and run the model:
vllm serve "01-ai/Yi-34B-Chat"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "01-ai/Yi-34B-Chat",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'