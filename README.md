# Coin24Dive

Searching for crashed shitcoins that can come back 

## Process

each of the below stages are saving the compiled information to files, to 

- make it as fast as possible
- make sure not to burn API calls unnecessary
- to be able to serve the data on a webserver easily
- to be able to do more analytics later on


### Daily market scanning

what:   getting market data from https://api.coingecko.com/api/v3/coins/markets ; this is approximately 17 thousand coins' data
how:    implemented in function: getter.get_coins_markets_all()
output: saved to dict coins and written into a one single file "data/marketdata/coins{date}.json"


### Searching for coins with specific criteria

what:   filtering the above market data for coins that dropped at least 75% in price in the last 24 hours. 
how:    implemented in function: diver.diver
output: top_divers variable in main and written into a one single file dives{date}.json


### Getting detailed coin data for each coin

what:   for all the top_diver coins, getting data from https://api.coingecko.com/api/v3/coins/{id} 
how:    implemented in function: getter.get_coindata()
output: coindata, ex_inf variables for the full data, and exchange info only 
        and written into one file per coin into data\coindata\symbol.json and data\exchangedata\symbol.json respectively


### Analyzing the top divers with LLM

what:   all the detailed coindata of the 'top divers' is being sent into LLM(s) for analysis
how:    see implementation in the llm folder. there is a superpromt telling the LLM what metrics to look for.
        currently OpenRouter is used with structured outputs so we can get a json back 
output: json structured output back-validated with the requested schema (llm\schemas\analytics_schema.json) 
        with the symbol, a dead_score from 0 to 10 and the analysis text


### Results

what  : compiling a list top diver coins, filtering by dead score
how   : see main.py & implementation of message sending: notifications.py
output: prints a table to stdout & send a message on pushover about the coins with a certain max dead score

sample output:


```
TASK: [RESULTS] **********************************************************************************************************************************************************************************************
        id                    | symbol | dead_score | chg_%_24h | exchanges-traded-on
fsn                              fsn            9         -79% Uniswap V3 (Ethereum), Nonkyc.io
beware-of-geeks-bearing-grifts   bogbg        8.6         -85% Uniswap V2 (Ethereum)
staked-bitz                      sbitz        7.8         -93% Invariant (Eclipse)
maneki-neko-2                    neko           8         -93% Uniswap V2 (Base)
nend                             nend         9.2         -75% BingX
cyberyen                         cy           9.2         -87% Komodo Wallet, Bitcointry
x-world-games                    xwg          9.1         -88% Uniswap V2 (Ethereum), LATOKEN, PancakeSwap (v2)
qmall                            qmall        8.8         -77% Uniswap V2 (Ethereum), PancakeSwap (v2), QMall
prodigi-connect                  pdg          9.4         -84% BingX
kira-ai                          kira         8.5         -86% Uniswap V2 (Ethereum)
build                            build        9.6         -93% RadioShack (Ethereum), PancakeSwap (v2)
coreto                           cor          9.1         -79% Uniswap V2 (Ethereum), ProBit Global
frapped-usdt                     fusdt        9.8         -96% Equalizer, Curve (Fantom), Sushiswap (Fantom), SpiritSwap, Beethoven X, SpiritSwap (V2)
```



