from flask import Flask, request
from twilio.rest import Client
from threading import Thread
import queue
import time
import openai
import json
from browser_actions import BrowserActions
from overlay import Overlay
import sys
import base64
import os
from dotenv import load_dotenv
from pyngrok import ngrok
import subprocess

app = Flask(__name__)
messages_queue = queue.Queue()

def long_running_process():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_image

    with open("vision_prompt.txt", "r") as file:
        vision_prompt = file.read()

    with open("decision_prompt.txt", "r") as file:
        decision_prompt = file.read()
        
    # Send the user input and screenshot to OpenAI. Because GPT-4 Vision cannot call functions, we must send its input back again
    def image_analysis(history, user_input, screenshot_path):
        print("Starting image analysis...")
        encoded_image = encode_image(screenshot_path)
        prompt_history = ""
        for item in history[-15:]:
            prompt_history += item + "\n"
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Original query:" + user_input},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64," + encoded_image,
                            },
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Interaction history:" + prompt_history},
                    ],
                },
            ],
            max_tokens=500,
        )
        history.append("Assistant: " + response.choices[0].message.content)
        return response.choices[0]

    # Once image has been analysed, we'll take its output and pass it to GPT with function calls.
    def choose_function(history, user_input, image_analysis_output):
        print("Starting function call..")
        # turn history list into a string
        prompt_history = ""
        for item in history[-15:]:
            prompt_history += item + "\n"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": decision_prompt},
                    ],
                },
                            {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": prompt_history},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "User query:" + user_input},
                    ],
                },
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": "Image analysis:" + image_analysis_output.message.content},
                    ],
                },
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "open_snapchat_message",
                        "description": "Opens up the chat window for a specific contact so that messages can be read and sent. Only call this if we are specifically instructed to read a specific snap, if we haven't already read the messages inside and if we are given the position of the Snapchat to open as input.",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "position": {
                            "type": "integer",
                            "description": "The position of the Snapchat to open, e.g., 0 for the first and latest Snapchat, then 1 for the second, and so on."
                            }
                        },
                        "required": ["position"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "send_snapchat_message",
                        "description": "Send a message to an already opened Snapchat with the user's message.",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                            "type": "string",
                            "description": "The message to send to the Snapchat contact."
                            }
                        },
                        "required": ["message"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "reply_to_user",
                        "description": "Answers the user's question with a text response. We call this function when we have enough information to satisfy the user's request.",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "response": {
                            "type": "string",
                            "description": "The text response to send to the user, informing them of the completion of their request or the information they wanted. E.g. 'You have 2 new Snapchats from X and Y' or 'I have sent the message to X', or 'X said Y'."
                            }
                        },
                        "required": ["response"]
                        }
                    }
                }
            ],
            tool_choice="auto",
            max_tokens=500,
        )
        try:
            reply_content = response.choices[0].message.tool_calls[0].function
            print("Received function call: " + reply_content.name)
        except:
            reply_content = response.choices[0].message.content
            print("Received text response: " + reply_content)
        return reply_content

    def send_sms(message):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)

        message = client.messages.create(
        from_=os.getenv("FROM_NUMBER"),
        to=os.getenv("TO_NUMBER"),
        body=message
        )

    def main():
        browser_actions = BrowserActions()
        try:
            print("Application start up!")
            overlay = Overlay()
            answered = True
            history = []
            already_sent = False
            already_opened = False

            def decide_next_action(function_call):
                nonlocal answered
                nonlocal history
                nonlocal already_sent
                nonlocal already_opened
                # check if name exists in function_call
                if isinstance(function_call, str):
                    print("GPT: " + function_call)
                    send_sms(function_call)
                    answered = True
                    history.append(function_call)
                    return
                if function_call.name == "open_snapchat_message" and not already_opened:
                    already_opened = True
                    history.append("Assistant called: " + function_call.name)
                    arguments_dict = json.loads(function_call["arguments"])
                    position = arguments_dict["position"]
                    browser_actions.open_chat(position)
                    answered = False

                elif function_call.name == "send_snapchat_message" and not already_sent:
                    already_sent = True
                    history.append("Assistant called: " + function_call.name)
                    arguments_dict = json.loads(function_call["arguments"])
                    message = arguments_dict["message"]
                    browser_actions.reply_to_chat(message)
                    answered = False

                elif function_call.name == "reply_to_user" or function_call.name == "send_snapchat_message" or function_call.name == "open_snapchat_message":
                    arguments_dict = json.loads(function_call["arguments"])
                    try:
                        response = arguments_dict["response"]
                    except:
                        response = "Send successful!"
                    print(response)
                    send_sms(response)

                    history.append("Assistant answered: " + response)
                    answered = True

            while True:
                checking_messages = True
                if answered:
                    print("Checking for messages...")
                    check_count = 0
                    while checking_messages:
                        if not messages_queue.empty():
                            question = messages_queue.get()
                            checking_messages = False
                        else:
                            # every minute (12 sleeps) print "checking for messages"
                            check_count += 1
                            if check_count == 12:
                                print("Still checking...")
                                browser_actions.return_to_home()
                                check_count = 0
                        time.sleep(5)  # Prevent this loop from consuming too much CPU
                    answered = False
                    already_sent = False
                    already_opened = False
                    if question == "exit":
                        print("Exiting...")
                        sys.exit(0)
                    history.append("User: " + question)  
                else:
                    browser_actions.take_screenshot("screen.png")
                    overlay.overlay_numbers("screen.png")
                    n = 0
                    while n < 3:
                        try:
                            image_analysis_output = image_analysis(history, question, "screen.png")
                            break
                        except Exception as e:
                            n += 1
                            print("Image analysis failed. Retrying..." + str(e))
                    if n == 3:
                        print("Image analysis failed 3 times. Exiting...")
                        sys.exit(1)
                    n = 0
                    while n < 3:
                        try:
                            decide_next_action(choose_function(history, question, image_analysis_output))
                            break
                        except Exception as e:
                            n += 1
                            print("Function call failed. Retrying..." + str(e))
                    if n == 3:
                        print("Function call failed 3 times. Exit loop and continue checking for messages...")
                        continue
                        
                        
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
        finally:
            print("Application stopped.")
    
    main()
    
def kill_chrome():
    subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    # check if sender is equal to to_number
    if request.values.get('From') != os.getenv("TO_NUMBER"):
        print("Intruder detected!" + request.values.get('From'))
        return "Message received from unauthorized number", 200
    else:
        print("Message received from authorized number")
    body = request.values.get('Body', None)
    print(f"Received message: {body}")
    messages_queue.put(body)  # Add the incoming message to the queue
    return "Message received", 200

if __name__ == "__main__":
    # Start the long-running process in a separate thread
    thread = Thread(target=long_running_process)
    thread.daemon = True  # Daemonize thread
    thread.start()

    # Start ngrok at free subdomain
    load_dotenv()
    ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))
    ngrok_tunnel = ngrok.connect(hostname=os.getenv("NGROK_DOMAIN"), proto="http", addr="5000")
    print(f'ngrok tunnel "{ngrok_tunnel.public_url}" -> "http://localhost:5000"')

    # Start the Flask application
    try:
        app.run(debug=True, use_reloader=False)  # use_reloader=False to avoid creating duplicate threads when the server reloads
    finally:
        ngrok.kill()
        kill_chrome()
        print("Application stopped.")

