import json
import pathlib

from src.strategy.simple import copy_transactions


def execute_strategy(mode, address_list, last_transactions_dict):
    if mode == "simple":
        copy_transactions(address_list, last_transactions_dict)


if __name__ == '__main__':
    addresses_list = json.loads((pathlib.Path(__file__).parent / "resources" / "addresses_list.json")
                                .read_text(encoding="UTF-8"))['addresses']
    last_transactions_dict = json.loads((pathlib.Path(__file__).parent / "resources" / "last_transactions.json")
                                        .read_text(encoding="UTF-8"))
    execute_strategy("simple", addresses_list, last_transactions_dict)
    print("")
