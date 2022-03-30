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
T = 2991
#every_day_best_rewards = [0]*T
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
        reward = payoff(chosen_coin, start_date, t)
        reward_sum[chosen_coin] += reward / rho[chosen_coin]
        rewards.append(reward)
        existing_coins = get_existing_coins(start_date, t)
    return sum(rewards)


def exp3_extension2(start_date, days, conf_param):
    epsilon = [1 / K]
    reward_sum = defaultdict(int)
    epsilon[0] = 1 / K
    rho = dict()
    rewards = []
    to_remove = set()  #every coin that once was removed
    A = get_existing_coins(start_date, 1)
    B = 4*(math.exp(1)-2)*(2*math.log(K)+math.log(2/conf_param))
    V = defaultdict(lambda: 0)  #1/K
    for t in range(1, days):
        epsilon.append(min([epsilon[0], math.sqrt(np.log(len(A)) / (len(A) * t))]))
        for coin in A:
            rho[coin] = (1-len(A)*epsilon[t])
            rho[coin] *= math.exp(epsilon[t-1]*reward_sum[coin]) / sum(math.exp(epsilon[t-1]*reward_sum[c]) for c in A)
            rho[coin] += epsilon[t]
            V[coin] += 1/rho[coin]
        coins_values = [(coin, rho[coin]) for coin in A]
        chosen_coin = choose_coin(coins_values)
        reward = payoff(chosen_coin, start_date, t) * rho[chosen_coin]
        reward_sum[chosen_coin] += reward / rho[chosen_coin]
        rewards.append(reward)
        best_coin = max(reward_sum, key=reward_sum.get)
        for c in A:
            if reward_sum[best_coin] - reward_sum[c] > math.sqrt(B*(V[best_coin] + V[c])):
                to_remove.add(c)
                reward_sum.pop(c)
                rho.pop(c)
        if len(A) < K:
            A = get_existing_coins(start_date, t+1)  # adding new coins if we need
        A = list(set(A) - set(to_remove))  #making sure that none of the coins that were removed remain in A
    return sum(rewards)

def get_best_coin_sum(start_date, days):
    best_sum = -float("inf")
    best_coin = list(crypto_datasets.keys())[0]
    for coin in crypto_datasets.keys():
        reward_sum = 0
        for t in range(days):
            reward_sum += payoff(coin, start_date, t)
        if reward_sum >= best_sum:
            best_coin = coin
            best_sum = reward_sum

    return best_coin, best_sum


def main():
    start_date = datetime.datetime.strptime("2015-01-01", "%Y-%m-%d")
    amount_days = range(600, 2000, 50)
    #rewards_extended = [exp3_extension1(start_date, i) for i in amount_days]
    best_coin_rewards = [get_best_coin_sum(start_date, i) for i in amount_days]
    best_coin = best_coin_rewards[-1][0]
    best_rewards = [r[1] for r in best_coin_rewards]
    #regrets_extended = [best_rewards[i] - rewards_extended[i] for i in amount_days]
    x = range(600, 2000, 50)
    """plt.title('Regret As a Function of Number of Days')
    plt.plot(x, regrets_extended, color="r", label="extended")
    plt.xlabel('Number Of Days')
    plt.ylabel('Regret')
    plt.show()"""



    params = [0.1, 0.3, 0.5, 0.7]
    for conf_param in params:
        rewards_extension2 = [exp3_extension2(start_date, i, conf_param) for i in amount_days]
        regrets_extended = [best_rewards[i] - rewards_extension2[i] for i in amount_days]
        plt.title(f'Regret As a Function of Number of Days, with conf_param: {conf_param}')
        plt.plot(x, regrets_extended, color="r", label="extended")
        plt.xlabel('Number Of Days')
        plt.ylabel('Regret')
        plt.show()


if __name__ == '__main__':
    start_date = datetime.datetime.strptime("2015-01-01", "%Y-%m-%d")
    create_crypto_dict()
    every_day_best_rewards = [get_best_coin_sum(start_date, i) for i in range(T)]
    main()
