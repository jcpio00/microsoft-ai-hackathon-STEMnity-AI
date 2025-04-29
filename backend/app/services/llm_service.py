
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from app.core import config

# Constants
GITHUB_API_ENDPOINT = "https://models.github.ai/inference" # Standard endpoint for GitHub Models

# Ensure required configuration is loaded
if not config.GITHUB_PAT or not config.GITHUB_MODEL_ID:
    raise ValueError("GITHUB_PAT and GITHUB_MODEL_ID must be set in the .env file")

# Initialize the client
# Check SDK documentation if you encounter issues.
try:
    credential = AzureKeyCredential(config.GITHUB_PAT)  # <-- Remove "Bearer "
    client = ChatCompletionsClient(endpoint=GITHUB_API_ENDPOINT, credential=credential)
except Exception as e:
    print(f"Error initializing ChatCompletionsClient: {e}")
    client = None # Ensure client is None if initialization fails

# Define the core function to get a response from the LLM
async def get_llm_response(user_prompt: str) -> str:
    """
    Sends a prompt to the configured GitHub Model and returns the response.
    """
    if not client:
        return "Error: LLM client failed to initialize. Check credentials and endpoint."

    # Use dicts for messages as expected by the API
    messages = [
        {"role": "system", "content": "You are a helpful and friendly STEM tutor for K-12 students. Explain concepts clearly and concisely. Focus on educational content."},
        {"role": "user", "content": user_prompt}
    ]

    try:
        print(f"Sending request to model: {config.GITHUB_MODEL_ID}")
        response = client.complete(  
            model=config.GITHUB_MODEL_ID,
            messages=messages,
            temperature=0.8,
            top_p=0.1,
            max_tokens=2048
        )

        if response.choices and len(response.choices) > 0:
            ai_reply = response.choices[0].message.content
            print(f"Received response: {ai_reply[:100]}...")
            return ai_reply
        else:
            print("Warning: Received no choices in the response.")
            return "Sorry, I couldn't generate a response."

    except HttpResponseError as e:
        print(f"Error calling GitHub Models API: {e.status_code} - {e.reason}")
        print(f"Response body: {e.response.text() if e.response else 'N/A'}")
        if e.status_code == 401:
             return "Error: Authentication failed. Check your GitHub PAT."
        if e.status_code == 404:
             return f"Error: Model '{config.GITHUB_MODEL_ID}' not found or endpoint incorrect."
        if e.status_code == 429:
             return "Error: Rate limit exceeded. Please try again later."
        return f"Sorry, an API error occurred ({e.status_code})."
    except Exception as e:
        print(f"An unexpected error occurred in llm_service: {e}")
        return "Sorry, an unexpected error occurred while processing your request."
