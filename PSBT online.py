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
        "txid": "b1a1a5b82143003020689b0d105a1e7b1652136e0d37e6f8595a8e0f6c2c62c9",
        "vout": 0,
        "amount": 0.05,
        "scriptPubKey": "76a914c622a55986872a3e0f6c9d06637e1713e5e4933988ac"
    },
    {
        "txid": "a9a23c31821464455f7560447335d886a11782e4e1a0d33e5c709e3a3e61884b",
        "vout": 1,
        "amount": 0.1,
        "scriptPubKey": "76a914c622a55986872a3e0f6c9d06637e1713e5e4933988ac"
    }
]

# The address of the recipient
recipient_address = "tb1qj5lqj4p3j7f5y5w2w4f8h0l0t9p2q0t7e7s7q5"

# The amount to send (in BTC)
amount_to_send = 0.05

# Your change address (where remaining funds will be sent)
change_address = "tb1qj2m6d7u7a2e5x4f7g8h9l0p0t7s8d0e7x2z9t2c"

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