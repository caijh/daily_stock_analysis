#!/usr/bin/env python
"""
Script to fetch stock list from external API and update .env file.
Used in GitHub Actions to set STOCK_LIST environment variable.
"""

import os
import sys
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fetch_my_stock_list import ConfigExt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def update_env_file(stock_list: list, env_file_path: str = '.env'):
    """Update STOCK_LIST in .env file"""
    if not os.path.exists(env_file_path):
        logger.warning(f".env file not found at {env_file_path}, creating new one")
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Auto-generated stock list\nSTOCK_LIST={','.join(stock_list)}\n")
        logger.info(f"Created .env file with {len(stock_list)} stocks")
        return

    # Read existing .env file
    with open(env_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Update or add STOCK_LIST line
    updated = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('STOCK_LIST='):
            new_lines.append(f"STOCK_LIST={','.join(stock_list)}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        # Add STOCK_LIST at the end
        new_lines.append(f"\nSTOCK_LIST={','.join(stock_list)}\n")

    # Write back to file
    with open(env_file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    logger.info(f"Updated STOCK_LIST in .env with {len(stock_list)} stocks")


def main():
    """Main function to fetch stocks and update .env"""
    logger.info("Fetching stock list from external API...")
    stocks = ConfigExt.fetch_stocks_from_api()

    if not stocks:
        logger.warning("No stocks fetched from API, .env will not be updated")
        # Still output empty list for GitHub Actions
        print(f"STOCK_LIST=")
        return

    # stocks只取前10
    if len(stocks) > 20:
        stocks = stocks[:20]

    # Update .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    update_env_file(stocks, env_path)

    # Output for GitHub Actions to capture
    stock_list_str = ','.join(stocks)
    print(f"STOCK_LIST={stock_list_str}")
    logger.info(f"Stock list: {stock_list_str}")


if __name__ == '__main__':
    main()