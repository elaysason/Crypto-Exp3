import datetime
import random
from operator import itemgetter
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

coins_list = ["Aave", "BinanceCoin", "Bitcoin", "Cardano", "ChainLink", "Cosmos", "CryptocomCoin", "Dogecoin", "EOS",
              "Ethereum", "Iota", "Litecoin", "Monero", "NEM", "Polkadot", "Solana", "Stellar", "Tether",
              "Tron", "Uniswap", "USDCoin", "WrappedBitcoin", "XRP"]
K = 23
epsilon = [1 / K]
t = 0
T = 2991
end_date = datetime.datetime.strptime("2021-07-06", "%Y-%m-%d")
crypto_datasets = dict()
reward_sum = dict()


def payoff(coin, start_date, t, amountToInvest=1.0):
    date = get_date(start_date, t).date()
    on_date = crypto_datasets[coin].loc[crypto_datasets[coin]["Date"] == date]
    if len(on_date) == 0:
        before_date = crypto_datasets[coin].loc[crypto_datasets[coin]["Date"] < date].sort_values(by=["Date"],ascending=False)
        open = before_date['Open'].head(20).mean()
        close = before_date['Close'].head(20).mean()
        return amountToInvest*close/open - amountToInvest

    sharesBought = amountToInvest / pd.to_numeric(on_date['Open'])
    amountAfterSale = list(pd.to_numeric(sharesBought) * pd.to_numeric(on_date['Close']))[0]

    return amountAfterSale - amountToInvest


def create_crypto_dict():
    for c in coins_list:
        file = "coin_" + c + ".csv"
        crypto = pd.read_csv(file)
        crypto['Date'] = pd.to_datetime(crypto['Date']).dt.date
        crypto_datasets[c] = crypto
        reward_sum[c] = 0


def get_date(start_date, days):
    return start_date + datetime.timedelta(days=days)


def get_existing_coins(start_date, days):
    existing = []
    for i, key in enumerate(crypto_datasets.keys()):
        if min(crypto_datasets[key]["Date"]) <= get_date(start_date, days).date():
            existing.append(i)
    return existing


def choose_coin(coin_value_list):
    coins = [tup[0] for tup in coin_value_list]
    probs = [float(tup[1]) for tup in coin_value_list]
    return random.choices(coins, weights=probs)[0]


## choice = random.uniform(0, sum(probs))
## choiceIndex = 0

## for weight in probs:
##     choice -= weight
##     if choice <= 0:
##         return choiceIndex
##     choiceIndex += 1

def exp3_extintion(confidence_parameter, date, days):
    epsilon = [0]


def exp3_base(date, days):
    eta = np.sqrt(np.log(K) / T * K)
    start_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    existing_coins = get_existing_coins(start_date, 0)
    coins_election = []
    scores = [0] * K
    reward = lambda choice, t: payoff(coins_list[choice], start_date, t)
    best_sum = 0
    reward_sum = 0
    for t in range(1, days):
        cur_distribution = []
        for i in range(K):
            if i in existing_coins:
                cur_distribution.append(
                    np.exp(eta * scores[i]) / np.sum([np.exp(scores[j] * eta) for j in existing_coins]))
            else:
                cur_distribution.append(0)
        coins_values = [(coin, cur_distribution[coin]) for coin in existing_coins]
        chosen_coin = choose_coin(coins_values)
        cur_reward = payoff(coins_list[chosen_coin], start_date, t=t - 1)
        for i in range(K):
            if i in existing_coins:
                scores[i] = scores[i] + 1
                if chosen_coin == i:
                    scores[i] -= (1 - cur_reward) / cur_distribution[i]
        reward_sum += cur_reward
        coins_election.append(chosen_coin)
        best_sum += max([reward(s, t) for s in existing_coins])
        existing_coins = get_existing_coins(start_date, t)

    return best_sum - reward_sum


if __name__ == '__main__':
    create_crypto_dict()

    ## days = range(100, 1000, 50)

    ## regrets = [exp3_base("2018-01-01", t) for t in days]
    ## print(regrets)
    ## x = range(100, 1000, 50)
    ## plt.title('Regret As a Function of Number of Days')
    ## plt.plot(x, regrets)
    ## plt.xlabel('Number Of Days')
    ## plt.ylabel('Regret')
    ## plt.show()

    days = range(100, 2300, 150)

    regrets = [exp3_base("2015-01-01", t) for t in days]
    print(regrets)
    x = range(100, 2300, 150)
    plt.title('Regret As a Function of Number of Days')
    plt.plot(x, regrets)
    plt.xlabel('Number Of Days')
    plt.ylabel('Regret')
    plt.show()
