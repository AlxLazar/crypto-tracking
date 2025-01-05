from requests import get
from matplotlib import pyplot as plt
from datetime import datetime

import os
from dotenv import load_dotenv
# Load secrets from .env file
load_dotenv()

API_KEY = os.getenv("ETHERSCAN_API_ACCESS_KEY")
address = os.getenv("MY_ETH_ADDRESS")
BASE_URL = "https://api.etherscan.io/v2/api"
ETH_VALUE = 10 ** 18

transactions_chain_list_eth = {
    "ETH-Mainnet": "1",
    "Arbitrum One Mainnet": "42161",
    "Base Mainnet": "8453",
    "Blast Mainnet": "81457",
    "Linea Mainnet": "59144",
    "OP Mainnet": "10",
    "Scroll Mainnet": "534352",
    "Taiko Mainnet": "167000",
    "zkSync Mainnet": "324"
}

transactions_chain_list_evm_others = {
    "Avalanche C-Chain": "43114",
    "BNB Smart Chain Mainnet": "56",
    "Mantle Mainnet": "5000",
    "Polygon Mainnet": "137",
    "Polygon zkEVM Mainnet": "1101",
}

# Function used to build the API call based on which arguments are expected by the API endpoint
def make_api_url(chainid, module, action, address, **kwargs):
    url = BASE_URL + f"?chainid={chainid}&module={module}&action={action}&address={address}&apikey={API_KEY}"

    for key, value in kwargs.items():
        url += f"&{key}={value}"

    return url

# Function used to pull the latest account balance (in ETH)
def get_account_balance(address, chainid):
    balance_url = make_api_url(chainid, "account", "balance", address, tag="latest")
    response = get(balance_url)
    data = response.json()

    value = int(data["result"]) / ETH_VALUE

    return value

# Function used to pull all transaction history for the account (both normal and internal transactions)
def get_transactions(address):
    # Normal transactions
    normal_tx_url = make_api_url("1", "account", "txlist", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
    response_normal = get(normal_tx_url)
    transaction_data = response_normal.json()["result"]

    # Internal transactions
    internal_tx_url = make_api_url("1", "account", "txlistinternal", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
    response_internal = get(internal_tx_url)
    data_internal = response_internal.json()["result"]

    # Concatenate normal and internal transactions
    transaction_data.extend(data_internal)
    transaction_data.sort(key=lambda x: int(x["timeStamp"]))

    current_balance = 0
    balances = []
    times = []

    # Loop through the transaction history and build a historical list of inbound and outbound ETH values
    for tx in transaction_data:
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

# for chain, id in transactions_chain_list_eth.items():
#     eth = get_account_balance(address,id)
#     print(eth)

get_transactions(address)