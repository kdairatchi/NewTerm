#!/bin/bash

echo "Welcome to the Learning Script Setup!"
echo "This script will guide you through setting up all dependencies for using the learning Python script."

# Step 1: Check for Python installation
echo "Checking if Python3 is installed..."
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Installing Python3..."
    # For Debian/Ubuntu-based systems
    sudo apt-get update
    sudo apt-get install python3 -y
    sudo apt-get install python3-pip -y
else
    echo "Python3 is already installed."
fi

# Step 2: Install required Python libraries
echo "Installing required Python libraries..."
pip3 install argparse colorama prompt_toolkit openai readline

# Step 3: Set up OpenAI API Token
echo "To use AI features, you need an OpenAI API Token."
read -p "Please enter your OpenAI API Token: " OPENAI_API_KEY

# Create a config file to save the API key
CONFIG_FILE="config.json"
echo "{
  \"openai_api_key\": \"$OPENAI_API_KEY\"
}" > $CONFIG_FILE

echo "OpenAI API Token saved successfully."

# Step 4: Set up the Python script (if not already present)
PYTHON_SCRIPT="learning_script.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Creating the Python learning script..."
    cat <<EOL > $PYTHON_SCRIPT
#!/usr/bin/env python3

import argparse
import os
import subprocess
import readline
import json
from colorama import Fore, Style, init
from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.key_binding import KeyBindings
import openai

# Initialize colorama
init(autoreset=True)

# Load configuration (e.g., API keys)
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.load(config_file)
    return {}

# Function to get AI-generated suggestions
def get_ai_suggestion(prompt, api_key):
    openai.api_key = api_key
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Main interactive prompt
def interactive_prompt():
    session = PromptSession()
    bindings = KeyBindings()

    # Load configuration
    config = load_config()
    api_key = config.get("openai_api_key", "")

    @bindings.add('c-g')
    def _(event):
        if not api_key:
            print_formatted_text(Fore.RED + "API key is missing. Please set it in config.json")
            return
        user_query = input(Fore.YELLOW + "AI Suggestion Mode: Ask your question...\n> ")
        response = get_ai_suggestion(user_query, api_key)
        print(Fore.CYAN + "AI Suggestion: " + response)

    while True:
        try:
            user_input = session.prompt("> ", key_bindings=bindings)
            if user_input == "exit":
                break
            elif user_input.startswith("learn "):
                command = user_input.split(" ")[1]
                print(Fore.CYAN + f"Explanation for {command}: Not implemented.")
            elif user_input.startswith("!"):
                # Execute a command directly
                command_to_run = user_input[1:]
                try:
                    output = subprocess.check_output(command_to_run, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                    print(Fore.GREEN + output)
                except subprocess.CalledProcessError as e:
                    print(Fore.RED + e.output)
            else:
                print(Fore.RED + "Unknown command. Type 'exit' to quit.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced terminal learning script with AI suggestions.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enter interactive learning mode.")
    args = parser.parse_args()

    if args.interactive:
        interactive_prompt()
EOL
    echo "Python learning script created successfully."
else
    echo "Python learning script already exists."
fi

# Step 5: Make the Python script executable
chmod +x $PYTHON_SCRIPT

echo "Setup is complete! You can now run the learning script using:"
echo "./learn.py -i"
