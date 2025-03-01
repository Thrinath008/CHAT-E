from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os 
import time
import mtranslate as mt

env_vars = dotenv_values(".env")
Inputlanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set

chat_log_path = "Data/ChatLog.json"

# Ensure the Data directory exists
os.makedirs("Data", exist_ok=True)

# Ensure the chat log file exists
if not os.path.exists(chat_log_path):
    with open(chat_log_path, "w") as f:
        f.write("")

# Define HTML Code
HtmlCode = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "{Inputlanguage}";  // ✅ Fixed insertion
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                console.log("Recognized:", transcript);
                output.textContent += transcript;
            }};

            recognition.onend = function() {{
                recognition.start();
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            recognition.stop();
            output.innerHTML = "";
        }}
    </script>
</body>
</html>
"""


# Save the HTML file
html_path = "Data/Voice.html"
with open(html_path, "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()
Link = f"file://{current_dir}/{html_path}"

# Configure Selenium WebDriver
chrome_options = Options()
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
chrome_options.add_argument(f'--user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")

# **REMOVE HEADLESS MODE** (Needed for microphone access)
# chrome_options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

TempDirpath = os.path.join(current_dir, "Frontend", "Files")

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirpath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "what", "what's", "why", "how", "how's", "when", "where", "where's",
        "who", "who's", "which", "whom", "whose", "can you", "could you"
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

def SpeechRecognition():
    global driver  # Reuse the same driver instance
    try:
        driver.get(Link)  # Open the webpage once
        driver.find_element(By.ID, "start").click()
        print("[INFO] Speech recognition started...")

        last_text = ""

        while True:
            try:
                Text = driver.find_element(By.ID, "output").text
                if Text and Text != last_text:
                    print(f"[DEBUG] Raw text detected: {Text}")
                    driver.find_element(By.ID, "end").click()
                    last_text = Text
                    
                    if Inputlanguage.lower() == "en" or "in" in Inputlanguage.lower():
                        return QueryModifier(Text)
                    else:
                        SetAssistantStatus("Translating...")
                        return QueryModifier(UniversalTranslator(Text))
                
                time.sleep(0.5)  # Reduce CPU usage by adding a small delay
            except Exception:
                pass
    except Exception as e:
        print("Error:", str(e))
        return None

if __name__ == "__main__":
    try:
        print("Listening... (Press CTRL+C to stop)")
        while True:
            Text = SpeechRecognition()
            if Text:
                print("You said:", Text)
    except KeyboardInterrupt:
        print("\nStopping...")
        driver.quit()  # Close the browser when script stops
