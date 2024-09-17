import argparse
import sys
import os
import logging
import colorama
from colorama import Fore, Style
import client  # Importing client
from urllib.parse import urlparse, parse_qs, urlencode

yellow_color_code = "\033[93m"
reset_color_code = "\033[0m"

colorama.init(autoreset=True)  # Initialize colorama for colored terminal output

log_format = '%(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
logging.getLogger('').handlers[0].setFormatter(logging.Formatter(log_format))

HARDCODED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".json",
    ".css", ".js", ".webp", ".woff", ".woff2", ".eot", ".ttf", ".otf", ".mp4", ".txt"
]

def has_extension(url, extensions):
    """
    Check if the URL has a file extension matching any of the provided extensions.

    Args:
        url (str): The URL to check.
        extensions (list): List of file extensions to match against.

    Returns:
        bool: True if the URL has a matching extension, False otherwise.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    extension = os.path.splitext(path)[1].lower()

    return extension in extensions

def clean_url(url):
    """
    Clean the URL by removing redundant port information for HTTP and HTTPS URLs.

    Args:
        url (str): The URL to clean.

    Returns:
        str: Cleaned URL.
    """
    parsed_url = urlparse(url)
    
    if (parsed_url.port == 80 and parsed_url.scheme == "http") or (parsed_url.port == 443 and parsed_url.scheme == "https"):
        parsed_url = parsed_url._replace(netloc=parsed_url.netloc.rsplit(":", 1)[0])

    return parsed_url.geturl()

def clean_urls(urls, extensions, placeholder):
    """
    Clean a list of URLs by removing unnecessary parameters and query strings.
    Args:
        urls (list): List of URLs to clean.
        extensions (list): List of file extensions to check against.
        placeholder (str): Placeholder for parameter values.
    Returns:
        list: List of cleaned URLs.
    """
    cleaned_urls = set()
    for url in urls:
        cleaned_url = clean_url(url)
        if not has_extension(cleaned_url, extensions):
            parsed_url = urlparse(cleaned_url)
            query_params = parse_qs(parsed_url.query)
            if query_params:  # Check if there are any query parameters
                cleaned_params = {key: placeholder for key in query_params}
                cleaned_query = urlencode(cleaned_params, doseq=True)
                cleaned_url = parsed_url._replace(query=cleaned_query).geturl()
                cleaned_urls.add(cleaned_url)
    return list(cleaned_urls)


def fetch_and_clean_urls(domain, extensions, silent, proxy, placeholder, global_file=None):
    """
    Fetch and clean URLs related to a specific domain from the Wayback Machine.
    """
    wayback_uri = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=txt&collapse=urlkey&fl=original&page=/"
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Fetching URLs for {Fore.CYAN + domain + Style.RESET_ALL}")
    response = client.fetch_url_content(wayback_uri, proxy)
    
    if response is None:
        logging.error(f"Failed to fetch data for domain {Fore.RED + domain + Style.RESET_ALL}")
        return

    urls = response.text.split()
   # logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Raw URLs: {urls}")
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Found {Fore.GREEN + str(len(urls)) + Style.RESET_ALL} URLs for {Fore.CYAN + domain + Style.RESET_ALL}")

    cleaned_urls = clean_urls(urls, extensions, placeholder)
   # logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Cleaned URLs: {cleaned_urls}")
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Found {Fore.GREEN + str(len(cleaned_urls)) + Style.RESET_ALL} URLs after cleaning")

    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    if global_file:
        with open(global_file, "a") as f:
            for url in cleaned_urls:
                f.write(url + "\n")
        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Appended cleaned URLs to global file {Fore.CYAN + global_file + Style.RESET_ALL}")

    elif not global_file:
        result_file = os.path.join(results_dir, f"{domain}.txt")
        with open(result_file, "w") as f:
            for url in cleaned_urls:
                f.write(url + "\n")
                if not silent:
                    print(url)
        
        logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Saved cleaned URLs to {Fore.CYAN + result_file + Style.RESET_ALL}")

def clear_files(global_file, results_dir):
    """
    Clear the content of the global file and delete all files in the results directory.

    Args:
        global_file (str): Path to the global output file.
        results_dir (str): Path to the results directory.

    Returns:
        None
    """
    if global_file:
        # Clear the content of the global file if it exists
        with open(global_file, "w") as f:
            f.truncate(0)  # Clear the file content
       # logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Cleared global file {Fore.CYAN + global_file + Style.RESET_ALL}")

    if os.path.exists(results_dir):
        for file_name in os.listdir(results_dir):
            file_path = os.path.join(results_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
       # logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Cleared all files in results directory {Fore.CYAN + results_dir + Style.RESET_ALL}")

# Define the log text once
log_text = """
   ____                 __  __ _                  
|  _ \\ __ _ _ __ __ _|  \\/  (_)_ __   ___ _ __ 
| |_) / _` | '__/ _` | |\\/| | | '_ \\ / _ \\ '__|
|  __/ (_| | | | (_| | |  | | | | | |  __/ |   
|_|   \\__,_|_|  \\__,_|_|  |_|_|_| |_|\\___|_|   

                  by RedHelmet
"""

def print_banner():
    # Print the banner text
    print(f"{yellow_color_code}{log_text}{reset_color_code}")

def main():
    """
    Main function to handle command-line arguments and start URL mining process.
    """
    parser = argparse.ArgumentParser(description="Getting URLs from Web Archives")
    parser.add_argument("-d", "--domain", help="Domain name to fetch related URLs for.")
    parser.add_argument("-l", "--list", help="File containing a list of domain names.")
    parser.add_argument("-s", "--silent", action="store_true", help="Suppress terminal output and banner.")
    parser.add_argument("--proxy", help="Set the proxy address for web requests.", default=None)
    parser.add_argument("-p", "--placeholder", help="Placeholder for parameter values", default="FUZZ")
    parser.add_argument("-g", "--global-file", help="Path to a global file where URLs are appended.")
    
    # Check if -h or --help is in sys.argv before parsing
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
        # Print the banner text before showing help
        print_banner()

    # Proceed to parse arguments and run the main logic
    args = parser.parse_args()

    # Clear files and directory if required
    clear_files(args.global_file, "results")

    if not args.domain and not args.list:
        parser.error("Please provide either the -d option or the -l option.")

    if args.domain and args.list:
        parser.error("Please provide either the -d option or the -l option, not both.")

    extensions = HARDCODED_EXTENSIONS

    # Print the banner if not in silent mode
    if not args.silent:
        print_banner()

    if args.list:
        with open(args.list, "r") as f:
            domains = [line.strip().lower().replace('https://', '').replace('http://', '') for line in f.readlines()]
            domains = [domain for domain in domains if domain]  # Remove empty lines
            domains = list(set(domains))  # Remove duplicates
        for domain in domains:
            fetch_and_clean_urls(domain, extensions, args.silent, args.proxy, args.placeholder, args.global_file)
    elif args.domain:
        domain = args.domain.lower().replace('https://', '').replace('http://', '')
        fetch_and_clean_urls(domain, extensions, args.silent, args.proxy, args.placeholder, args.global_file)

if __name__ == "__main__":
    main()