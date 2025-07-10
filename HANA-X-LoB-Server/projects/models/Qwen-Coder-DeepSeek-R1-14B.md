# Install vLLM from pip:
pip install vllm

# Load and run the model:
vllm serve "radna/Qwen-Coder-DeepSeek-R1-14B"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "radna/Qwen-Coder-DeepSeek-R1-14B",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'