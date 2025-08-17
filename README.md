# Coin24Dive 🚀

**Mission:** Discover crashed shitcoins with comeback potential.  

Coin24Dive automates the process of scanning, filtering, analyzing, and reporting coins that have sharply dropped in value, allowing traders and analysts to identify potential opportunities quickly.

---

## Workflow Overview

Each stage of Coin24Dive is optimized to:

- Maximize speed  
- Minimize unnecessary API calls  
- Store results for easy web-serving  
- Enable advanced analytics downstream  

---

### 1. Daily Market Scanning

**Objective:** Collect global market data from [CoinGecko API](https://api.coingecko.com/api/v3/coins/markets).  

- **Scope:** ~17,000 coins  
- **Function:** `getter.get_coins_markets_all()`  
- **Output:**  
  - Dictionary: `all_coingecko_coins`  
  - File: `data/marketdata/coins{date}.json`  

> This provides a complete snapshot of the crypto market for daily analysis.

---

### 2. Filtering Coins by Price Crash

**Objective:** Identify coins that dropped ≥75% in the last 24 hours.  

- **Function:** `diver.diver`  
- **Output:**  
  - Dictionary: `top_divers`  
  - File: `dives{date}.json`  

> Only the most drastic “divers” are kept for deeper analysis.

---

### 3. Fetching Detailed Coin Data

**Objective:** Retrieve comprehensive coin and exchange information for top divers.  

- **API:** `https://api.coingecko.com/api/v3/coins/{id}`  
- **Function:** `getter.get_coindata()`  
- **Output:**  
  - Full coin data: `coindata`  
  - Exchange info only: `ex_inf`  
  - Files per coin:  
    - `data/coindata/{symbol}.json`  
    - `data/exchangedata/{symbol}.json`  

> Each coin’s details are saved individually to allow efficient querying and historical tracking.

---

### 4. LLM-Powered Analysis

**Objective:** Leverage LLMs to analyze top divers for revival potential.  

- **Implementation:** See `llm/` folder  
- **Method:** A “superprompt” guides the LLM to evaluate key metrics. Currently uses **OpenRouter** with structured JSON outputs.  
- **Output:** JSON matching schema: `llm/schemas/analytics_schema.json`  
  - Fields include `symbol`, `dead_score` (0–10), and `analysis_text`  

> This stage brings AI insights into potential recovery likelihood.

---

### 5. Display & Notification

**Objective:** Present filtered results and notify stakeholders.  

- **Implementation:** `main.py` + `notifications.py`  
- **Functionality:**  
  - Print top divers in a formatted table  
  - Send push notifications via Pushover for coins below a specified `dead_score` threshold

sample output:


```
TASK: [DISPLAY RESULTS] ********************************************************************************************************************
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                   ┃ Symbol     ┃ Dead Score ┃ 24h Change ┃ Exchanges                                                                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ mai-kava             │ mimatic    │        9.1 │       -96% │ Équilibre                                                                  │
│ nest                 │ nest       │        8.7 │       -89% │ Uniswap V4 (Ethereum), CoinW, LATOKEN, PancakeSwap (v2)                    │
│ mogul-productions    │ stars      │         10 │       -83% │ Uniswap V2 (Ethereum), LATOKEN, ApeSwap                                    │
│ stfx                 │ stfx       │        8.5 │       -87% │ MEXC, Uniswap V3 (Ethereum), Uniswap V4 (Ethereum), CoinEx, Raydium (CLMM) │
│ tokabu               │ tokabu     │        4.8 │       -78% │ Uniswap V2 (Ethereum)                                                      │
```


### Tech Highlights

- **API Efficiency:** Reduces repeated calls by storing intermediate data  
- **Structured Analysis:** LLM outputs standardized JSON for downstream usage  
- **Extensible:** Designed for future analytics, web dashboards, or alert systems

### Next Steps / TODOs

- Add historical trend tracking per coin  
- Integrate additional LLM models for diversified analysis  
- Build a lightweight web dashboard to visualize top divers

> ⚠️ **Disclaimer:** Coin24Dive is for informational purposes only. Crypto trading is highly speculative. Always do your own research.
