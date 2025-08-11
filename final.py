# ========== ONLINE DEVICE CODE ==========

from bitcoinlib.wallets import Wallet
from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import HDKey
from bitcoinlib.psbt import PSBT
import base64
import requests
import time

# Step 1: Load public keys from offline devices
# These should be collected securely via QR code, USB, or file transfer
key1_pub = HDKey(import_key='xpub1...')
key2_pub = HDKey(import_key='xpub2...')
key3_pub = HDKey(import_key='xpub3...')

# Step 2: Create multisig wallet (2-of-3)
multisig_wallet = Wallet.create(
    'MyMultisigWallet', 
    keys=[key1_pub, key2_pub, key3_pub],
    network='bitcoin',
    witness_type='segwit',  # P2WSH
    multisig=2
)

print("Multisig Address:", multisig_wallet.get_key().address)

# Step 3: Create a PSBT transaction
# NOTE: Replace UTXO and destination with actual data
tx = Transaction(network='bitcoin')
tx.add_input(address='your_multisig_address', value=10000)  # Replace with real UTXO details
tx.add_output(address='destination_btc_address', value=9000)
psbt = PSBT.from_transaction(tx)

# Step 4: Export unsigned PSBT to file for offline signing
psbt_base64 = psbt.to_base64()
with open("unsigned_psbt.txt", "w") as f:
    f.write(psbt_base64)

print("Unsigned PSBT saved to 'unsigned_psbt.txt'. Share this with signers.")

# ========== OFFLINE DEVICE CODE (run separately on each airgapped device) ==========

# Step 5: Load PSBT and sign with private key (example with passphrase)
# This code is to be run on airgapped devices
from bitcoinlib.psbt import PSBT
from bitcoinlib.keys import HDKey

with open("unsigned_psbt.txt", "r") as f:
    psbt_base64 = f.read()

psbt = PSBT.from_base64(psbt_base64)

# Load private key securely (NEVER expose this key online)
signing_key = HDKey().from_passphrase('your secure passphrase')
psbt.sign(signing_key)

# Save signed PSBT to file for return to coordinator
signed_psbt = psbt.to_base64()
with open("signed_psbt_1.txt", "w") as f:
    f.write(signed_psbt)

print("Signed PSBT saved. Share it with the coordinator.")

# ========== BACK ON ONLINE DEVICE ==========

# Step 6: Combine signed PSBTs
from bitcoinlib.psbt import PSBT

with open("signed_psbt_1.txt", "r") as f1, open("signed_psbt_2.txt", "r") as f2:
    psbt1 = PSBT.from_base64(f1.read())
    psbt2 = PSBT.from_base64(f2.read())

# Merge signatures
psbt1.combine(psbt2)

# Step 7: Finalize and broadcast
if psbt1.is_fully_signed():
    final_tx = psbt1.tx()
    final_tx_hex = final_tx.as_hex()
    print("Transaction ready to broadcast:", final_tx_hex)

    # Broadcast using Blockstream API
    broadcast_response = requests.post(
        'https://blockstream.info/api/tx',
        data=final_tx_hex,
        headers={'Content-Type': 'text/plain'}
    )

    if broadcast_response.status_code == 200:
        txid = broadcast_response.text.strip()
        print("Broadcast success! TXID:", txid)

        # Step 8: Monitor TXID status until confirmed
        print("Checking TXID status...")
        while True:
            status_response = requests.get(f'https://blockstream.info/api/tx/{txid}/status')
            if status_response.status_code == 200:
                status = status_response.json()
                print("Confirmed:", status['confirmed'])
                if status['confirmed']:
                    print("Block Height:", status['block_height'])
                    print("Block Hash:", status['block_hash'])
                    break
                else:
                    print("Unconfirmed... checking again in 15 seconds")
            else:
                print("Status check failed.")
            time.sleep(15)
    else:
        print("Broadcast failed:", broadcast_response.text)
else:
    print("Not enough signatures yet.")

