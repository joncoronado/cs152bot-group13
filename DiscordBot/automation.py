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

context = [
    {
        "role": "system", 
        "content": "You are a content moderation system. Classify each input as either harassment or not harassment. If harassment, specify the tags. Potential tags: [Harassment, Phishing, IT Problems, Inappropriate Content, Unknown Member, Threat, Hate Speech, Sexual Harassment, Bullying, Violent Threat, Nonviolent Threat, Personal Threat, Loved Ones Threat, Other Threat, Extortion, Blackmail, Doxxing, Racism, Sexism, Homophobia, Transphobia, Religious Discrimination, Ethnic/Cultural Discrimination, Blocked, Not Blocked, Other]."
    },
    {
        "role": "user",
        "content": "Alex's ass looks great!"
    },
    {
        "role": "assistant",
        "content": "{\"harassment\": true, \"tags\": [\"Harassment\", \"Sexual Harassment\"], \"reasoning\": \"The message is objectifying Alex in a sexual manner.\"}"
    }
]

def classify_message(message):
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=context + [
            {"role": "user", "content": message}
        ],
        response_format=HarassmentClassification,
    )
    output = response.choices[0].message.parsed
    return output