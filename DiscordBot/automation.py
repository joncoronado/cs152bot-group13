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
        "content": "I am going to release inappropriate photos of Ronny if he doesn't give me a million dollars"
    },
    {
        "role": "assistant", 
        "content": "{\"harassment\": true, \"tags\": [\"Harassment\", \"Threat\", \"Extortion\", \"Blackmail\"], \"reasoning\": \"The message threatens to blackmail Ronny.\"}"
    },
    {
        "role": "user", 
        "content": "I love bullying"
    },
    {
        "role": "assistant", 
        "content": "{\"harassment\": false, \"tags\": null, \"reasoning\": \"The user is expressing a personal preference.\"}"
    },
    {
        "role": "user", 
        "content": "Fuck you Ronny im going to beat you up"
    },
    {
        "role": "assistant", 
        "content": "{\"harassment\": true, \"tags\": [\"Harassment\", \"Threat\", \"Violent Threat\"], \"reasoning\": \"The message threatens physical harm.\"}"
    },
    {
        "role": "user",
        "content": "Everyone tells me that Jonathan is fat, but I don't think so!"
    },
    {
        "role": "assistant",
        "content": "{\"harassment\": true, \"tags\": [\"Harassment\", \"Bullying\"], \"reasoning\": \"The message implies that there is a negative public opinion of Jonathan, which is bullying.\"}"
    },
    {
        "role": "user",
        "content": "George looks like the type of person to put a fork in the microwave"
    },
    {
        "role": "assistant",
        "content": "{\"harassment\": true, \"tags\": [\"Harassment\", \"Bullying\"], \"reasoning\": \"The message implies George is not smart and would harm himself unintentionally.\"}"
    },
    {
        "role": "user",
        "content": "Jonathan's smell makes me want to unalive myself"
    },
    {
        "role": "assistant",
        "content": "{\"harassment\": true, \"tags\": [\"Harassment\", \"Bullying\"], \"reasoning\": \"The message implies that Jonathan's smell is bad enough that they want to self harm.\"}"
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