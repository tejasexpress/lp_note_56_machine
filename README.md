
# DATA NEEded

### To find pools
- market cap of each token
- 3 day average 24hr volume
- should exist before last 3 months 
- >2 DEX pools for token pair

### Token information

- CMC API for token info - https://coinmarketcap.com/api/documentation/v1/
- RSI of token 
- volume and TVL of token

---
#### **General Information**

| Field         | Type       | Description                                                                                   |
| ------------- | ---------- | --------------------------------------------------------------------------------------------- |
| **`address`** | **String** | **The unique identifier for the liquidity pool, usually a blockchain public key or address.** |
| **`name`**    | **String** | **The name of the trading pair, formatted as `TOKEN1-TOKEN2`.**                               |
| **`mint_x`**  | **String** | **The token address for the first token in the pair (`x`).**                                  |
| **`mint_y`**  | **String** | **The token address for the second token in the pair (`y`).**                                 |
| **`reserve_x`**   | **String**     | **The blockchain address holding reserves for token `x`.**                                        |
| **`reserve_y`**   | **String**     | **The blockchain address holding reserves for token `y`.**                                        |

---

#### **Reserves**

| Field              | Type   | Description                                          |
| ------------------ | ------ | ---------------------------------------------------- |
| `reserve_x_amount` | Number | The total amount of token `x` in the liquidity pool. |
| `reserve_y_amount` | Number | The total amount of token `y` in the liquidity pool. |

---

#### **Trading and Fees**

| Field                     | Type   | Description                                                                                  |
| ------------------------- | ------ | -------------------------------------------------------------------------------------------- |
| `bin_step`                | Number | Defines the price increment between bins in the liquidity pool.                              |
| `base_fee_percentage`     | String | The base percentage fee charged on each trade.                                               |
| `max_fee_percentage`      | String | The maximum fee percentage that can be charged per trade.                                    |
| `protocol_fee_percentage` | String | The percentage of trading fees allocated to the protocol, as opposed to liquidity providers. |

---

#### **Liquidity and Performance**

| Field                     | Type   | Description                                                              |
| ------------------------- | ------ | ------------------------------------------------------------------------ |
| `liquidity`               | Number | The total liquidity in the pool, calculated from the reserves and price. |
| `fees_24h`                | Number | Total fees collected in the past 24 hours.                               |
| `today_fees`              | Number | Fees generated so far for the current day.                               |
| `trade_volume_24h`        | Number | The trading volume over the past 24 hours.                               |
| `cumulative_trade_volume` | String | The total trading volume since the pool was created.                     |
| `cumulative_fee_volume`   | String | The total fees collected since the pool's inception.                     |

---

#### **Price and Yield**

| Field           | Type   | Description                                                                      |
| --------------- | ------ | -------------------------------------------------------------------------------- |
| **`current_price`** | **Number** | **The current price of token `x` in terms of token `y`.**                            |
| `apr`           | Number | The annual percentage rate (APR) for liquidity providers, based on trading fees. |
| `apy`           | Number | The annual percentage yield (APY), factoring in compounding returns.             |

---

#### **Farming Rewards**

| Field           | Type   | Description                                                                             |
| --------------- | ------ | --------------------------------------------------------------------------------------- |
| `farm_apr`      | Number | The annual percentage rate (APR) from farming rewards, if applicable.                   |
| `farm_apy`      | Number | The annual percentage yield (APY) from farming rewards, if applicable.                  |
| `reward_mint_x` | String | The address of the reward token for `x`. "11111111111111111111111111111111" means none. |
| `reward_mint_y` | String | The address of the reward token for `y`. "11111111111111111111111111111111" means none. |

---

#### **Visibility**

| Field  | Type    | Description                                                                   |
| ------ | ------- | ----------------------------------------------------------------------------- |
| `hide` | Boolean | Indicates whether the liquidity pool is hidden (`true`) or visible (`false`). |


---

### For risk monitoring

- price of both coins when bid made
- starting amount of tokens invested
- current price of tokens invested
- fees earned
- health score - https://de.fi/scanner
- https://docs.google.com/spreadsheets/d/1RIlAb-eilVWUVzruDUWR7Sidt8LI-GB1VIBhiKC_ccI/edit?gid=1434356868#gid=1434356868
- somehow find IL
- volume when started volume right now (of pool)
- current balance initial balance

---

## Creating position and trading

https://www.npmjs.com/package/@meteora-ag/dlmm

https://github.com/MeteoraAg/cpi-examples


---

#### Input

- [ ] Get pool data 
- [ ] identify pools which are profitable
	- [ ] https://x.com/Tuuxxdotsol/status/1875919815170547728
	- [ ] get token information
- [ ] identify if we should put money

#### Current position

- [ ] get current positions 
- [ ] check for risk parameters
	- [ ] exit at stop loss
	- [ ] calc IL, exit if 1.5%
	- [ ] exit if 24hr vol drops by more than 40%
	- [ ] rebalance at 7% range deviation

#### Put positions

- [ ] position structure
