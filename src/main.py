# Copyright 2024 Mohammed Al-Islam
#
# This is a rough example and is not suitable for deployment

import litellm
import os
import json
from datetime import date
import time

CONFIG_PATH = "config.json"

# --- functions (limited to max 2 params)

def fun_add(a, b):
    """
        adds 2 numbers and returns the result
    """
    print("called add()")
    result = {'result': a + b}
    return result

def fun_weather(location):
    """
        returns the weather as a hardcoded value
    """
    print("called weather()")
    result = {'weather': 'sunny'}
    return result

def fun_pwd():
    """
        returns the current working directory
    """
    print("called pwd()")
    result = {'path': os.getcwd()}
    return result

def fun_datetime():
    """
        returns the current date and time
    """
    return {'date': date.today(), 'time': time.strftime("%H:%M:%S", time.localtime())}

# --- configuration

def load_config():
    """
        Loads the configuration for the LLM endpoint and chat format
    """
    with open(CONFIG_PATH) as f:
        return json.loads(f.read())

# --- parse function


def trim_response(response):
    """
        Trim the LLM response to remove everything after the function call
    """
    end_of_params = response.find(')')
    return response[0:end_of_params + 1]

def extract_name(response):
    """
        extract function name from LLM response
    """
    
    start_of_params = response.find('(')

    if start_of_params == -1:
        return ""
    else:
        return response[0:start_of_params]

def extract_param(response, index):
    """
        extract function param from LLM reponse
    """
    start_of_params = response.find('(')
    end_of_params = response.find(')')

    if start_of_params != -1 and end_of_params != -1 and (end_of_params - start_of_params) > 1:
        params = response[start_of_params + 1:end_of_params].split(',')
        try:
            return eval(params[index])
        except IndexError:
            return ""

# --- handle function

def call_function(response, function_list):
    """
        given an LLM response, try to call a function if name is found in list
    """
    result = ""

    print("identifying function")
    function_name = extract_name(response)
    
    if str.isidentifier(function_name):
        function_param1 = extract_param(response, 0)
        function_param2 = extract_param(response, 1)
        print(f"function info: {function_name}({function_param1}, {function_param2})")
        # hardcoded for now
        if function_name == function_list[0]['name']:
            result = fun_add(function_param1, function_param2)
        elif function_name == function_list[1]['name']:
            result = fun_weather(function_param1)
        elif function_name == function_list[2]['name']:
            result = fun_pwd()
        elif function_name == function_list[3]['name']:
            result = fun_datetime()

    if len(result) > 0:
        return "\n\n" + str(result) + "\n\n"
    else:
        return result
                

# --- LLM interaction

def generate(chat_history, prompt, function_list, BASE_URL="http://localhost", START_SEQ="", END_SEQ=""):
    """
        Generates an LLM response from the user prompt, optionally calling a function
    """
    chat_message = chat_history['choices'][0]['message']['content']
    
    #print("sending prompt")
    response = litellm.completion(
        model = "openai/llama3.1",
        api_key = "1234",
        api_base = BASE_URL + "/v1",
        messages = [
            {
                "role": "user",
                "content":  chat_message + START_SEQ + prompt + END_SEQ,
            }
        ],
        max_tokens = 300
    )

    response = response['choices'][0]['message']['content']
    function = trim_response(response) # keep only the function call
    function_result = call_function(function, function_list)
    history_prompt = START_SEQ + prompt + END_SEQ # for chat history

    if function_result!="":
        #print("sending 2nd prompt")
        response2 = litellm.completion(
            model = "openai/llama3.1",
            api_key = "1234",
            api_base = BASE_URL + "/v1",
            messages = [
                {
                    "role": "user",
                    "content":  chat_message + history_prompt + response + function_result,
                }
            ],
            max_tokens = 300
        )

        response2 = response2['choices'][0]['message']['content']
    else: # if no function call happened, no need to send back result
        print(response)
        response2 = ""
        
    chat_history['choices'][0]['message']['content'] += (history_prompt + response + function_result + response2)
    return response2
    

def main():
    """
        Runs the main program. The user can chat to the assistant in a loop until done
    """

    functions = [{'name': 'add', 'param1': 'a', 'param2': 'b', 'impl': fun_add},
                 {'name': 'weather', 'param1': 'location', 'impl': fun_weather},
                 {'name': 'pwd', 'impl': fun_pwd},
                 {'name': 'datetime', 'impl': fun_datetime}]

    config = load_config()
    BASE_URL = config['base_url']
    SYS_PROMPT = config['system_prompt']
    START_SEQ = config['start_sequence']
    END_SEQ = config['end_sequence']

    chat_history = {"choices": [{"message": {"content": SYS_PROMPT}}]}
    prompt = ""
    while prompt!="/X" and prompt!="/x":
        prompt = input(">")

        if prompt=="/X" or prompt=="/x":
            pass

        elif prompt=="/P" or prompt=="/p":
            print(chat_history['choices'][0]['message']['content'] + "\n")
        
        elif prompt=="/S" or prompt=="/s":
            print("NOTICE: If the file already exists, it will be overwritten")
            path = input("Please enter the name for your chat >")
            try:
                if not os.path.exists("chats"): # check for chats folder
                    os.makedirs("chats")
                if path[len(path)-4:len(path)]!=".txt": # add .txt if not there
                    path += ".txt"
                with open("chats/" + path, 'w') as f:
                    f.write(chat_history['choices'][0]['message']['content'])
                    print("NOTICE: Saved chat to chats/" + path + "\n")
            except Exception as e:
                print(e)
                print("ERROR: Unable to save chat\n")

        elif prompt=="/L" or prompt=="/l":
            path = input("Please enter the name for the chat to load >")
            try:
                if path[len(path)-4:len(path)]!=".txt": # add .txt if not there
                    path += ".txt"
                with open("chats/" + path, 'r') as f:
                    chat_history['choices'][0]['message']['content'] = f.read()
                    print("NOTICE: Successfully loaded chat from chats/" + path + "\n")
            except Exception as e:
                print("ERROR: Unable to load chat\n")

        elif prompt=="/N" or prompt=="/n":
            chat_history = {"choices": [{"message": {"content": SYS_PROMPT}}]}
            print("NOTICE: New chat session started\n")

        elif prompt=="/H" or prompt=="/h":
            print("Commands:")
            print("/P - Print the whole chat session")
            print("/S - Saves the chat session to a txt file")
            print("/L - Loads a chat session from a txt file")
            print("/N - Starts a new chat session")
            print("/H - Displays this list")
            print("/X - Exit the program\n")
            print("All commands can be entered in uppercase or lowercase.\n")

        else:
            response = generate(chat_history, prompt, functions, BASE_URL, START_SEQ, END_SEQ)
            print(response)

    print("NOTICE: Exiting...")

main()
