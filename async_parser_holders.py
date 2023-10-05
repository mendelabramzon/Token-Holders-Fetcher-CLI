import requests
import json
import os
import argparse
from tqdm import tqdm
import asyncio
import aiohttp
from aiohttp.client_exceptions import ContentTypeError
from aiohttp.client_exceptions import ClientConnectorError



TRANSFER_EVENT_SIGNATURE = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"  # ERC20 Transfer event

CHUNK_SIZE = 1000

ENDPOINTS = list(set([
    "https://cloudflare-eth.com",
    "https://main-light.eth.linkpool.io",
    "https://eth-rpc.gateway.pokt.network",
    "https://api.mycryptoapi.com/eth",
    "https://mainnet.eth.cloud.ava.do/",
    "https://ethereumnodelight.app.runonflux.io",
    "https://rpc.flashbots.net/",
    "https://rpc.ankr.com/eth",
    "https://mainnet.eth.cloud.ava.do/",
    "https://eth-mainnet.nodereal.io/v1/",
    "https://eth-mainnet.public.blastapi.io",
    "https://api.securerpc.com/v1",
    "https://eth-mainnet.rpcfast.com",
    "https://1rpc.io/eth",
    "https://ethereum.publicnode.com",
    "https://rpc.payload.de",
    "https://llamanodes.com/",
    "https://eth.api.onfinality.io/public",
    'https://eth.llamarpc.com',
    'https://endpoints.omniatech.io/v1/eth/mainnet/public',
    'https://rpc.ankr.com/eth',
    'https://ethereum.publicnode.com',
    'wss://ethereum.publicnode.com',
    'https://rpc.builder0x69.io',
    'https://rpc.mevblocker.io',
    'https://virginia.rpc.blxrbdn.com',
    'https://uk.rpc.blxrbdn.com',
    'https://singapore.rpc.blxrbdn.com',
    'https://eth.rpc.blxrbdn.com',
    'https://cloudflare-eth.com',
    'https://eth-mainnet.public.blastapi.io',
    'https://api.securerpc.com/v1',
    'https://eth-rpc.gateway.pokt.network',
    'https://eth-mainnet-public.unifra.io',
    'https://ethereum.blockpi.network/v1/rpc/public',
   'https://rpc.payload.de',
    'https://api.zmok.io/mainnet/oaen6dy8ff6hju9k',
    'https://eth-mainnet.g.alchemy.com/v2/demo',
    'https://core.gashawk.io/rpc',
    'https://eth-mainnet.rpcfast.com?api_key=xbhWBI1Wkguk8SNMu1bvvLurPGLXmgwYeC4S6g2H7WdwFigZSmPWVZRxrskEQwIf',
    'https://rpc.eth.gateway.fm',
    'https://eth.meowrpc.com',
    'https://eth.drpc.org',
    'https://eth-mainnet.diamondswap.org/rpc'
]))

MAX_RETRIES = 3  # Number of retries for each endpoint

async def async_get_logs_in_range(contract_address, endpoint_url, start_block, end_block):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getLogs",
        "params": [{
            "fromBlock": hex(start_block),
            "toBlock": hex(end_block),
            "address": contract_address,
            "topics": [TRANSFER_EVENT_SIGNATURE]
        }]
    }

    for _ in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        print(f"Error for endpoint {endpoint_url}: {response.status} {response.reason}")
                        continue  # Retry
                    data = await response.json()
                    return data.get('result', [])
        
        except ContentTypeError as ce:
            print(f"Content type error for endpoint {endpoint_url}: {str(ce)}")
            ENDPOINTS.remove(endpoint_url)  # Remove the endpoint from the list
            return []
        except ClientConnectorError as cce:
            print(f"SSL error for endpoint {endpoint_url}: {str(cce)}")
            ENDPOINTS.remove(endpoint_url)  # Remove the endpoint from the list
            return []

        except Exception as e:
            print(f"Error fetching logs from endpoint {endpoint_url}: {str(e)}")
            continue  # Retry

    # If we reach here, it means all retries failed. Consider removing the endpoint.
    print(f"Removing problematic endpoint: {endpoint_url}")
    ENDPOINTS.remove(endpoint_url)
    return []



async def async_get_latest_block(endpoint_url):
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint_url, json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}) as response:
            data = await response.json()
            return int(data['result'], 16)

async def async_get_balance(contract_address, holder, endpoint_url):
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

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint_url, json=payload) as response:
            response_data = await response.json()
            balance_hex = response_data.get('result', '0x0')
            return int(balance_hex, 16)  # Convert hex to int

async def async_update_json_file_with_balance(filename, contract_address, endpoint_url, new_holders):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            holder_balances = json.load(file)
    else:
        holder_balances = {}

    for holder in new_holders:
        if holder not in holder_balances:
            holder_balances[holder] = await async_get_balance(contract_address, holder, endpoint_url)

    with open(filename, 'w') as file:
        json.dump(holder_balances, file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Ethereum token holders and their balances.")
    parser.add_argument("contract_address", type=str, help="Ethereum contract address of the token.")
    parser.add_argument("--start-block", type=int, default=1, help="Block number to start fetching from. Default is 1.")
    args = parser.parse_args()

    async def main():
            # Use the first endpoint to get the latest block
        latest_block = await async_get_latest_block(ENDPOINTS[0])
    
     # Create a tqdm progress bar
        pbar = tqdm(total=latest_block, desc="Processing blocks", ncols=100)

    # Create tasks for each endpoint to fetch logs asynchronously
        tasks = [async_get_logs_in_range(args.contract_address, url, args.start_block, latest_block) for url in ENDPOINTS]
    
    # Gather results and filter out empty results
        all_logs = [logs for logs in await asyncio.gather(*tasks) if logs]
    
    # Process logs
        for logs in all_logs:
            # Your logic to process each set of logs
            # For demonstration purposes, we'll just print the number of logs fetched from each endpoint
            print(f"Fetched {len(logs)} logs from endpoint.")
        
            # Update the progress bar with the number of blocks processed
            pbar.update(len(logs))  # Assuming each log corresponds to a block

    # Close the progress bar
        pbar.close()

    # Run the main async function
    asyncio.run(main())

