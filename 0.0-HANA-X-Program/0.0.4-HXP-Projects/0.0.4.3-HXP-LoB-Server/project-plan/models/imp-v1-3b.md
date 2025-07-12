# Install AI model serving framework:
pip install transformers torch

# Load and run the model:
# Model: MILVLG/imp-v1-3b (Ultra-lightweight Agent)
# Server configuration for HXP LoB Server

# Call the server using curl:
curl -X POST "http://localhost:8000/v1/completions" \
	-H "Content-Type: application/json" \
	--data '{
		"model": "MILVLG/imp-v1-3b",
		"prompt": "Once upon a time,",
		"max_tokens": 512,
		"temperature": 0.5
	}'