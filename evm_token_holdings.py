import requests
import math
import os
from dotenv import load_dotenv
# Load secrets from .env file
load_dotenv()

address = os.getenv("MY_ETH_ADDRESS")

# Function used to pull all curent token holdings from ETH mainnet
def print_eth_tokens():
    balances_url = "https://eth-mainnet.g.alchemy.com/v2/KisLzhy0b63vMZBIjmoI_FPBZrbr1y4Z"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "alchemy_getTokenBalances",
        "params": [address],
        "id": 1
    }

    balances_response = requests.post(balances_url, headers=headers, json=payload)

    json_response = balances_response.json()
    # print(json_response['result']['tokenBalances'])

    final_response = []
    for item in json_response['result']['tokenBalances']:
        metadata_url = "https://eth-mainnet.g.alchemy.com/v2/KisLzhy0b63vMZBIjmoI_FPBZrbr1y4Z"
        metadata_headers = {
            "Content-Type": "application/json"
        }
        metadata_payload = {
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenMetadata",
            "params": [item['contractAddress']],
            "id": 1
        }
        metadata_response = requests.post(metadata_url, headers=metadata_headers, json=metadata_payload)
        metadata_json = metadata_response.json()
        # print(metadata_json)
        if int(item['tokenBalance'], 16) != 0:
            final_response.append({'symbol': metadata_json['result']['symbol'], 'name': metadata_json['result']['name'], 'contractAddress': item['contractAddress'], 'balance': round(float(int(item['tokenBalance'], 16))/math.pow(10,int(metadata_json['result']['decimals'])),2)})
    print(final_response)

    # # Print the response
    # print(response.status_code)  # HTTP status code
    # print(response.json())       # Parsed JSON response

print_eth_tokens()