from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Use a valid file path
chat_log_path = "Data/ChatLog.json"

# Ensure the Data directory exists
os.makedirs("Data", exist_ok=True)

# Ensure the chat log file exists
if not os.path.exists(chat_log_path):
    with open(chat_log_path, "w") as f:
        dump([], f)

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} with real-time up-to-date internet search capabilities.
*** Provide answers in a professional manner, with proper punctuation, grammar, and sentence structure. ***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chat_log_path, "w") as f:
        dump([], f)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    answer = f"Search results for '{query}':\n[start]\n"

    for i in results:
        answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    answer += "[end]"
    return answer

def AnswerModifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    current_date_time = datetime.datetime.now()
    return f"""Use this real-time information if needed:
Day: {current_date_time.strftime("%A")}
Date: {current_date_time.strftime("%d")}
Month: {current_date_time.strftime("%B")}
Year: {current_date_time.strftime("%Y")}
Time: {current_date_time.strftime("%H")}:{current_date_time.strftime("%M")}:{current_date_time.strftime("%S")}
"""

def RealtimeSearchEngine(prompt):
    global messages  # Do not modify SystemChatBot globally

    with open(chat_log_path, "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})

    temp_chatbot = SystemChatBot.copy()  # Copy instead of modifying global list
    temp_chatbot.append({"role": "user", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=temp_chatbot + [{"role": "user", "content": Information()}] + messages,
        max_tokens=2024,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )

    answer = ""

    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = answer.replace("</s>", "")
    messages.append({"role": "assistant", "content": answer})

    with open(chat_log_path, "w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(answer)

if __name__ == "__main__":
    while True:
        prompt = input("Online search: ")
        print(RealtimeSearchEngine(prompt))
