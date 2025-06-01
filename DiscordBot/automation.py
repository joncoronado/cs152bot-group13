import os
from openai import OpenAI
from pydantic import BaseModel
from enums import Tags
import json

class HarassmentClassification(BaseModel):
    harassment: bool
    tags: list[Tags] | None = None  # Use the Tags enum for classification
    reasoning: str


tokens_path = os.path.join(os.path.dirname(__file__), 'tokens.json')
with open(tokens_path) as f:
    tokens = json.load(f)
client = OpenAI(api_key=tokens["openai"])


developer_message_path = os.path.join(os.path.dirname(__file__), 'developer_message.txt')
with open(developer_message_path) as dev_f:
    developer_message = dev_f.read()

def classify_message(message, context):
    if len(context) > 50:
        context = context[-50:]

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a content moderation system. You will follow developer-supplied instructions."},
            {"role": "developer", "content": developer_message},
            {"role": "system", "content": f'{context}'},
            {"role": "user", "content": message}
        ],
        response_format=HarassmentClassification,
    )
    output = response.choices[0].message.parsed
    return output