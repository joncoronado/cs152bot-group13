# This is example code using GPT-4 to do a basic classification of a text string
# It is super basic, your milestone 3 should do better than this
# This is a live API key that should be used only for the CS 152 project
# Please do not check the API key into a public GitHub repo or share it with anybody outside of your group


import os
import openai
from openai import OpenAI
import json


tokens_path = os.path.join(os.path.dirname(__file__), 'tokens.json')
with open(tokens_path) as f:
    tokens = json.load(f)
client = OpenAI(api_key=tokens["openai"])

def classify_message(message):
    response = client.chat.completions.create(model="gpt-4",
    messages = [{"role": "system", "content": "You are a content moderation system. Classify each input as either harassment or not harassment. If harassment, choose one of the following [Threats, Hate Speech, Bullying, Sexual Harassment, Other] and explain why. If not harassment, simply respond with 'Not harassment'."},
            {"role": "user", "content": "I am going to release inappropriate photos of Ronny if he doesn't give me a million dollars"},
            {"role": "assistant", "content": "Harassment: Threat. The user is threatening to blackmail Ronny."},
            {"role": "user", "content": "I love bullying"},
            {"role": "assistant", "content": "Not harassment"},
            {"role": "user", "content": "Fuck you Ronny im going to beat you up"},
            {"role": "assistant", "content": "Harassment: Threat. The user is threatening to hurt Ronny."},
            {"role": "user", "content": "George's address is 728 Winding Maple Drive Stonebrook, IL 60458 United States. I'll see you there tomorrow. Bring torches"},
            {"role": "assistant", "content": "Harassment: Threat. The user doxxing Ronny and threatening to hurt him."},
            {"role": "user", "content": message}])
    output = response.choices[0].message.content
    return output