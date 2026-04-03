from dataclasses import dataclass
from typing import List, Optional

import requests

@dataclass
class ConfigExt:
    # 单例实例存储
    _instance: Optional['ConfigExt'] = None

    @classmethod
    def get_instance(cls) -> 'ConfigExt':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def fetch_stocks_from_api(cls) -> List[str]:
        """
        Fetch stock codes from external API and transform them according to exchange rules.

        API: https://trading-view.joinspace.pp.ua/api/trading-plus/strategy/trading?page=1&page_size=1000

        Returns:
            List of transformed stock codes
        """
        import logging
        logger = logging.getLogger(__name__)

        api_url = "https://junhuitsai-trading-plus-ai.hf.space/strategy/trading?page=1&page_size=1000"

        try:
            response = requests.post(api_url, data=[], headers={'Content-Type': 'application/json'}, timeout=10)
            response.raise_for_status()
            result = response.json()

            stock_list = []

            # Extract stock codes from API response
            if 'data' in result and 'items' in result['data']and isinstance(result['data']['items'], list):
                for item in result['data']['items']:
                    stock_code = item.get('stock_code', '').strip()
                    exchange = item.get('exchange', '').upper().strip()
                    strategy_type = item.get('strategy_type', '').upper().strip()
                    if not stock_code:
                        continue
                    if strategy_type not in ['LONG']:
                        continue
                    if exchange not in ['SSE', 'SZSE', 'HKEX']:
                        continue

                    # Transform stock code based on exchange
                    transformed_code = cls._transform_stock_code(stock_code, exchange)
                    if transformed_code:
                        stock_list.append(transformed_code)

            if stock_list:
                logger.info(f"Successfully fetched {len(stock_list)} stocks from API")

            return stock_list

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch stocks from API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching stocks from API: {e}")
            return []

    @classmethod
    def _transform_stock_code(cls, stock_code: str, exchange: str) -> Optional[str]:
        """
        Transform stock code based on exchange rules.

        Args:
            stock_code: Original stock code
            exchange: Exchange name (NASDAQ, HKEX, SSE, SZSE, etc.)

        Returns:
            Transformed stock code or None if invalid
        """
        if not stock_code:
            return None

        stock_code = stock_code.upper()

        # NASDAQ: Remove .NS suffix
        if exchange == 'NASDAQ':
            if stock_code.endswith('.NS'):
                return stock_code[:-3]
            return stock_code

        # HKEX (Hong Kong): Convert to hk + number
        elif exchange == 'HKEX':
            # Remove any existing prefix/suffix and add 'hk' prefix
            code = stock_code.replace('HK', '').replace('.', '')
            # Ensure it's a valid number
            if code.isdigit():
                return f'HK{code}'
            return None

        # SSE (Shanghai Stock Exchange): Remove .SH suffix
        elif exchange in ('SSE', 'SH'):
            if stock_code.endswith('.SH'):
                return stock_code[:-3]
            return stock_code

        # SZSE (Shenzhen Stock Exchange): Remove .SZ suffix
        elif exchange in ('SZSE', 'SZ'):
            if stock_code.endswith('.SZ'):
                return stock_code[:-3]
            return stock_code

        # Other exchanges: return as-is
        else:
            return stock_code