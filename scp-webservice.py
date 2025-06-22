import os
import sys
import json
import argparse
import urllib.parse
from dotenv import load_dotenv
from zeep import Client
from zeep.helpers import serialize_object
from zeep.exceptions import Fault

WSDL_URL = 'https://www.servercontrolpanel.de/WSEndUser?wsdl'

# Load credentials
load_dotenv() 
LOGIN = os.getenv("NETCUP_LOGIN") or input("Enter NETCUP_LOGIN: ")
PASSWORD = os.getenv("NETCUP_PASSWORD") or input("Enter NETCUP_PASSWORD: ")

client = Client(WSDL_URL)

# Corrected parameter names and added language/year/month where required
OPERATIONS = {
    'getUserData': [],
    'getVServers': [],
    'getVServerInformation': ['vservername'],
    'getVServerIPs': ['vserverName'],
    'getVServerState': ['vserverName'],
    'getVServerUptime': ['vserverName'],
    'getVServerNickname': ['vservername'],
    'setVServerNickname': ['vservername', 'vservernickname'],
    'getVServerLogEntryCount': ['vservername'],
    'getVServerLogEntries': ['vservername', 'start', 'results', 'language'],
    'getVServerUpdateNotification': ['vserverName'],
    'stopVServer': ['vserverName'],
    'startVServer': ['vserverName'],
    'vServerACPIReboot': ['vserverName'],
    'vServerACPIShutdown': ['vserverName'],
    'vServerStart': ['vserverName'],
    'vServerSuspend': ['vserverName'],
    'vServerResume': ['vserverName'],
    'vServerRestore': ['vserverName'],
    'vServerReset': ['vserverName'],
    'vServerPoweroff': ['vserverName'],
    'addCloudVLANInterface': ['vservername', 'cloudvlanid', 'driver'],
    'changeIPRouting': ['routedIP', 'routedMask', 'destinationVserverName', 'destinationInterfaceMAC'],
    'getVServerStatToken': ['vserverName'],
    'getPanelSettings': [],
    'setPanelSettings': ['settings'],
    'getLoginToken': [],
    'changeUserPassword': ['newPassword'],
    'sendPasswordResetRequest': [],
}

def prompt_inputs(params):
    """Prompt user for parameter input interactively"""
    inputs = {}
    for param in params:
        val = None

        if param in ("vserverName", "vservername", "destinationvservername"):
            vservers = client.service.getVServers(loginName=LOGIN, password=PASSWORD)
            if not vservers:
                print("No vServers available.")
                return {}
            print("Available vServers:")
            for i, vs in enumerate(vservers, 1):
                print(f"{i}. {vs}")
            try:
                idx = int(input(f"Select {param} (number): ")) - 1
                if 0 <= idx < len(vservers):
                    val = vservers[idx]
                else:
                    print("Invalid selection.")
                    return {}
            except Exception:
                print("Invalid input.")
                return {}

        elif param == "driver":
            print("Available drivers: virtio, e1000, rtl8139")
            val = input("Enter driver [virtio]: ").strip()
            if not val:
                val = "virtio"
            if val not in ("virtio", "e1000", "rtl8139"):
                print("Invalid driver.")
                return {}

        elif param == "start" and 'getVServerLogEntries' in OPERATIONS:
            val = input("Which log entry to start with? (0 = most recent) [0]: ")
            if not val:
                val = "0"

        elif param == "results" and 'getVServerLogEntries' in OPERATIONS:
            val = input("Max log entries [10]: ")
            if not val:
                val = "10"

        elif param == "language" and 'getVServerLogEntries' in OPERATIONS:
            val = input("Language [en]: ")
            if not val:
                val = "en"

        else:
            val = input(f"Enter {param}: ")

        if param in ("start", "results", "cloudvlanid", "year", "month", "day"):
            try:
                val = int(val)
            except ValueError:
                print(f"Invalid number for {param}.")
                return {}

        inputs[param] = val

    return inputs

def call_method(method_name, params, json_output=False):
    """Call a SOAP method and handle response"""
    try:
        method = getattr(client.service, method_name)
        response = method(loginName=LOGIN, password=PASSWORD, **params)
        if method_name == "getVServerStatToken" and isinstance(response, str):
            encoded = urllib.parse.quote(response)
            print(f"\nStat Token:\nRaw: {response}\nURL-safe: {encoded}")
        elif json_output:
            print(json.dumps(serialize_object(response), indent=2, ensure_ascii=False))
        else:
            print("\nResponse:\n", response)
    except Fault as fault:
        print(f"SOAP Fault: {fault}")
    except Exception as e:
        print(f"Error: {e}")

def interactive_mode(json_output, loop=False):
    """Run the interactive CLI interface"""
    while True:
        print("\nAvailable Actions:")
        for i, op in enumerate(OPERATIONS.keys(), 1):
            print(f"{i}. {op}")
        print("0. Exit")

        try:
            choice = int(input("Select an option: "))
            if choice == 0:
                break
            method_name = list(OPERATIONS.keys())[choice - 1]
        except Exception:
            print("Invalid selection.")
            if not loop:
                break
            continue

        param_names = OPERATIONS[method_name]
        user_inputs = prompt_inputs(param_names)
        if param_names and not user_inputs:
            if not loop:
                break
            continue

        call_method(method_name, user_inputs, json_output)

        if not loop:
            break

def main():
    parser = argparse.ArgumentParser(description="Netcup SCP SOAP CLI")
    parser.add_argument("--action", help="SOAP action to perform", choices=OPERATIONS.keys())
    parser.add_argument("--params", help="JSON string of parameters for the action", default="{}")
    parser.add_argument("--json", help="Output in JSON", action="store_true")
    parser.add_argument("--continue", dest="loop", help="Keep returning to the main menu in interactive mode", action="store_true")
    args = parser.parse_args()

    if args.action:
        try:
            params = json.loads(args.params)
            missing = [p for p in OPERATIONS[args.action] if p not in params]
            if missing:
                print(f"Missing parameters: {missing}")
                sys.exit(1)
            call_method(args.action, params, args.json)
        except json.JSONDecodeError:
            print("Invalid JSON passed to --params")
            sys.exit(1)
    else:
        interactive_mode(args.json, loop=args.loop)

if __name__ == "__main__":
    main()
