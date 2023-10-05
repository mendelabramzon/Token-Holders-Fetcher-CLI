
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

---

# Ethereum Token Holders Fetcher (Async Version)

This script asynchronously fetches Ethereum token holders and their balances using multiple Ethereum RPC endpoints.

## Features

- Asynchronous fetching for faster data retrieval.
- Utilizes multiple Ethereum RPC endpoints for redundancy and higher availability.
- Automatically retries failed requests.
- Automatically removes problematic endpoints that consistently fail.
- Provides a progress bar to track the processing of blocks.

## Prerequisites

- Python 3.7+
- Libraries: `aiohttp`, `requests`, `tqdm`, `argparse`

You can install the required libraries using:

```bash
pip install aiohttp requests tqdm argparse
```

## Usage

1. Clone the repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

2. Run the script:

```bash
python script_name.py <contract_address> --start-block <start_block_number>
```

Replace `<contract_address>` with the Ethereum contract address of the token and `<start_block_number>` with the block number to start fetching from. The `--start-block` argument is optional and defaults to 1.

## How It Works

1. The script first determines the latest block on the Ethereum network.
2. It then asynchronously fetches logs for ERC20 Transfer events from the specified start block to the latest block.
3. The script extracts token holders from the logs and fetches their balances.
4. All data is saved to a JSON file named `holders_balances.json`.

## Handling Endpoint Limitations

The script is designed to handle endpoint limitations:

- If a request to an endpoint fails, the script will retry it a specified number of times.
- If an endpoint consistently causes issues, it will be automatically removed from the list of endpoints.

## Contributing

Feel free to fork the repository, make changes, and submit pull requests. Feedback and contributions are welcome!

---

Note: Make sure to replace placeholders like `<repository_url>`, `<repository_directory>`, and `script_name.py` with the actual values relevant to your project.
