import json
import pathlib
import time

from src.model.defi import Strategy

if __name__ == "__main__":
    smart_money_wallets = json.loads(
        (pathlib.Path(__file__).parent / "resources" / "addresses_list.json").read_text(
            encoding="UTF-8"
        )
    )["addresses"]
    last_transactions_dict = json.loads(
        (
            pathlib.Path(__file__).parent / "resources" / "last_transactions.json"
        ).read_text(encoding="UTF-8")
    )

    strategy = Strategy()
    print("running")
    while True:
        strategy.execute(
            Strategy.SIMPLE,
            **{
                "smart_money_wallets": smart_money_wallets,
                "last_transactions_dict": last_transactions_dict,
            }
        )
        time.sleep(120)
