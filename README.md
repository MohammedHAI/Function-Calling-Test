# Function-Calling-Test
 Python application for function calling with LLMs.
 
## Details
 
Designed for models that are running on an OpenAI-Compatible API. Currently only supports Meta-Llama-3.1-8B-Instruct.

Functions are defined in main.py and function detection is hardcoded. After detecting a function in the LLM's response, the appropriate call is made and the result is sent back to the LLM for summarization.

## Planned Features

- Use a Flask server to host the front-end rather than terminal
- Allow the user to have many rounds of conversation with the assistant
- Allow the user to save and load their chats
- Add support for more models
- Handle more than one function call per assistant turn
- Support loading settings from configuration files