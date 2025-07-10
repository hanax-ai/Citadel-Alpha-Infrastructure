# Install vLLM from pip:
pip install vllm

# Load and run the model:
vllm serve "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'