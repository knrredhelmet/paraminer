import requests
import random
import logging
import time

logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 3

def load_user_agents():
    """
    Loads a list of user agents.
    """
    return [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        # ... [add user agents]
    ]

def fetch_url_content(url, proxy=None):
    """
    Fetches the content of a URL using a random user agent.
    Retries up to MAX_RETRIES times if the request fails.
    """
    user_agents = load_user_agents()
    proxies = {'http': proxy, 'https': proxy} if proxy else None

    for attempt in range(MAX_RETRIES):
        user_agent = random.choice(user_agents)
        headers = {"User-Agent": user_agent}

        try:
            response = requests.get(url, proxies=proxies, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt + 1}/{MAX_RETRIES}: Retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.warning("Keyboard Interrupt received. (Use CTRL+Z for FULL STOP)")
            return None  # Instead of exiting, just return None to indicate an interruption

    logging.error(f"Failed to fetch URL after {MAX_RETRIES} retries.")
    return None  # Return None if all retries fail
