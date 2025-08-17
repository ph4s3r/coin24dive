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


### Dispaly Results & send out notifications

what  : compiling a list top diver coins, filtering by dead score  
how   : see main.py & implementation of message sending: notifications.py  
output: prints a table to stdout & send a message on pushover about the coins with a certain max dead score  

sample output:


```
TASK: [DISPLAY RESULTS] **********************************************************************************************************************************************************************************************************************
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                   ┃ Symbol     ┃ Dead Score ┃ 24h Change ┃ Exchanges                                                                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ mai-kava             │ mimatic    │        9.1 │       -96% │ Équilibre                                                                  │
│ nest                 │ nest       │        8.7 │       -89% │ Uniswap V4 (Ethereum), CoinW, LATOKEN, PancakeSwap (v2)                    │
│ mogul-productions    │ stars      │         10 │       -83% │ Uniswap V2 (Ethereum), LATOKEN, ApeSwap                                    │
│ stfx                 │ stfx       │        8.5 │       -87% │ MEXC, Uniswap V3 (Ethereum), Uniswap V4 (Ethereum), CoinEx, Raydium (CLMM) │
│ tokabu               │ tokabu     │        4.8 │       -78% │ Uniswap V2 (Ethereum)                                                      │
```



