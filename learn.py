#!/usr/bin/env python3

import argparse
import os
import subprocess
import readline
import shutil
import difflib
import json
from colorama import Fore, Style, init
from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.key_binding import KeyBindings
import openai  # Requires the openai package (pip install openai)

# Initialize colorama
init(autoreset=True)

# Load custom aliases from a configuration file
CONFIG_FILE = "command_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump({}, config_file)
    with open(CONFIG_FILE, 'r') as config_file:
        return json.load(config_file)

def save_config(config):
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config, config_file, indent=4)

# Function to get all available system commands
def get_all_system_commands():
    system_path = os.getenv('PATH')
    commands = set()
    for path in system_path.split(os.pathsep):
        if os.path.isdir(path):
            for cmd in os.listdir(path):
                commands.add(cmd)
    return sorted(commands)

all_commands = get_all_system_commands()

# Function to auto-correct arguments
def auto_correct(argument, choices):
    matches = difflib.get_close_matches(argument, choices, n=1, cutoff=0.6)
    return matches[0] if matches else argument

# Function to check if an app is installed
def check_app_installed(app_name):
    return shutil.which(app_name) is not None

# Function to explain common Linux commands
def explain_command(command):
    explanations = {
        "ls": "The 'ls' command lists directory contents.",
        "cd": "The 'cd' command changes the current directory.",
        "rm": "The 'rm' command removes files or directories.",
        # Add more common explanations if needed
    }
    return explanations.get(command, "No explanation available for this command.")

# Function to get AI-generated suggestions
def get_ai_suggestion(prompt):
    # Placeholder for OpenAI API key (set your API key here)
    openai.api_key = "YOUR_OPENAI_API_KEY"
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Set up autocomplete using readline
def completer(text, state):
    options = [cmd for cmd in all_commands if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

# Main interactive prompt
def interactive_prompt():
    session = PromptSession()
    bindings = KeyBindings()

    @bindings.add('c-g')
    def _(event):
        user_query = input(Fore.YELLOW + "AI Suggestion Mode: Ask your question...\n> ")
        response = get_ai_suggestion(user_query)
        print(Fore.CYAN + "AI Suggestion: " + response)

    @bindings.add('c-c')
    def _(event):
        print_formatted_text(Fore.BLUE + "Command Help: Available commands are ls, cd, rm, etc.")

    @bindings.add('c-i')
    def _(event):
        print_formatted_text(Fore.GREEN + "Installed Applications Info:")
        for app in all_commands:
            if check_app_installed(app):
                print(Fore.GREEN + f"{app} is installed.")
            else:
                print(Fore.RED + f"{app} is NOT installed.")

    while True:
        try:
            user_input = session.prompt("> ", key_bindings=bindings)
            if user_input == "exit":
                break
            elif user_input.startswith("learn "):
                command = user_input.split(" ")[1]
                print(Fore.CYAN + explain_command(command))
            elif user_input in all_commands:
                if check_app_installed(user_input):
                    print(Fore.GREEN + f"{user_input} is installed.")
                else:
                    print(Fore.RED + f"{user_input} is NOT installed.")
            elif user_input.startswith("!"):
                # Execute a command directly
                command_to_run = user_input[1:]
                try:
                    output = subprocess.check_output(command_to_run, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                    print(Fore.GREEN + output)
                except subprocess.CalledProcessError as e:
                    print(Fore.RED + e.output)
            else:
                print(Fore.RED + "Unknown command. Press Ctrl+C for help.")
        except KeyboardInterrupt:
            break

# Main function
def main():
    # Load user configuration
    config = load_config()

    # Argument parser setup
    parser = argparse.ArgumentParser(description="Enhanced terminal learning script with customizable commands, AI suggestions, autocomplete, and hotkeys.")
    parser.add_argument("app", nargs='?', type=str, help="The name of the app you want to check (e.g., git, node).")
    parser.add_argument("-a", "--auto-correct", action="store_true", help="Enable auto-correction for app names.")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enter interactive learning mode.")
    parser.add_argument("-c", "--customize", nargs=2, metavar=('ALIAS', 'COMMAND'), help="Add a custom command alias.")

    # Parse arguments
    args = parser.parse_args()

    if args.interactive:
        interactive_prompt()
        return

    if args.customize:
        alias, command = args.customize
        config[alias] = command
        save_config(config)
        print(Fore.YELLOW + f"Alias '{alias}' for command '{command}' added successfully.")
        return

    # Handle app argument
    if args.app:
        app_name = args.app
        if args.auto_correct:
            corrected_app_name = auto_correct(app_name, all_commands)
            if corrected_app_name != app_name:
                print(f"{Fore.YELLOW}Did you mean '{corrected_app_name}'? Auto-correcting...{Style.RESET_ALL}")
                app_name = corrected_app_name

        # Check if the app is installed
        is_installed = check_app_installed(app_name)
        if is_installed:
            print(f"{Fore.GREEN}{app_name} is installed on your system.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{app_name} is NOT installed on your system.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
