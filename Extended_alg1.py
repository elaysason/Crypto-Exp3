import datetime
import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np
from collections import defaultdict

coins_list = ["Aave", "BinanceCoin", "Bitcoin", "Cardano", "ChainLink", "Cosmos", "CryptocomCoin", "Dogecoin", "EOS",
              "Ethereum", "Iota", "Litecoin", "Monero", "NEM", "Polkadot", "Solana", "Stellar", "Tether",
              "Tron", "Uniswap", "USDCoin", "WrappedBitcoin", "XRP"]
K = 23

end_date = datetime.datetime.strptime("2021-07-06", "%Y-%m-%d")
crypto_datasets = dict()


def create_crypto_dict():
    for c in coins_list:
        file = "coin_" + c + ".csv"
        crypto = pd.read_csv(file)
        crypto['Date'] = pd.to_datetime(crypto['Date']).dt.date
        crypto_datasets[c] = crypto



def get_date(start_date, days):
    return start_date + datetime.timedelta(days=days)


def get_existing_coins(start_date, days):
    existing = []
    for key in crypto_datasets.keys():
        if min(crypto_datasets[key]["Date"]) <= get_date(start_date, days).date():
            existing.append(key)
    return existing


def choose_coin(coin_value_list):
    coins = [tup[0] for tup in coin_value_list]
    probs = [tup[1] for tup in coin_value_list]
    return np.random.choice(a=coins, p=probs)

def payoff(coin, start_date, t, amountToInvest=1.0):
    date = get_date(start_date, t).date()
    on_date = crypto_datasets[coin].loc[crypto_datasets[coin]["Date"] == date]
    if len(on_date) == 0:
        before_date = crypto_datasets[coin].loc[crypto_datasets[coin]["Date"] < date].sort_values(by=["Date"],
                                                                                                  ascending=False)
        open = before_date['Open'].head(20).mean()
        close = before_date['Close'].head(20).mean()
        return amountToInvest * close / open - amountToInvest

    sharesBought = amountToInvest / pd.to_numeric(on_date['Open'])
    amountAfterSale = list(pd.to_numeric(sharesBought) * pd.to_numeric(on_date['Close']))[0]

    return amountAfterSale - amountToInvest


def exp3_extension1(start_date, days):
    epsilon = [1 / K]
    reward_sum = defaultdict(int)
    epsilon[0] = 1 / (len(get_existing_coins(start_date, 0)))
    rho = dict()
    rewards = []
    best_rewards = []
    existing_coins = get_existing_coins(start_date, 0)
    for t in range(1, days):
        epsilon.append(min([epsilon[0], math.sqrt(np.log(len(existing_coins)) / (len(existing_coins) * t))]))
        for coin in existing_coins:
            rho[coin] = (1 - len(existing_coins) * epsilon[t])
            val = math.exp(epsilon[t - 1] * reward_sum[coin]) / \
                sum([math.exp(epsilon[t - 1] * reward_sum[c]) for c in existing_coins])
            rho[coin] *= val
            rho[coin] += epsilon[t]
        coins_values = [(coin, rho[coin]) for coin in existing_coins]
        chosen_coin = choose_coin(coins_values)
        reward = payoff(chosen_coin, start_date, t)  # pd.to_numeric(on_date["Close"].values - on_date["Open"].values)
        reward_sum[chosen_coin] += reward / rho[chosen_coin]
        rewards.append(reward)
        best_rewards.append(max(payoff(coin, start_date, t) for coin in existing_coins))
        existing_coins = get_existing_coins(start_date, t)
    return sum(best_rewards) - sum(rewards)

def main():
    create_crypto_dict()
    amount_days = range(100, 2000, 50)
    start_date = datetime.datetime.strptime("2013-04-29", "%Y-%m-%d")
    regrets = [exp3_extension1(start_date, i) for i in amount_days]
    print(regrets)
    x = range(100, 2000, 50)
    plt.title('Regret As a Function of Number of Days')
    plt.plot(x, regrets)
    plt.xlabel('Number Of Days')
    plt.ylabel('Regret')
    plt.show()


if __name__ == '__main__':
    main()
