# Predbot 🤖📈

A Binance Futures Trading Analysis Bot that identifies high-potential trade opportunities and sends notifications to Telegram.

## Features

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

- **10 Chart Patterns**:
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
- **Telegram Notifications**: Sends detailed trade alerts with signal strength, timeframe analysis, and detected patterns

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
    for signal in results:
        print(f"{signal['symbol']}: {signal['recommendation']} ({signal['signal_strength']}%)")

asyncio.run(single_scan())
```

## Sample Telegram Alert

```
🟢 TRADE ALERT: BTCUSDT 🟢

📊 Signal: LONG
💪 Strength: 78.5%
💰 Price: $42,500.00
⏰ Time: 2024-01-15 14:30:00 UTC

📈 Timeframe Analysis:
  🟢 5m: BULLISH (72%)
  🟢 15m: BULLISH (75%)
  🟢 1h: BULLISH (80%)
  🟢 4h: BULLISH (82%)

🔧 Key Indicators:
  🟢 RSI: BUY
  🟢 MACD: BUY
  🟢 EMA: BUY
  ⚪ BOLLINGER: NEUTRAL
  🟢 STOCHASTIC: BUY

📐 Patterns Detected:
  🟢 double_bottom: 85% confidence
  🟢 ascending_triangle: 70% confidence

⚠️ This is not financial advice. Always do your own research.
```

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

4. **Pattern Detection**: All 10 chart patterns are checked for each timeframe.

5. **Trend Analysis**: Signals are aggregated with timeframe-weighted scoring to determine overall trend direction and strength.

6. **Signal Generation**: If trend alignment exceeds the threshold (default: 70%) and signal strength is above the minimum (default: 60%), a strong signal is generated.

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