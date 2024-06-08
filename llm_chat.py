import ollama
from openai import OpenAI

def get_response(message):
  response = ollama.chat(model='llama3', messages=[
    {
      'role': 'user',
      'content': message,
    },
  ])
  return (response['message']['content'])

def get_response_openai(message):
  client = OpenAI()

  completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "user", "content": message}
    ]
  )
  return completion.choices[0].message.content
