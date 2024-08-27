# Function-Calling-Test
 Python application for function calling with LLMs.
 
## Details
 
Designed for models that are running on an OpenAI-Compatible API. Currently only supports Meta-Llama-3.1-8B-Instruct.

Functions are defined in main.py and function detection is hardcoded. After detecting a function in the LLM's response, the appropriate call is made and the result is sent back to the LLM for summarization.

## Planned Features

In no particular order:
- Use a Flask server to host the front-end rather than terminal
- Add support for more models
- Allow custom functions to accept a varying number of parameters
- Make it possible to select the available functions during the chat session
- Handle more than one function call per assistant turn
- Support loading settings from configuration files
- Allow the function calling system to interact with the assistant autonomously
- Add type hints, comments, clean up the code