# Install LLM serving framework from pip:
pip install vllm

# Load and run the model:
vllm serve "openchat/openchat-3.5-0106"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "openchat/openchat-3.5-0106",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'