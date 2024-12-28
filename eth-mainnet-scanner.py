from requests import get
from matplotlib import pyplot as plt
from datetime import datetime

import os
from dotenv import load_dotenv
# Load secrets from .env file
load_dotenv()

API_KEY = os.getenv("API_ACCESS_KEY")
address = os.getenv("MY_ETH_ADDRESS")
BASE_URL = "https://api.etherscan.io/api"
ETH_VALUE = 10 ** 18

# Function used to build the API call based on which arguments are expected by the API endpoint
def make_api_url(module, action, address, **kwargs):
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"

    for key, value in kwargs.items():
        url += f"&{key}={value}"

    return url

# Function used to pull the latest account balance (in ETH)
def get_account_balance(address):
    balance_url = make_api_url("account", "balance", address, tag="latest")
    response = get(balance_url)
    data = response.json()

    value = int(data["result"]) / ETH_VALUE

    return value

# Funtion used to pull all transaction history for the account (both normal and internal transactions)
def get_transactions(address):
    # Normal transactions
    normal_tx_url = make_api_url("account", "txlist", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
    response_normal = get(normal_tx_url)
    data_normal = response_normal.json()["result"]

    # Internal transactions
    internal_tx_url = make_api_url("account", "txlistinternal", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
    response_internal = get(internal_tx_url)
    data_internal = response_internal.json()["result"]

    # Concatenate normal and internal transactions
    data_normal.extend(data_internal)
    data_normal.sort(key=lambda x: int(x["timeStamp"]))

    current_balance = 0
    balances = []
    times = []

    # Loop through the transaction history and build a historical list of inbound and outbound ETH values
    for tx in data_normal:
        to_addr = tx["to"]
        from_addr = tx["from"]
        value = int(tx["value"]) / ETH_VALUE
        if "gasPrice" in tx:
            gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / ETH_VALUE
        else:
            gas = int(tx["gasUsed"]) / ETH_VALUE

        timestamp = datetime.fromtimestamp(int(tx["timeStamp"]))

        money_inbound = to_addr.lower() == address.lower()

        if money_inbound:
            current_balance += value
        else:
            current_balance -= value + gas
        
        balances.append(current_balance)
        times.append(timestamp)

    # Plot transaction history
    plt.plot(times, balances)
    plt.show()

eth = get_account_balance(address)
print(eth)

get_transactions(address)