# Arbitrum Airdrop Mass Claimer

This script will wait for the airdrop to go live, claim from multiple addresses and send the $ARB to a single main wallet. 

## Prerequisites

### Using pipenv (Recommended)

```
pipenv shell
pipenv install
python main.py
```

### Using requirements.txt

```
pip install -r requirements.txt
python main.py
```

## Configuration

You need to fill in the config. I strongly recommend not using arb1.arbitrum.io as it will probably go down during the claim. Get your own RPC at Infura or Alchemy.

The tokens will be sent to `main_address`. Please ensure triple check this address is correct, or you will get NO TOKENS. 

```
{
    "privatekeys": [
        "pk1",
        "pk2",
        "pk3"
    ],
    "rpc": "[YOUR ALCHEMY RPC, DON'T USE arb1.arbitrum.io]",
    "main_address": "0xabc"
}
```