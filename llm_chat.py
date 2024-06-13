import ollama
from openai import OpenAI

def get_response_llama3(message):
  response = ollama.generate(model='llama3', prompt=message)
  return (response['response'])

def get_response_openai(message):
  client = OpenAI()

  completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "user", "content": message}
    ]
  )
  return completion.choices[0].message.content

def get_response(message, llm):
  if llm == 'llama3':
    return get_response_llama3(message)
  else:
    return get_response_openai(message)