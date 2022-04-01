# Crypto-Exp3
About Using exp3 and its variations of it to select coins to invest in.
1. [General](#General)
    - [Background](#background)
3. [Program Structure](#Program-Structure)
4. [Installation](#Installation)
5. [Footnote](#footnote)
## General
The goal is to use exp3 and variations of it in order to select the the coins will gain to most rewards and the least regret over a cretian timeframe.
### Background
Exp3 is a simple algorithm used for adversarial bandits.Adversarial bandits stands for a "game" which the player have to choose one action which its reward is sampled from a certian distirbution. Our particular implention is in the context of cryptocurrencies historical prices. The goal is to choose to most lucrative coin.

## Program Structure
The first part is specific functions for the dataset.The second part is the implementaions of the algorithms:
* Basis - The implementaion with constant learning rate
* Expansion 1 - Implementaion with decarsing learning rate
* Expansion 2 - Uses some confidence parameter δ to create a lower bound on the regret in each round and deletes every action that its regret may be higher than the created lower bound
