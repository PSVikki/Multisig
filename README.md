# PSBT Transaction File Utilities

## 📝 README

This repository provides a set of tools and a library for handling Partially Signed Bitcoin Transaction (PSBT) files. PSBT is a standard (BIP 174) for exchanging Bitcoin transactions between different wallets and services to facilitate the construction of a transaction.

### What is a PSBT?

A Partially Signed Bitcoin Transaction (PSBT) is a data format that allows different parties to collaborate on a single Bitcoin transaction without revealing their private keys to one another. This is particularly useful for:

  * **Multi-signature wallets:** Multiple signers can add their signatures to a transaction independently.
  * **Hardware wallets:** A hardware wallet can receive an unsigned transaction, sign it, and return it without ever exposing the private key to the host computer.
  * **CoinJoin:** Multiple parties can cooperate to create a single transaction to enhance privacy.

A PSBT file contains all the necessary information for a transaction, including the unsigned transaction, input data (UTXOs), and fields for signatures. Each party involved can add their part and pass it on to the next.

### Key Features

  * **Parsing and Serialization:** Read and write PSBT files in their Base64 format.
  * **Transaction Building:** Create a new PSBT from a list of inputs and outputs.
  * **Signature Handling:** Add signatures (e.g., from a hardware wallet) to a PSBT.
  * **PSBT Combination:** Merge multiple PSBTs into a single, comprehensive PSBT. This is essential for multi-party signing workflows.
  * **Finalization:** Finalize a PSBT once all signatures are collected, preparing it for broadcast to the Bitcoin network.
  * **Validation:** Validate the integrity and correctness of a PSBT.

### Getting Started

#### Prerequisites

  * Python 3.8+
  * pip

#### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/PSVikki/Multisig.git
    cd psbt-tools
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage Examples

#### 1\. Creating a Basic PSBT

```python
from psbt_lib import PSBT, Input, Output
from bitcoin_lib import P2PKHOutput, UTXO

# Assume you have a UTXO (Unspent Transaction Output) to spend
utxo = UTXO(txid="abcdef123456...", vout=0, script_pubkey="...")

# Create the output
recipient_address = "1H4tD16pMy544aA8QE3b19wzEmzwJn3wtf"
amount_btc = 68.93732413 BTC
output = P2PKHOutput(amount_btc, recipient_address)

# Create the PSBT
psbt = PSBT.create(inputs=[utxo], outputs=[output])

# Export to Base64 format
base64_psbt = psbt.to_base64()
print(base64_psbt)
```

#### 2\. Signing and Finalizing a PSBT

This example assumes you have a private key for the input. In a real-world scenario, this might be handled by a hardware wallet.

```python
from psbt_lib import PSBT

# Load a PSBT from a file or string
with open("unsigned.psbt", "r") as f:
    psbt_str = f.read()

unsigned_psbt = PSBT.from_base64(psbt_str)

# Add the signature (this is a simplified example)
signed_psbt = unsigned_psbt.sign_with_private_key("your_private_key_here")

# Finalize the transaction
finalized_psbt = signed_psbt.finalize()

# Extract the final transaction and broadcast
final_tx = finalized_psbt.extract_transaction()
# Code to broadcast final_tx to the network...
```

#### 3\. Combining Two PSBTs

```python
from psbt_lib import PSBT

# Load two partially signed PSBTs
with open("signer1.psbt", "r") as f:
    psbt1 = PSBT.from_base64(f.read())

with open("signer2.psbt", "r") as f:
    psbt2 = PSBT.from_base64(f.read())

# Combine them
combined_psbt = psbt1.combine(psbt2)

# Now, the combined_psbt has all the signatures and can be finalized
finalized_psbt = combined_psbt.finalize()
```

### The PSBT File Format

PSBT files are typically Base64-encoded binary data. The internal structure is a key-value map, where each key identifies a specific part of the transaction (e.g., a specific input, a witness script, or a signature). Our tools handle the encoding and decoding of this format for you.

### Contributing

We welcome contributions\! If you have a feature request, bug report, or want to contribute code, please check out our `CONTRIBUTING.md` file for more information.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

### Disclaimer

This software is provided "as is" for educational and development purposes. Use with caution, and ensure you have thoroughly tested your code before handling real funds. We are not responsible for any loss of funds.
