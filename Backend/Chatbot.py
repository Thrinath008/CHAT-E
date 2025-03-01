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
    with open(chat_log_path, "w") as f:  # ✅ Fixed mode
        dump([], f)

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chat_log_path, "w") as f:  # ✅ Fixed mode
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"""Day: {current_date_time.strftime("%A")}
Date: {current_date_time.strftime("%d")}
Month: {current_date_time.strftime("%B")}
Year: {current_date_time.strftime("%Y")}
Time: {current_date_time.strftime("%H")} hours : {current_date_time.strftime("%M")} minutes : {current_date_time.strftime("%S")} seconds.
"""

def AnswerModifier(Answer):
    return "\n".join(line for line in Answer.split("\n") if line.strip())

def ChatBot(Query):
    try:
        with open(chat_log_path, "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "user", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": Answer})  # ✅ Fixed role

        with open(chat_log_path, "w") as f:  # ✅ Fixed mode
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")

        with open(chat_log_path, "w") as f:  # ✅ Fixed mode
            dump([], f, indent=4)

        return "An error occurred, please try again."

if __name__ == "__main__":
    while True:
        user_input = input("me --> ")
        print(ChatBot(user_input))
