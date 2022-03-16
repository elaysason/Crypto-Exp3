import datetime
from operator import itemgetter
import pandas as pd
import numpy as np

coins_list = ["Aave", "BinanceCoin", "Bitcoin", "Cardano", "ChainLink", "Cosmos", "CryptocomCoin", "Dogecoin", "EOS",
              "Ethereum", "Iota", "Litecoin", "Monero", "NEM", "Polkadot", "Solana", "Stellar", "Tether",
              "Tron", "Uniswap", "USDCoin", "WrappedBitcoin", "XRP"]
K = 23
epsilon = [1 / K]
t = 0
T = 2991
start_date = datetime.datetime.strptime("2013-04-29", "%Y-%m-%d")
end_date = datetime.datetime.strptime("2021-07-06", "%Y-%m-%d")
crypto_datasets = dict()
reward_sum = dict()


def create_crypto_dict():
    for c in coins_list:
        file = "coin_" + c + ".csv"
        crypto = pd.read_csv(file)
        crypto['Date'] = pd.to_datetime(crypto['Date']).dt.date
        crypto_datasets[c] = crypto
        reward_sum[c] = 0


def get_date(days):
    return start_date + datetime.timedelta(days=days)


def get_existing_coins(days):
    existing = []
    for key in crypto_datasets.keys():
        if min(crypto_datasets[key]["Date"]) <= get_date(days).date():
            existing.append(key)
    return existing


def choose_coin(coin_value_list):
    coins = [tup[0] for tup in coin_value_list]
    probs = [tup[1] for tup in coin_value_list]
    return np.random.choice(a=coins, p=probs)


if __name__ == '__main__':
    create_crypto_dict()
    coins_election = []
    existing_coins = get_existing_coins(1)
    epsilon[0] = 1 / (len(get_existing_coins(0)))
    rho = dict()
    for t in range(1, T + 1):
        epsilon.append(min([epsilon[0], np.sqrt(np.log(len(existing_coins)) / (len(existing_coins) * t))]))
        for coin in existing_coins:
            rho[coin] = (1 - len(existing_coins) * epsilon[t])
            val = np.exp(epsilon[t - 1] * reward_sum[coin]) / \
                sum(np.exp(epsilon[t - 1] * reward_sum[c]) for c in existing_coins)
            rho[coin] *= val
            rho[coin] += epsilon[t]
        coins_values = [(coin, rho[coin]) for coin in existing_coins]
        chosen_coin = choose_coin(coins_values)
        reward = float(
            crypto_datasets[chosen_coin].loc[crypto_datasets[chosen_coin]["Date"] == get_date(t - 1).date()]["Close"] -
            crypto_datasets[chosen_coin].loc[crypto_datasets[chosen_coin]["Date"] == get_date(t - 1).date()]["Open"])
        reward_sum[chosen_coin] += reward / rho[chosen_coin]
        coins_election.append(chosen_coin)
        existing_coins = get_existing_coins(t)

# TODO: calculate regret and plot it
