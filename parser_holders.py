import requests
import json
import os
import argparse
from tqdm import tqdm

def get_latest_block(infura_url):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_blockNumber",
        "params": []
    }
    response = requests.post(infura_url, json=payload)
    return int(response.json().get('result', '0x0'), 16)

def get_logs_in_range(contract_address, infura_url, from_block, to_block):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getLogs",
        "params": [{
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
            "address": contract_address,
            "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]
        }]
    }
    response = requests.post(infura_url, json=payload)
    return response.json().get('result', [])

def get_balance(contract_address, holder, infura_url):
    # Create the data payload for the balanceOf function
    data = '0x' + '70a08231'  # Function signature for balanceOf(address)
    data += holder[2:].rjust(64, '0')  # Append the holder address (without the '0x' prefix) and pad it to 64 characters

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [{
            "to": contract_address,
            "data": data
        }, "latest"]
    }

    response = requests.post(infura_url, json=payload)
    balance_hex = response.json().get('result', '0x0')
    return int(balance_hex, 16)  # Convert hex to int

def update_json_file_with_balance(filename, contract_address, infura_url, new_holders):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            holder_balances = json.load(file)
    else:
        holder_balances = {}

    for holder in new_holders:
        if holder not in holder_balances:
            holder_balances[holder] = get_balance(contract_address, holder, infura_url)

    with open(filename, 'w') as file:
        json.dump(holder_balances, file)


def parse_blocks(contract_address, infura_url, filename="holders_balances.json"):
    latest_block = get_latest_block(infura_url)
    current_block = 1
    chunk_size = 1000

    # Initialize progress bar
    pbar = tqdm(total=latest_block, desc="Processing blocks", ncols=100)

    while current_block <= latest_block:
        logs = get_logs_in_range(contract_address, infura_url, current_block, current_block + chunk_size - 1)
        new_holders = set()
        for log in logs:
            new_holders.add(log['topics'][1])
            new_holders.add(log['topics'][2])

        update_json_file_with_balance(filename, contract_address, infura_url, new_holders)

        # Update progress bar
        pbar.update(chunk_size)
        current_block += chunk_size

    pbar.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Ethereum token holders and their balances.")
    parser.add_argument("contract_address", type=str, help="Ethereum contract address of the token.")
    args = parser.parse_args()

    infura_url = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
    parse_blocks(args.contract_address, infura_url)
