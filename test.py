import requests
import json
from datetime import datetime
from uuid import uuid4

try:
    from config import ASSISTANT_NAME
except ImportError:
    ASSISTANT_NAME = "Jarvis"

BASE_URL = "http://localhost:8000"
SESSION_ID = None
CURRENT_MODE = None

def print_header():
    print("\n" + "="*60)
    print("🤖 J.A.R.V.I.S - General & Realtime Chat")
    print("="*60)
    print("\nModes: 1=General, 2=Realtime")
    print("Commands: /history, /clear, /quit")
    print("="*60 + "\n")

def get_user_input():
    try:
        return input("\nYou: ").strip()
    except (KeyboardInterrupt, EOFError):
        return None

def send_message(message, mode):
    global SESSION_ID
    if not SESSION_ID:
        SESSION_ID = str(uuid4())
    endpoint = "/chat/realtime" if mode == "realtime" else "/chat"
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"message": message, "session_id": SESSION_ID},
            timeout=60 if mode == "realtime" else 30
        )
        if response.status_code == 200:
            data = response.json()
            SESSION_ID = data.get("session_id", SESSION_ID)
            return data.get("response", "No response")
        else:
            try:
                err = response.json()
                if isinstance(err.get("detail"), str):
                    return f"❌ {err['detail']}"
            except:
                pass
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_chat_history():
    if not SESSION_ID:
        return "No active session"
    try:
        response = requests.get(f"{BASE_URL}/chat/history/{SESSION_ID}", timeout=10)
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            output = f"\n📜 History ({len(messages)} messages):\n" + "-"*40 + "\n"
            for msg in messages:
                role = "You" if msg.get("role") == "user" else ASSISTANT_NAME
                output += f"{role}: {msg.get('content', '')}\n"
            return output + "-"*40
        return "Could not retrieve history"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print_header()
    global SESSION_ID, CURRENT_MODE
    while True:
        user_input = get_user_input()
        if user_input is None or user_input in ["/quit", "/exit"]:
            print("\n👋 Goodbye!")
            break
        if user_input == "1":
            CURRENT_MODE = "general"
            print("✅ Switched to GENERAL chat\n")
            continue
        elif user_input == "2":
            CURRENT_MODE = "realtime"
            print("✅ Switched to REALTIME chat\n")
            continue
        elif user_input == "/history":
            print(get_chat_history())
            continue
        elif user_input == "/clear":
            SESSION_ID, CURRENT_MODE = None, None
            print("\n🔄 Session cleared!")
            continue
        if not CURRENT_MODE:
            print("❌ Select mode first (1 or 2)")
            continue
        print(f"🤖 {ASSISTANT_NAME}: ", end="", flush=True)
        print(send_message(user_input, CURRENT_MODE))

if __name__ == "__main__":
    main()
