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