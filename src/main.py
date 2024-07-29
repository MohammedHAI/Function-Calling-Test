# Copyright 2024 Mohammed Al-Islam
#
# This is a rough example and is not suitable for deployment

import litellm
import os
import json
from datetime import date
import time

# --- chat format (llama 3.1)

SYS_PROMPT = '''<|start_header_id|>system<|end_header_id|>\n\nYou have access to the following functions:

add(a, b) - adds 2 numbers and returns the result
weather(location) - returns the weather of the specified location
pwd() - returns the current working directory
datetime() - returns the current date and time

To call a function, simply write its name and the parameters you wish to use. For example, to add 3 and 4, write:

add(3, 4)

'''

START_SEQ = "<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
END_SEQ = "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

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

# --- parse function

def extract_name(response):
    """
        extract function name from LLM response
    """
    
    end_of_name = response.find('(')

    if end_of_name == -1:
        return ""
    else:
        return response[0:end_of_name]

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

def call_function(response, functions):
    """
        given an LLM response, try to call a function if name is found in list
    """
    result = "{'result': 'Error: function not found'}"

    print("identifying function")
    function_name = extract_name(response)
    if str.isidentifier(function_name):
        function_param1 = extract_param(response, 0)
        function_param2 = extract_param(response, 1)
        print(f"function info: {function_name}({function_param1}, {function_param2})")
        # hardcoded for now
        if function_name == functions[0]['name']:
            result = fun_add(function_param1, function_param2)
        elif function_name == functions[1]['name']:
            result = fun_weather(function_param1)
        elif function_name == functions[2]['name']:
            result = fun_pwd()
        elif function_name == functions[3]['name']:
            result = fun_datetime()

    return "\n\n" + str(result) + "\n\n"
                

# --- main

def main():
    """
        Call LLM to provide function, extract and call function, then send response back
    """

    functions = [{'name': 'add', 'param1': 'a', 'param2': 'b'},
                 {'name': 'weather', 'param1': 'location'},
                 {'name': 'pwd'},
                 {'name': 'datetime'}]

    #prompt = "What's the weather in Moscow?"
    #prompt = "What's 3 + 4?"
    #prompt = "What directory am I in?"
    #prompt = "What's the date and time?"
    prompt = "What's 3 multiplied by 4? If you don't know, don't answer" # Bogus question with no appropriate function

    print("sending prompt")
    response = litellm.completion(
        model = "openai/llama3.1",
        api_key = "1234",
        api_base = "http://192.168.0.50:5001/v1",
        messages = [
            {
                "role": "user",
                "content":  SYS_PROMPT + START_SEQ + prompt + END_SEQ,
            }
        ],
        max_tokens = 300
    )

    response = response['choices'][0]['message']['content']
    print(response)
    
    function_result = call_function(response, functions)
    
    print("sending 2nd prompt")
    response2 = litellm.completion(
        model = "openai/llama3.1",
        api_key = "1234",
        api_base = "http://192.168.0.50:5001/v1",
        messages = [
            {
                "role": "user",
                "content":  SYS_PROMPT + START_SEQ + prompt + END_SEQ + response + function_result,
            }
        ],
        max_tokens = 300
    )

    response2 = response2['choices'][0]['message']['content']
    print(response2)

    print("\n\nFull Chat Log:")
    print(SYS_PROMPT + START_SEQ + prompt + END_SEQ + response + function_result + response2)

main()
