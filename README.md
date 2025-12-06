# Predbot 🤖📈

A Binance Futures Scalping Bot with **20x Cross Leverage** that identifies high-probability trade opportunities with DCA (Dollar Cost Averaging) entry levels and multiple take profit levels, and sends detailed notifications to Telegram.

## Features

- **20x Cross Leverage**: Pre-configured for Binance Futures with 20x cross margin
- **DCA Scalping Trade Signals**: Generates complete trade setups with:
  - **4 DCA Entry Levels** for optimal average entry price
  - **4 Take Profit Levels** for scaling out (0.3%, 0.8%, 1.5%, 2.5%)
  - **Stop Loss** with ATR-based calculation
  - **Average Entry Price** calculation
  - **Trade Quality Score** (0-100)

- **Strict Trade Quality Validation**: Only sends trades that meet strict criteria (to avoid loss trades):
  - Minimum **1:2 Risk/Reward ratio**
  - At least **7/10 indicators** aligned
  - **70%+ timeframe** alignment
  - Minimum **1% profit potential**
  - Minimum trade score of **75**

- **Volatility Scanner**: Automatically identifies the top 20 most volatile coins on Binance Futures
- **Multi-Timeframe Analysis**: Analyzes coins across multiple timeframes (5m, 15m, 1h, 4h)
- **10 Technical Indicators**:
  1. RSI (Relative Strength Index)
  2. MACD (Moving Average Convergence Divergence)
  3. Bollinger Bands
  4. EMA (Exponential Moving Average)
  5. SMA (Simple Moving Average)
  6. Stochastic Oscillator
  7. ADX (Average Directional Index)
  8. CCI (Commodity Channel Index)
  9. Williams %R
  10. OBV (On Balance Volume)

- **10 Chart Patterns** (detected BEFORE breakout):
  1. Double Top
  2. Double Bottom
  3. Head and Shoulders
  4. Inverse Head and Shoulders
  5. Ascending Triangle
  6. Descending Triangle
  7. Symmetrical Triangle
  8. Rising Wedge
  9. Falling Wedge
  10. Bullish/Bearish Engulfing

- **Trend Direction Analysis**: Combines signals from indicators and patterns to determine overall trend
- **Telegram Notifications**: Sends detailed scalping trade alerts with all entry/exit levels

## ⚠️ Important Note

**This bot does NOT execute trades.** It only identifies potential trading opportunities and sends notifications. All trading decisions should be made by you after your own research and analysis.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Predbot.git
cd Predbot
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the bot:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

Edit the `.env` file with your settings:

```env
# Binance API (Read-only access recommended)
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Bot Settings
TOP_VOLATILE_COINS=20
TIMEFRAMES=5m,15m,1h,4h
SIGNAL_STRENGTH_THRESHOLD=60
```

### Getting Binance API Keys

1. Go to [Binance](https://www.binance.com)
2. Navigate to API Management
3. Create a new API key with **Read-Only** permissions
4. Copy the API Key and Secret to your `.env` file

### Setting up Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the bot token to your `.env` file
4. Get your chat ID:
   - Send a message to your bot
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

## Usage

### Run the Bot

```bash
python run.py
```

The bot will:
1. Connect to Binance Futures API
2. Scan for top 20 volatile coins every 5 minutes
3. Analyze each coin using indicators and patterns
4. Send Telegram alerts for strong signals

### Run a Single Scan

```python
import asyncio
from src.bot import Predbot

async def single_scan():
    bot = Predbot()
    results = await bot.run_single_scan()
    for trade in results:
        print(f"{trade['symbol']}: {trade['direction']} (Score: {trade['trade_score']})")

asyncio.run(single_scan())
```

## Sample Telegram Alert

```
🟢 SCALPING TRADE: BTCUSDT 🟢

📊 Direction: LONG
⚡ Leverage: 20x CROSSED
🏆 Trade Quality: ⭐⭐ HIGH PROBABILITY
💯 Score: 82/100
💰 Current Price: $42,500.0000
⏰ Time: 2024-01-15 14:30:00 UTC

📍 DCA ENTRY LEVELS (25% each):
  Entry 1 (25%): $42,457.5000
  Entry 2 (25%): $42,287.5000
  Entry 3 (25%): $42,075.0000
  Entry 4 (25%): $41,925.5000
  📊 Avg Entry: $42,186.3750

🎯 TAKE PROFIT LEVELS (Scale Out):
  TP1 (25%): $42,312.9300 (0.3%)
  TP2 (25%): $42,524.4900 (0.8%)
  TP3 (25%): $42,819.1000 (1.5%)
  TP4 (25%): $43,240.9000 (2.5%)

🛑 STOP LOSS: $41,764.2300 (-1%)

📈 TRADE METRICS:
  Risk: 1.00%
  Reward: 2.50%
  R:R Ratio: 1:2.5
  Indicators Aligned: 8/10

📊 KEY LEVELS:
  Support: $41,800.0000
  Resistance: $44,200.0000

📈 Timeframe Analysis:
  🟢 5m: BULLISH (78%)
  🟢 15m: BULLISH (82%)
  🟢 1h: BULLISH (85%)
  🟢 4h: BULLISH (88%)

🔧 Key Indicators:
  🟢 RSI: BUY
  🟢 MACD: BUY
  🟢 EMA: BUY
  🟢 STOCHASTIC: BUY
  🟢 ADX: BUY

💡 DCA EXECUTION STRATEGY:
• Set leverage to 20x CROSS margin
• Place 25% of position at each entry level
• Wait for price to reach each level before adding
• Average entry price improves with each DCA fill
• Take 25% profit at each TP level
• Move stop to breakeven after TP1 hits

⚠️ This is not financial advice. Always manage your risk.
```

## Scalping Trade Validation

The bot only sends trades that meet **strict quality criteria** to avoid loss trades:

| Criteria | Minimum Requirement |
|----------|-------------------|
| Risk/Reward Ratio | **1:2** |
| Profit Potential | **1%** |
| Indicator Alignment | **7/10 indicators** |
| Timeframe Alignment | **70%** |
| Trade Score | **75/100** |

### Trade Quality Scores

- **⭐⭐⭐ EXCELLENT (85-100)**: Very high probability setup
- **⭐⭐ HIGH PROBABILITY (75-84)**: Strong setup (minimum for alerts)
- **⭐ MODERATE (65-74)**: Not sent - below threshold

## Pattern Detection

The bot detects patterns **before breakout** to provide early entry opportunities:

- **FORMING**: Pattern is developing, watch for confirmation
- **READY**: Pattern complete, price approaching breakout level - optimal entry zone
- **CONFIRMED**: Breakout has occurred, can still enter on retest

## Project Structure

```
Predbot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main bot orchestrator
│   ├── config.py           # Configuration management
│   ├── binance_client.py   # Binance API integration
│   ├── indicators.py       # Technical indicators (10)
│   ├── patterns.py         # Chart patterns (10)
│   ├── trend_analyzer.py   # Multi-timeframe trend analysis
│   ├── scalping_analyzer.py # Scalping trade generator
│   └── telegram_notifier.py # Telegram notifications
├── tests/
│   └── ...                 # Unit tests
├── .env.example            # Environment template
├── .gitignore
├── requirements.txt
├── run.py                  # Entry point
└── README.md
```

## How It Works

1. **Volatility Scan**: The bot fetches 24h ticker data and identifies the top 20 most volatile USDT futures pairs with sufficient volume.

2. **Data Collection**: For each volatile coin, OHLCV data is fetched for configured timeframes (default: 5m, 15m, 1h, 4h).

3. **Technical Analysis**: All 10 indicators are calculated and generate signals (BUY/SELL/NEUTRAL).

4. **Pattern Detection**: All 10 chart patterns are checked BEFORE breakout for early entry opportunities.

5. **Trend Analysis**: Signals are aggregated with timeframe-weighted scoring to determine overall trend direction and strength.

6. **Scalping Trade Generation**: 
   - Calculate 4 entry levels for scaling in
   - Calculate 4 take profit levels for scaling out
   - Calculate stop loss based on ATR and support/resistance
   - Validate trade meets quality criteria

7. **Quality Validation**: Only trades meeting strict criteria are sent:
   - Risk/Reward >= 1:1.5
   - 6+ indicators aligned
   - 60%+ timeframe alignment
   - 0.5%+ profit potential

8. **Notification**: High-probability trades are sent to Telegram with complete setup details.

7. **Notification**: Strong signals are sent to Telegram with detailed analysis.

## Customization

### Adjusting Sensitivity

- **Higher sensitivity** (more signals): Lower `SIGNAL_STRENGTH_THRESHOLD` to 50
- **Lower sensitivity** (fewer, stronger signals): Raise `SIGNAL_STRENGTH_THRESHOLD` to 70+

### Adding Timeframes

Modify `TIMEFRAMES` in `.env`:
```env
TIMEFRAMES=1m,5m,15m,30m,1h,4h,1d
```

### Volume Filter

Adjust minimum 24h volume:
```env
MIN_VOLUME_USD=50000000  # $50M minimum volume
```

## Disclaimer

This software is for educational and informational purposes only. Cryptocurrency trading carries significant risk. The developers are not responsible for any financial losses incurred from using this bot. Always do your own research and never invest more than you can afford to lose.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.