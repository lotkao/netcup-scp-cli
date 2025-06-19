import os
import sys
import urllib.parse
from zeep import Client

# Load credentials from environment variables or prompt user
LOGIN = os.getenv("NETCUP_LOGIN")
if not LOGIN:
    LOGIN = input("Enter NETCUP_LOGIN: ")

PASSWORD = os.getenv("NETCUP_PASSWORD")
if not PASSWORD:
    PASSWORD = input("Enter NETCUP_PASSWORD: ")

WSDL_URL = 'https://www.servercontrolpanel.de/WSEndUser?wsdl'
client = Client(WSDL_URL)

# Define actions and their corresponding methods/actions
actions = [
    ("List VServers", "getVServers", []),
    ("Start VServer", "startVServer", ["vserverName"]),
    ("Stop VServer", "stopVServer", ["vserverName"]),
    ("Get VServer State", "getVServerState", ["vserverName"]),
    ("Get VServer IPs", "getVServerIPs", ["vserverName"]),
    ("Change IP Routing", "changeIPRouting", ["routedIP", "routedMask", "destinationVserverName", "destinationInterfaceMAC"]),
    ("Get VServer Stat Token", "getVServerStatToken", ["vserverName"]),
]

def prompt_inputs(params):
    inputs = {}
    for p in params:
        if p == "vserverName" or p == "destinationVserverName":
            vservers = client.service.getVServers(loginName=LOGIN, password=PASSWORD)
            if not vservers:
                print("No VServers found.")
                return {}
            print("Available VServers:")
            for i, v in enumerate(vservers, start=1):
                print(f"{i}. {v}")
            try:
                choice = int(input(f"Select {p} by number: ")) - 1
                if choice < 0 or choice >= len(vservers):
                    raise ValueError
                inputs[p] = vservers[choice]
            except ValueError:
                print("Invalid selection.")
                return {}
        else:
            inputs[p] = input(f"Enter {p}: ")
    return inputs

def print_stat_token(token):
    encoded_token = urllib.parse.quote(token)
    print("\nStat Token:")
    print(f"Raw: {token}")
    print(f"URL-safe: {encoded_token}")

def main():
    print("Netcup SCP WebService CLI")
    while True:
        print("\nAvailable Actions:")
        for i, (name, _, _) in enumerate(actions, start=1):
            print(f"{i}. {name}")
        print("0. Exit")

        try:
            choice = int(input("Select an option (number): ")) - 1
            if choice == -1:
                print("Exiting.")
                break
            if choice < 0 or choice >= len(actions):
                raise ValueError
        except ValueError:
            print("Invalid selection.")
            continue

        action_name, method_name, param_names = actions[choice]
        extra_params = prompt_inputs(param_names)
        if not extra_params and param_names:
            continue

        try:
            response = getattr(client.service, method_name)(loginName=LOGIN, password=PASSWORD, **extra_params)
            print("\nResponse:")
            print(response)

            if method_name == "getVServerStatToken" and isinstance(response, str):
                print_stat_token(response)

        except Exception as e:
            print(f"Error during request: {e}")

if __name__ == "__main__":
    main()
