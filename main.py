import json
import time
from web3 import Web3
from eth_account import Account

CLAIM_PERIOD_START = 16890400

# ABI of the contract with the claim() function
with open('claim_contract.abi') as f:
    contract_abi = json.load(f)

with open('multicall.abi') as f:
    multicall_abi = json.load(f)

with open("arb_token.abi") as f:
    arb_token_abi = json.load(f)

# Read config.json
with open('config.json', 'r') as f:
    config = json.load(f)


rpc_url = config['rpc']
private_keys = config['privatekeys']

# Connect to Arbitrum node
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Claim contract address
contract_address = w3.toChecksumAddress("0x67a24CE4321aB3aF51c2D0a4801c3E111D88C9d9")
arb_address = w3.toChecksumAddress("0x912CE59144191C1204E64559FE8253a0e49E6548")
multicall_address = w3.toChecksumAddress("0xcA11bde05977b3631167028862bE2a173976CA11")

main_address = w3.toChecksumAddress(config['main_address'])

# Ensure connected to Ethereum node
if not w3.isConnected():
    print("Not connected to Ethereum node.")
    exit(1)

# Instantiate contract
contract = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=contract_abi)
arb_token = w3.eth.contract(address=w3.toChecksumAddress(arb_address), abi=arb_token_abi)
multicall = w3.eth.contract(address=w3.toChecksumAddress(multicall_address), abi=multicall_abi)

while True:
    # get current block number
    current_block = multicall.functions.getBlockNumber().call()
    if current_block >= CLAIM_PERIOD_START:
        break
    else:
        print(f"Waiting for claim period to start. Current L1 block: {current_block}, Claim period start: {CLAIM_PERIOD_START}")
        print(f"Approx time remaining: {(CLAIM_PERIOD_START - current_block) * 11} seconds")
        time.sleep(5)


# Call claim() function for each private key
for pk in private_keys:
    account = Account.privateKeyToAccount(pk)
    address = account.address
    nonce = w3.eth.getTransactionCount(account.address)
    gas_price = w3.eth.gasPrice * 10 # gas price is based on the current network gas price

    claim_txn = contract.functions.claim().buildTransaction({
        'from': account.address,
        'gas': 750000,
        'gasPrice': gas_price,
        'nonce': nonce
    })

    signed_txn = account.signTransaction(claim_txn)

    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Transaction sent for {address} with hash {txn_hash.hex()}")
        txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
        if txn_receipt['status']:
            print(f"Claim successful for {address}...")
        else:
            print(f"Claim failed for {address}...")

    except Exception as e:
        print(f"Error sending transaction for private key {pk[:6]}...: {str(e)}")

# Now transfer to main address
for pk in private_keys:
    account = Account.privateKeyToAccount(pk)
    address = account.address
    nonce = w3.eth.getTransactionCount(account.address)
    gas_price = w3.eth.gasPrice * 10 # gas price is based on the current network gas price

    balance = arb_token.functions.balanceOf(address).call()

    print(f"Transferring {balance} to {main_address} from {address}")

    transfer_txn = arb_token.functions.transfer(main_address, balance).buildTransaction({
        'from': account.address,
        'gas': 500000,
        'gasPrice': gas_price,
        'nonce': nonce
    })

    signed_txn = account.signTransaction(transfer_txn)

    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Transaction sent for {address} with hash {txn_hash.hex()}")
        txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
        if txn_receipt['status']:
            print(f"Transfer successful for {address}...")
        else:
            print(f"Transfer failed for {address}...")

    except Exception as e:
        print(f"Error sending transaction for private key {pk[:6]}...: {str(e)}")
