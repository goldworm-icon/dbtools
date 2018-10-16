# ICON DB TOOLS

* Extract data from LevelDB managed by loopchain
* Execute ICON Service with block extracted from loopchain LevelDB

# Commands

## sync

* Synchronize ICON Service statedb with confirmed_transaction_list of block db 
* Execute IconServiceEngine.invoke() with confirmed transactions extracted from block db
* Compare commit_state in block with state_root_hash created from IconServiceEngine
* Compare transaction result in block with 

```bash
(venv) $ icondbtools sync --help
usage: icondbtools sync [-h] --db DB [-s START] [-c COUNT]
                        [-o BUILTIN_SCORE_OWNER] [--stop-on-error]
                        [--no-commit] [--write-precommit-data]

optional arguments:
  -h, --help            show this help message and exit
  --db DB
  -s START, --start START
                        start height to sync
  -c COUNT, --count COUNT
                        The number of blocks to sync
  -o BUILTIN_SCORE_OWNER, --owner BUILTIN_SCORE_OWNER
                        BuiltinScoreOwner
  --stop-on-error       stop running when commit_state is different from
                        state_root_hash
  --no-commit           Do not commit
  --write-precommit-data
                        Write precommit data to file

(venv) $ icondbtools sync --db ./db_13.125.135.114:7100_icon_dex --stop-on-error
```

| key | value | desc |
|:----|:-----:|------|
| --db | string | the path of loopchain db<br>ex) --db ./db_13.125.135.114:7100_icon_dex |
| -s, --start | int | start block height to sync<br>ex) --start 1234 |
| -c, --count | int | the number of blocks to sync<br>ex) --count 100 |
| -o, --owner | string | Set buitinScoreOwner address |
| --stop-on-error | - | If an error happens, sync is stopped |
| --no-commit | - | Do not write changed states to stateDB |
| --write-precommit-data | - |  Write updated states (key:value pairs) to file for debugging |

## lastblock
Print the last block in block db

```bash
(venv) $ icondbtools lastblock --help
usage: icondbtools lastblock [-h] --db DB

optional arguments:
  -h, --help  show this help message and exit
  --db DB

(venv) $ icondbtools lastblock --db ./db_13.125.135.114:7100_icon_dex
Namespace(db='../db_data/mainnet/db', func=<function print_last_block at 0x7f8ff76b8c80>)
{'version': '0.1a', 'prev_block_hash': 'dbedbc1d62b1ce2948b90a1bc5f15f921bdb84442465757a1b72563d43b0dc56', 'merkle_tree_root_hash': '2248fa6e966f7d13ac091914a92453df017be1fa8552c115fa0ca574bd30cd81', 'time_stamp': 1538705882749492, 'confirmed_transaction_list': [{'version': '0x3', 'nid': '0x1', 'from': 'hx522bff55a62e0c75a1b51855b0802cfec6a92e84', 'to': 'hx11de4e28be4845de3ea392fd8d758655bf766ca7', 'value': '0xe35fa931a0000', 'stepLimit': '0xf4240', 'timestamp': '0x57771e1850109', 'signature': 'zekHL22qcFJA3HheIFeyRIaxQ/hqn3ZDeGNPmCN0GepDyzbKcejaDp9i5pJuam9ooxL47SV9Si1me4FmWHUeCQE=', 'txHash': '2248fa6e966f7d13ac091914a92453df017be1fa8552c115fa0ca574bd30cd81'}], 'block_hash': '7fde929247ff78639560b633172b730cb63be91cfd10acc59aca777ba0c7f774', 'height': 67720, 'peer_id': 'hxe5eae2613e8b6c19302335676c3c04866e7c6298', 'signature': '/22IPWX7EdmT8DDTeTg+ATufqReCjKnfJLFsqo42W+wi3M3DAYDxQjO6goXFcM2GkytlLRDOZpiO4u2Q5k1G8QE=', 'commit_state': {'icon_dex': '48e288616311a7a8de8e3fc23e573c4f364a086fffbfabe48ab7d15c001510ee'}}
```

## block
Print the block indicated by block height.

```bash
(venv) $ icondbtools block --help
usage: icondbtools block [-h] --db DB --height HEIGHT

optional arguments:
  -h, --help       show this help message and exit
  --db DB
  --height HEIGHT  start height to sync

(venv) $ icondbtools block --db ./db_13.125.135.114:7100_icon_dex --height 2
{'version': '0.1a', 'prev_block_hash': 'd5629fe006104df557570ce2613c8df1901d8f6f322b9f251645c201fa1d1e9e', 'merkle_tree_root_hash': '935e69a1937292e8de171e3c796c555e23d16e680ede6086a7583937d7ca703e', 'time_stamp': 1519289605629115, 'confirmed_transaction_list': [{'from': 'hx5a05b58a25a1e5ea0f1d5715e1f655dffc1fb30a', 'to': 'hxdbc9f726ad776d9a43d5bad387eff01325178fa3', 'value': '0x845951614014880000000', 'fee': '0x2386f26fc10000', 'timestamp': '1519289605344996', 'tx_hash': '935e69a1937292e8de171e3c796c555e23d16e680ede6086a7583937d7ca703e', 'signature': 'kF5b/l709ikHJwbGH8MvlwsWNjGbtmzZu4agizhVAGYQaIwInuBxw36P4jvFGY0DzmOVQ5SwB02zAn1/G8g1OQA=', 'method': 'icx_sendTransaction'}], 'block_hash': '8304cc79c8788cea92d3f25d1ce1e59ad66f8b6b03465d23128e6c8229467ee0', 'height': 2, 'peer_id': 'hx1fe2dfae9a5439bb1d4e193a3b7c6e5df6c6650e', 'signature': '0lUIA1mbiCDUyTcK6L0WfYWXMiD6TDCsCK01LWWOSvgqFp7rD+tgVBm0kbfp8DvpJNZPDV+dkNqj5EcYid0sHgA=', 'commit_state': {'icon_dex': '7b230ee5138e8b5a5faed4b5f59c032c8ad23b00991f263a05a3f41409de9237'}}
```

## clear

Remove .score/ and .statedb/ in a working directory.

```bash
(venv) $ icondbtools clear --help
usage: icondbtools clear [-h]

optional arguments:
  -h, --help  show this help message and exit

(venv) $ icondbtools clear
```

## txresult
Extract the transaction result indicated by transaction hash from block db and print it.

```bash
(venv) $ icondbtools txresult --help
usage: icondbtools txresult [-h] --db DB --hash TX_HASH

optional arguments:
  -h, --help      show this help message and exit
  --db DB
  --hash TX_HASH  tx hash without "0x" prefix

(venv) $ icondbtools txresult --db ../db_data/testnet/db --hash 7c1358eeaaa354d3ffa00f734d69038a4d3989a7d623857165244ab19cbe0ebd
{'block_hash': '8b6b7f6a208052d82c9f9f66050b22d24af2ecd511a0d2a49135b7f94e25e7b8', 'block_height': 32304, 'tx_index': '0x0', 'transaction': {'data': {'method': 'airdrop', 'params': {'amount': '0xde0b6b3a7640000', 'accounts': 'hxda034f6d8baae7ffb85ac827d91bbf0678719361'}}, 'stepLimit': '0x87000000', 'signature': 't1ZkT7ug4sDwimQ6eFlZ73DSVPvsfOFUcNkZYrNTQjYabT4f7+vpVgOIUxQ1co4fIZ56ixbgw3iV8QORh6n1CAE=', 'dataType': 'call', 'nid': '0x2', 'from': 'hx53dffc3b22a79845208f7f5fbd47f2e357162937', 'to': 'cx9de0c8e7266406df184b07f1c886c2eac804abef', 'version': '0x3', 'timestamp': '0x57771a5bf3e28'}, 'result': {'txHash': '7c1358eeaaa354d3ffa00f734d69038a4d3989a7d623857165244ab19cbe0ebd', 'blockHeight': '0x7e30', 'blockHash': '8b6b7f6a208052d82c9f9f66050b22d24af2ecd511a0d2a49135b7f94e25e7b8', 'txIndex': '0x0', 'to': 'cx9de0c8e7266406df184b07f1c886c2eac804abef', 'stepUsed': '0x32cd0', 'stepPrice': '0x2540be400', 'cumulativeStepUsed': '0x32cd0', 'eventLogs': [{'scoreAddress': 'cx4fd2ddde487072f4465b23fa40660db2676f5d94', 'indexed': ['Transfer(Address,Address,int,bytes)', 'cx9de0c8e7266406df184b07f1c886c2eac804abef', 'hxda034f6d8baae7ffb85ac827d91bbf0678719361', '0xde0b6b3a7640000'], 'data': ['0x61697264726f70706564']}, {'scoreAddress': 'cx9de0c8e7266406df184b07f1c886c2eac804abef', 'indexed': ['EventAirdropped(Address,int,int)', 'hxda034f6d8baae7ffb85ac827d91bbf0678719361'], 'data': ['0xde0b6b3a7640000', '0x2']}], 'logsBloom': '0x000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002300000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002a0000000000000000000000000000000000000000000000000000000000000081000000000000000000000000000000000000000000000000000000000000008600000000000000000000000000000000000000000000000000020000000000180000000000000000000000000000000000000000000000000000000000000208000000000000', 'status': '0x1'}}
```