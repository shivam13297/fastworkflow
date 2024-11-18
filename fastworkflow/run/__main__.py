import argparse
import json
import os
import random
from typing import Optional
from dotenv import dotenv_values

from colorama import Fore, Style, init

import fastworkflow
from fastworkflow.command_router import CommandRouter
from fastworkflow.command_executor import CommandExecutor

# Initialize colorama
init(autoreset=True)

def print_command_output(command_output):
    for command_response in command_output.command_responses:
        session_id = fastworkflow.WorkflowSession.get_active_session_id()
        if command_response.response:   
            print(
                f"{Fore.GREEN}{Style.BRIGHT}{session_id} AI>{Style.RESET_ALL}{Fore.GREEN} {command_response.response}{Style.RESET_ALL}"
        )

        for artifact_name, artifact_value in command_response.artifacts.items():
            print(
                f"{Fore.CYAN}{Style.BRIGHT}{session_id} AI>{Style.RESET_ALL}{Fore.CYAN} Artifact: {artifact_name}={artifact_value}{Style.RESET_ALL}"
            )
        for action in command_response.next_actions:
            print(
                f"{Fore.BLUE}{Style.BRIGHT}{session_id} AI>{Style.RESET_ALL}{Fore.BLUE} Next Action: {action}{Style.RESET_ALL}"
            )
        for recommendation in command_response.recommendations:
            print(
                f"{Fore.MAGENTA}{Style.BRIGHT}{session_id} AI>{Style.RESET_ALL}{Fore.MAGENTA} Recommendation: {recommendation}{Style.RESET_ALL}"
            )


parser = argparse.ArgumentParser(description="AI Assistant for workflow processing")
parser.add_argument("workflow_path", help="Path to the workflow folder")
parser.add_argument("env_file_path", help="Path to the environment file")
parser.add_argument(
    "--startup_command", help="Optional startup command", default=""
)
parser.add_argument(
    "--startup_action", help="Optional startup action", default=""
)
parser.add_argument(
    "--keep_alive", help="Optional keep_alive", default=True
)

args = parser.parse_args()

if not os.path.isdir(args.workflow_path):
    print(
        f"{Fore.RED}Error: The specified workflow path '{args.workflow_path}' is not a valid directory.{Style.RESET_ALL}"
    )
    exit(1)

print(
    f"{Fore.GREEN}{Style.BRIGHT}AI>{Style.RESET_ALL}{Fore.GREEN} AI Assistant is running with workflow: {args.workflow_path}{Style.RESET_ALL}"
)
print(
    f"{Fore.GREEN}{Style.BRIGHT}AI>{Style.RESET_ALL}{Fore.GREEN} Type 'exit' to quit.{Style.RESET_ALL}"
)

if args.startup_command and args.startup_action:
    raise ValueError("Cannot provide both startup_command and startup_action")

fastworkflow.init(env_vars={**dotenv_values(args.env_file_path)})

startup_action: Optional[fastworkflow.Action] = None
if args.startup_action:
    with open(args.startup_action, 'r') as file:
        startup_action_dict = json.load(file)
    startup_action = fastworkflow.Action(**startup_action_dict)

workflow_session = fastworkflow.WorkflowSession(
    CommandRouter(),
    CommandExecutor(),
    random.randint(1, 100000000),
    args.workflow_path, 
    startup_command=args.startup_command, 
    startup_action=startup_action, 
    keep_alive=args.keep_alive
)

workflow_session.start()
command_output: fastworkflow.CommandOutput = workflow_session.command_output_queue.get()#(timeout=1)
if command_output:
    print_command_output(command_output)

while not workflow_session.workflow_is_complete or args.keep_alive:
    user_command = input(
        f"{Fore.YELLOW}{Style.BRIGHT}User>{Style.RESET_ALL}{Fore.YELLOW} "
    )
    if user_command == "exit":
        break

    workflow_session.user_message_queue.put(user_command)
    
    command_output = workflow_session.command_output_queue.get()
    if command_output:
        print_command_output(command_output)
