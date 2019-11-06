#from main import chat
from flask import Flask, request, jsonify
from main import model, bag_of_words, words, labels, data
import numpy as np
import random
import requests


app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'aOfxZ2ABTmp0zm+EP2oEWbXHPxHTnBGVhN3zDfBL+q8='  # <paste your verify token here>
PAGE_ACCESS_TOKEN = 'EAAHJH39NVRcBAAXIr5bGW52yyr2urcD7raNiVEL5MwKfxKQ0kDkdMbei61xVkMHgwUQ89xRdfZBqYQzEDqD39mlFhbZASXgDw6HBj2PWu1rdksxlQwN3dmRBnRRp4S5YTChUzEPpIObBv8nVlZCZASpzDLHYdANi4ZAmigMI9CQZDZD'  # paste your page access token here>"


# def get_bot_response(message):
#     """This is just a dummy function, returning a variation of what
#     the user said. Replace this function with one connected to chatbot."""
#     return "This is a dummy response to '{}'".format(message)

#chat()

#@app.route('/', methods=['GET', 'POST'])
def chat():
    # Logic for POST request
    if request.method == 'POST':
        user_input = request.get_json(force=True)

        results = model.predict([bag_of_words(user_input["user_message"], words)])[0]
        results_index = np.argmax(results)
        tag = labels[results_index]
        print(user_input["user_message"])

        if results[results_index] > 0.7:
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']

            print(random.choice(responses))
        else:
            return "I didn't get that please try again"
            # print("I didn't get that. PLease type another question")

    return jsonify("See ya")






#
#     print("Start talking with the bot (Type quit to stop!) ")
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == "quit":
#             break
#
#         results = model.predict([bag_of_words(user_input, words)])[0]
#         results_index = np.argmax(results)
#         tag = labels[results_index]
#
#         if results[results_index] > 0.7:
#             for tg in data["intents"]:
#                 if tg['tag'] == tag:
#                     responses = tg['responses']
#
#             print(random.choice(responses))
#         else:
#             print("I didn't get that. PLease type another question")
#
#
# #chat()


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    response = chat()
    send_message(sender, response)


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


@app.route("/webhook")
def listen():
    """This is the main function flask uses to
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id, text)

        return "ok"


def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()