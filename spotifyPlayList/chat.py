import openai
import json

# Set your API key
def promptgpt (prompt):
    openai.api_key = '<your-api-key>'
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            # Edit the system
            {"role":'system','content':'You are very curt and only ever speak a few words. Use as few words as possible when replying. I will describe something and you give me a name for a playlist for it, keep it simple and just use the keywords because I am searching through playlists that are already made under that name'},
            {"role": "user", "content": prompt},
        ],
    )


    return completion.choices[0].message.content
