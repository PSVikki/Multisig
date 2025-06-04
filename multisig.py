# Multisig Signing Tool Starter Kit (2-of-3 Example)
# This includes: Key generation, PSBT creation, signing, and broadcasting structure

from bitcoinlib.wallets import Wallet
from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import HDKey
from bitcoinlib.psbt import PSBT

# 1. Generate or import keys (here we generate 3 new keys)
key1 = HDKey().public()
key2 = HDKey().public()
key3 = HDKey().public()

# 2. Create multisig wallet (2-of-3)
multisig_wallet = Wallet.create(
    'MyMultisigWallet', 
    keys=[key1, key2, key3],
    network='bitcoin',
    witness_type='segwit',  # P2WSH
    multisig=2  # 2-of-3
)

print("Multisig Address:", multisig_wallet.get_key().address)

# 3. Create a PSBT transaction (simulate sending 0.0001 BTC)
tx = Transaction(network='bitcoin')
tx.add_input(address='your_multisig_address', value=10000)  # Replace with real UTXO details
tx.add_output(address='destination_btc_address', value=9000)
psbt = PSBT.from_transaction(tx)

# Export PSBT to share with signers
psbt_base64 = psbt.to_base64()
print("Unsigned PSBT:", psbt_base64)

# 4. Each signer loads the PSBT and signs it separately (simulate with same keys)
psbt_signer1 = PSBT.from_base64(psbt_base64)
psbt_signer1.sign(HDKey().from_passphrase('your passphrase 1'))

psbt_signer2 = PSBT.from_base64(psbt_signer1.to_base64())
psbt_signer2.sign(HDKey().from_passphrase('your passphrase 2'))

# 5. Finalize and broadcast
if psbt_signer2.is_fully_signed():
    final_tx = psbt_signer2.tx()
    print("Ready to broadcast:", final_tx.as_hex())
    # You can now broadcast using bitcoinlib or another method
else:
    print("Not enough signatures yet.")
