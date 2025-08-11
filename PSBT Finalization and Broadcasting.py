Creating a Bitcoin offline transaction using a Partially Signed Bitcoin Transaction (PSBT) is the modern and highly secure way to do it. The PSBT format (defined in BIP 174) is specifically designed for offline signing workflows. It allows for a transaction to be constructed on an online machine and then passed to an offline machine for signing without exposing sensitive private keys to the internet.

This process is generally broken down into three main stages:

1.  **PSBT Creation (Online):** A "watch-only" wallet or an online application constructs a transaction and populates it with all the necessary information, such as the UTXOs to be spent, the recipient's address, the amount, and the change address. It does not add any signatures. The output is a raw PSBT in base64 format.
2.  **PSBT Signing (Offline):** The PSBT is transferred to an offline, air-gapped machine. Using the private key (which never leaves the device), the PSBT is signed. The result is a new PSBT with partial signatures.
3.  **PSBT Finalization and Broadcasting (Online):** The partially signed PSBT is transferred back to an online machine. A software wallet or a broadcasting service finalizes the transaction by adding the final scripts, and then broadcasts it to the Bitcoin network.

The following Python code demonstrates this three-step process conceptually. We will use the `bitcoinlib` library, which supports PSBT.

**Disclaimer:** This is a simplified example for educational purposes. It's crucial to understand the risks and complexities of real-world Bitcoin transactions, including UTXO management, fee calculation, and security practices. **Always test with a Testnet wallet and a Testnet faucet first.**

-----

### Part 1: PSBT Creation (Online)

This script creates the PSBT. It needs to know your UTXOs, the recipient's address, and the amount.

```python
# Part 1: Run on an online machine to create the PSBT.
# You will need to get your UTXO details from a block explorer or a watch-only wallet.

from bitcoinlib.wallets import Wallet, wallet_delete
from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key
from bitcoinlib.networks import Network
import json

# --- CONFIGURATION (FILL IN YOUR DETAILS) ---

# The network you are working on ('mainnet', 'testnet', or 'regtest')
NETWORK = 'testnet'

# The UTXOs you want to spend (from a block explorer or your wallet)
# This data MUST be accurate.
utxos_to_spend = [
    {
        "txid": "dd23e8df8f2875c832bfbfdfca5b9faeb0b7b95d7446fc06eead8da8a9af17e9",
        "vout": 0,
        "amount": 45.42,
        "scriptPubKey": "1H4tD16pMy544aA8QE3b19wzEmzwJn3wtf"
    },
    {
        "txid": "3c185ef04212b43cf3eeaa7ae18e5df0a0948dd662ff5d96ddba413bf70de11a",
        "vout": 1,
        "amount":68.93732413,
        "scriptPubKey": "191oTkxrkmHFs3XGdUAzwkpKA1JKUVggFp"
    }
]

# The address of the recipient
recipient_address = "1H4tD16pMy544aA8QE3b19wzEmzwJn3wtf"

# The amount to send (in BTC)
amount_to_send = 0.05

# Your change address (where remaining funds will be sent)
change_address = "1H4tD16pMy544aA8QE3b19wzEmzwJn3wtf"

# --- PSBT CREATION LOGIC ---

try:
    print("--- Creating PSBT (Online) ---")

    # Calculate total input amount
    total_input_amount = sum(utxo['amount'] for utxo in utxos_to_spend)

    # Calculate fee. This is a critical step. For a real transaction, you
    # would calculate this dynamically based on current network conditions.
    # For this example, we use a fixed fee.
    fee = 0.00005  # A simple, fixed fee in BTC

    # Calculate the change amount
    change_amount = total_input_amount - amount_to_send - fee

    if change_amount < 0:
        raise ValueError("Insufficient funds to cover amount and fee.")

    # Create a new PSBT (Partially Signed Bitcoin Transaction)
    tx = Transaction(network=NETWORK)
    tx.set_psbt(True) # This is the key line to create a PSBT

    # Add inputs from the UTXO list
    for utxo in utxos_to_spend:
        tx.add_input(utxo['txid'], utxo['vout'], utxo['scriptPubKey'])

    # Add outputs
    tx.add_output(recipient_address, amount_to_send)
    tx.add_output(change_address, change_amount)

    # Get the PSBT in base64 format
    psbt_base64 = tx.psbt()

    print("\nPSBT created successfully. Transfer this PSBT to an offline machine for signing.")
    print("\n--- PSBT (Base64) ---")
    print(psbt_base64)

    # Save the PSBT to a file to transfer via USB
    with open("unsigned_transaction.psbt", "w") as f:
        f.write(psbt_base64)

except Exception as e:
    print(f"An error occurred: {e}")

```

### Part 2: PSBT Signing (Offline)

This script runs on a secure, air-gapped machine. It takes the base64 PSBT, signs it with your private key, and outputs the signed PSBT.

```python
# Part 2: Run on a secure, offline (air-gapped) machine.
# DO NOT CONNECT THIS MACHINE TO THE INTERNET.

from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key
import json

# --- CONFIGURATION (FILL IN YOUR DETAILS) ---

# Load the unsigned PSBT from the file transferred from the online machine
psbt_base64_unsigned = open("unsigned_transaction.psbt", "r").read()

# Your private key in WIF format. This is the only sensitive data.
# This private key MUST NEVER be on an online machine.
my_private_key_wif = "cM...your_private_key_in_wif_format...t8"

# --- PSBT SIGNING LOGIC ---

try:
    print("--- Signing PSBT (Offline) ---")
    
    # Load the PSBT from the base64 string
    tx = Transaction.from_psbt(psbt_base64_unsigned)
    
    # Get the private key object
    key = Key(my_private_key_wif)
    
    # Sign the PSBT. The library handles the signing of the transaction inputs.
    signed_tx = key.sign_transaction(tx)
    
    # Get the signed PSBT in base64 format
    signed_psbt_base64 = signed_tx.psbt()

    print("\nPSBT signed successfully. Transfer the signed PSBT back to an online machine.")
    print("\n--- Signed PSBT (Base64) ---")
    print(signed_psbt_base64)
    
    # Save the signed PSBT to a file to transfer via USB
    with open("signed_transaction.psbt", "w") as f:
        f.write(signed_psbt_base64)

except Exception as e:
    print(f"An error occurred: {e}")
```

### Part 3: PSBT Finalization and Broadcasting (Online)

This script takes the signed PSBT and broadcasts it to the Bitcoin network.

```python
# Part 3: Run on an online machine to broadcast the signed transaction.

from bitcoinlib.transactions import Transaction
from bitcoinlib.services.services import Service
import requests

# --- CONFIGURATION ---

# Load the signed PSBT from the file transferred from the offline machine
signed_psbt_base64 = open("signed_transaction.psbt", "r").read()

# --- BROADCAST LOGIC ---

try:
    print("--- Finalizing and Broadcasting PSBT (Online) ---")

    # Load the signed PSBT
    tx = Transaction.from_psbt(signed_psbt_base64)

    # Finalize the transaction
    tx.finalize()
    
    # Get the final raw transaction hex
    raw_tx_hex = tx.hex()

    # Use a service provider to broadcast the raw transaction
    # Many block explorers have APIs for this.
    # We'll use a public API for this example.
    
    api_url = "https://blockstream.info/tx/push"
    
    response = requests.post(api_url, data=raw_tx_hex)
    response.raise_for_status()
    tx_id = response.text

    print("\nTransaction broadcast successfully!")
    print(f"Transaction ID (TXID): {tx_id}")
    print(f"Check the transaction on a block explorer: https://blockstream.info/tx/push}")

except Exception as e:
    print(f"An error occurred while broadcasting: {e}")
    if 'response' in locals():
        print(f"API response: {response.text}")

```
