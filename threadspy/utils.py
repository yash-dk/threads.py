from typing import Any

def get_default_headers() -> dict:
    return {
        'Authority': 'www.threads.net',
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
            'q=0.8,application/signed-exchange;v=b3;q=0.7'
        ),
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.instagram.com',
        'Origin': 'https://www.threads.net',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15'
        ),
        'X-ASBD-ID': '129477',
        'X-IG-App-ID': '238260118697367',
    }

def populate_if_available(cls: Any, data: dict, key: str,threads_client = None) -> Any:
    if data.get(key) is not None:
        return cls.from_dict(data[key]) if threads_client is None else cls.from_dict(data[key],threads_client)
    else:
        return None
