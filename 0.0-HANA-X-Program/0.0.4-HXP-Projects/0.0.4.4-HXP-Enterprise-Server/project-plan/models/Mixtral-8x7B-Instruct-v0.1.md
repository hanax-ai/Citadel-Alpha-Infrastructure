# Install LLM serving framework from pip:
pip install vllm

# Load and run the model:
vllm serve "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'