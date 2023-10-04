
# Ethereum Token Holders Fetcher CLI

This command-line tool fetches the holders of an Ethereum token and their respective balances. It processes the Ethereum blockchain in chunks of 1000 blocks to efficiently retrieve the data and updates a JSON file with the holder addresses and their balances.

## Requirements

- Python 3.x
- `requests` library
- `tqdm` library

You can install the required libraries using pip:

```bash
pip install requests tqdm
```

## Setup

1. Set up an account on [Infura](https://infura.io/).
2. Create a new project on Infura and obtain the Project ID.
3. Replace `YOUR_INFURA_PROJECT_ID` in the URL `https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID` within the script with your actual Infura Project ID.

## Usage

To fetch the holders and their balances for a specific Ethereum token, run:

```bash
python script_name.py CONTRACT_ADDRESS
```

Replace:
- `script_name.py` with the name you've saved the script as.
- `CONTRACT_ADDRESS` with the Ethereum contract address of the token you want to fetch holders for.

The tool will display a progress bar showing the progress of block retrieval based on the total number of blocks and the speed of block retrieval. Once completed, the holder addresses and their balances will be stored in a file named `holders_balances.json`.

## How It Works

- The tool first determines the latest block on the Ethereum mainnet.
- Starting from the first block, it fetches logs in chunks of 1000 blocks until it reaches the latest block.
- For each chunk, it retrieves the logs to identify token transfer events and extracts the sender and receiver addresses.
- The tool then queries the token contract's `balanceOf` function for each new holder to get their balance.
- The holder addresses and their balances are stored and updated in a JSON file named `holders_balances.json`.

## Note

Fetching data from the Ethereum blockchain, especially for tokens with a large number of transfers and holders, can be time-consuming. Ensure you have a stable internet connection and be patient as the tool processes the blocks.

---
