# Install LLM serving framework from pip:
pip install vllm

# Load and run the model:
vllm serve "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/chat/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
		"messages": [
			{
				"role": "user",
				"content": "What is the capital of France?"
			}
		]
	}'