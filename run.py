#!/usr/bin/env python3
"""
Predbot - Binance Futures Trading Analysis Bot
Main entry point for running the bot.
"""

import asyncio
from src.bot import Predbot, main

if __name__ == "__main__":
    asyncio.run(main())
