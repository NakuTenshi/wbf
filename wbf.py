import sys
import os 
import re
import requests
from yaspin import yaspin
import argparse
import json
from datetime import datetime

parser = argparse.ArgumentParser(
    description="WaybackFinder (WBF) - a Tool for Extract domains, URLs, and parameters from archive.org snapshots."
)

parser.add_argument('-d', help="Target domain (example: site.tld)", required=True, type=str)
parser.add_argument("--from-year", type=int)
parser.add_argument("--to-year", type=int)





args = parser.parse_args()

# --- Colors ---
red     = "\033[31m"
blue    = "\033[34m"
green   = "\033[32m"
name_bg = "\033[48;5;235m"
gray_bg = "\033[48;5;236m"
reset   = "\033[0m"
bold = "\033[1m"

domain = args.d

current_year = datetime.now().year
from_year = args.from_year if args.from_year else current_year
to_year = args.to_year if args.to_year else current_year

founded_domains = 0
founded_params = 0
founded_param_urls = 0
founded_urls = 0


target_folder = f"./targets/{domain}"
os.makedirs(target_folder, exist_ok=True)

domains_file = f"{target_folder}/domains.txt"
os.system(f"touch {domains_file}") if not os.path.exists(domains_file) else ...

params_file = f"{target_folder}/params.txt"
os.system(f"touch {params_file}") if not os.path.exists(params_file) else ...

url_params_file = f"{target_folder}/url_params.txt"
os.system(f"touch {url_params_file}") if not os.path.exists(url_params_file) else ...

urls_file = f"{target_folder}/all_urls.txt"
os.system(f"touch {urls_file}") if not os.path.exists(urls_file) else ...

def remove_line(n):
    for _ in range(n):
        sys.stdout.write("\033[F")  # move cursor up
        sys.stdout.write("\033[K")  # clear line
    sys.stdout.flush()

def is_exists(filename, word):
    safe_word = re.escape(word)
    regex = re.compile(f"^{safe_word}$")

    with open(filename, "r") as f:
        for line in f:
            if regex.search(line.strip()):
                return True
    return False


def get_domain(url, index):
    global founded_domains

    extracted_domain = url.split("/")[2]

    if not is_exists(domains_file, extracted_domain):
        founded_domains += 1
        with open(domains_file, "a") as f:
            f.write(f"{extracted_domain}\n")

            remove_line(1)
            print(f"[{index}] Domain saved: {extracted_domain} -> {domains_file}")


def get_params(url, index):
    global founded_params

    if "?" in url:
        params_values = url.split("?")[-1].split("&")
        params = [i.split("=")[0] for i in params_values if i != "" or i != " "]

        for param in params:
            if not is_exists(params_file, param):
                founded_params += 1

                with open(params_file, "a") as f:
                    f.write(f"{param}\n")

                    remove_line(1)
                    print(f"[{index}] Param saved: {param} -> {params_file}")


def get_params_url(url, index):
    global founded_param_urls

    if "?" in url and not is_exists(url_params_file, url):
        founded_param_urls += 1
        with open(url_params_file, "a") as f:
            f.write(f"{url}\n")

            remove_line(1)
            print(f"[{index}] Param's URL saved at {url_params_file}")


def get_url(url, index):
    global founded_urls

    if not is_exists(urls_file, url):
        founded_urls += 1

        remove_line(1)
        print(f"[{index}] Saving URL...")
        with open(urls_file, "a") as f:
            f.write(f"{url}\n")


def banner():
    os.system("clear")
    me = f"created by: " + name_bg + red + "NakuTenshi" + reset + reset
    print(f"""{red}
    █     █░ ▄▄▄▄     █████▒
   ▓█░ █ ░█░▓█████▄ ▓██   ▓ 
   ▒█░ █ ░█ ▒██▒ ▄██▒████ ▒ 
   ░█░ █ ░█ ▒██░█▀  ░▓█▒  ░ 
   ░░██▒██▓ ░▓█  ▀█▓░▒█░    
   ░ ▓░▒ ▒  ░▒▓███▀▒ ▒ ░  ░ 
     ▒ ░ ░  ▒░▒   ░  ░    
     ░   ░   ░    ░  ░ ░  fuck this people
       ░     ░            {reset}WaybackFinder: Extract {red}domains{reset}, {red}URLs{reset}, and {red}params{reset}{red}
                  ░       {reset}{me}{red}
""")

def main():
    banner()

    print(f"{red}<--------------------- {reset}{red}{bold}Status{reset}{reset}{red} --------------------->{reset}")
    print(f'Target: {gray_bg}{red}{domain}{reset}{reset}')
    print(f"Searching from year: {gray_bg}{red}{from_year}{reset}{reset}")
    print(f"Searching to year: {gray_bg}{red}{to_year}{reset}{reset}")

    print(f"\n{red}<---------------------- {reset}{red}{bold}Logs{reset}{reset}{red} ---------------------->{reset}")

    with yaspin(text="Sending request to archive.org...", color="red") as sp:
        response = requests.get(
            "https://web.archive.org/cdx/search/cdx",
            stream=True,
            params={
                "url": domain,
                "matchType": "domain",
                "fl": "original",
                "collapse": "urlkey",
                "output": "json",
                "from": from_year,
                "to": to_year,
            },
        )

        if response.status_code == 200:
            sp.write(text=f"[{red}✔{reset}] Data successfully retrieved from archive.org\n")
            sp.stop()

            for index, line in enumerate(response.iter_lines()):
                if index == 0:
                    continue  # skip header
                if line:
                    index = f"{red}{index}{reset}" # make the index number to red
                    decoded = line.decode("utf-8").strip()[:-1]
                    url = json.loads(decoded)[0]

                    remove_line(1)
                    print(f'[{index}] Processing the URL')
                    get_domain(url, index)
                    get_params(url, index)
                    get_params_url(url, index)
                    get_url(url, index)

            remove_line(1)
            print(f"[{red}INFO{reset}] Domains found: {red}{founded_domains}{reset}")
            print(f"[{red}INFO{reset}] Parameters found: {red}{founded_params}{reset}")
            print(f"[{red}INFO{reset}] URLs with parameters: {red}{founded_param_urls}{reset}")
            print(f"[{red}INFO{reset}] Total URLs found: {red}{founded_urls}{reset}")

            print(f"[{red}DONE{reset}] Saved results in: {target_folder}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"{red}[ERROR{reset}] Connection failed. Please check your internet connection.")
    except KeyboardInterrupt:
        print("\nBye :)")
        exit()
    except Exception as e:
        print(f"[{red}ERROR{reset}] An unexpected error occurred: {e}")
