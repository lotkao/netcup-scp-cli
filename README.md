# Netcup SCP WebService CLI

A simple Python CLI tool to interact with [Netcup's SCP SOAP API](https://www.servercontrolpanel.de/WSEndUser?wsdl). Allows you to manage virtual servers (VServers), route failover IPs, and access basic statistics.

## Features

This script supports the following operations via an interactive CLI:

* List VServers in your Netcup SCP account
* Start or stop a vServer
* Get the current state (online/offline) of a vServer
* List the IP addresses assigned to a vServer
* Change routing for a Failover IP (e.g., assign to a different vServer)
* Generate a token to download vServer usage statistics (CPU, traffic, etc.)
* Reboot, shutdown, power off or reset vServer via ACPI
* Get vServer uptime and nickname
* Retrieve and set panel settings
* Get and filter vServer logs
* Add cloud VLAN interfaces
* Manage passwords and login tokens

Additional functionality may be added based on the full WSDL definitions.

---

## Requirements

* Python 3.8+
* The following Python packages:

  * `zeep` (for SOAP client support)

Install dependencies via:

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```
zeep
```

---

## Getting Started

### 1. Clone this Repository

```bash
git clone https://github.com/YOUR_USERNAME/netcup-scp-cli.git
cd netcup-scp-cli
```

### 2. Create a Virtual Environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Your SCP Webservice Credentials

Before running the script, export your SCP login name and API password as environment variables.
**Important:** The SCP **webservice password is not the same as your control panel login password**. You must enable the SOAP API and set a specific password in the Netcup SCP panel.

```bash
export NETCUP_LOGIN="your-login-username"
export NETCUP_PASSWORD="your-soap-api-password"
```

Alternatively, you can provide them inline when running the script:

```bash
NETCUP_LOGIN=your-login NETCUP_PASSWORD=your-password python scp-webservice.py
```

---

## Running the CLI

```bash
python scp-webservice.py
```

Follow the prompts to:

* Choose an action from the menu
* Input necessary parameters (e.g. vServer selection, IPs, MAC address)

---

## References

* Netcup SOAP API Help Center: [https://helpcenter.netcup.com/en/wiki/server/scp-webservice/](https://helpcenter.netcup.com/en/wiki/server/scp-webservice/)
* Full WSDL API: [https://www.servercontrolpanel.de/WSEndUser?wsdl](https://www.servercontrolpanel.de/WSEndUser?wsdl)
* XSD schema: [https://www.servercontrolpanel.de/SCP/WSEndUser?xsd=1](https://www.servercontrolpanel.de/SCP/WSEndUser?xsd=1)

---

## License

MIT License. See `LICENSE` file if provided.
