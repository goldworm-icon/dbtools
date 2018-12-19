# ChangeLog
Change logs of icondbtools

## 0.0.3 - 2018.12.19

* Add 'tps' command
    * Calculate tps based on confirmed transactions that a specific range of blocks contain.
    * tps = tx_count / (end block.timestamp - start block.timestamp)

## 0.0.2 - 2018.11.02

* Improve sync command
    * If --start option is not defined, icondbtools try to use the next height of the
    last block on .statedb/icon_dex as a start height.
    * Add flag options. (--no-fee, --no-audit, --deployer-whitelist, --score-package-validator)
* Add new commands. (statelastblock, account)

## 0.0.1

* Implement basic features
    * sync, lastblock, block, txresult, clear, statehash