import os, re, random, string, configparser
from tempfile import mkstemp
from time import sleep, thread_time
from typing import Set
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore, init
from ctypes import windll
import requests
from requests import Session
from random import choice
from threading import Thread, Lock
from easygui import fileopenbox
from fake_useragent import UserAgent
from timeit import default_timer as timer
checkerAgent = UserAgent()

class Stats:
    cpm = 0
    good = 0
    bad = 0
    upcoming = 0
    error = 0
    blocked = 0
    checked = 0
    eta = ''

class Settings:
    threads = 100
    printBad = False
    printUpcoming = True

class Proxies:
    list = []
    type = 'socks4'

class Checker:
    logo = """
        
 ███▄    █  ▄▄▄       ███▄ ▄███▓▓█████  ▄████▄   ██░ ██ ▓█████  ▄████▄   ██ ▄█▀▓█████  ██▀███        ██▓███ ▓██   ██▓
 ██ ▀█   █ ▒████▄    ▓██▒▀█▀ ██▒▓█   ▀ ▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒     ▓██░  ██▒▒██  ██▒
▓██  ▀█ ██▒▒██  ▀█▄  ▓██    ▓██░▒███   ▒▓█    ▄ ▒██▀▀██░▒███   ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒     ▓██░ ██▓▒ ▒██ ██░
▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄ ▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒▓▓▄ ▄██▒▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄       ▒██▄█▓▒ ▒ ░ ▐██▓░
▒██░   ▓██░ ▓█   ▓██▒▒██▒   ░██▒░▒████▒▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒ ▓███▀ ░▒██▒ █▄░▒████▒░██▓ ▒██▒ ██▓ ▒██▒ ░  ░ ░ ██▒▓░
░ ▒░   ▒ ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ░▒ ▒  ░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░ ▒▓▒ ▒▓▒░ ░  ░  ██▒▒▒ 
░ ░░   ░ ▒░  ▒   ▒▒ ░░  ░      ░ ░ ░  ░  ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░  ▒   ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░ ░▒  ░▒ ░     ▓██ ░▒░ 
   ░   ░ ░   ░   ▒   ░      ░      ░   ░         ░  ░░ ░   ░   ░        ░ ░░ ░    ░     ░░   ░  ░   ░░       ▒ ▒ ░░  
         ░       ░  ░       ░      ░  ░░ ░       ░  ░  ░   ░  ░░ ░      ░  ░      ░  ░   ░       ░           ░ ░     
                                       ░                       ░                                 ░           ░ ░                                                                                                                 
"""

class Main:
    def __init__(self):
        clear()
        self.version = '2.2'
        self.start_time = None
        self.is_running = True
        self.total_names = 1
        self.name_list = []
        self.config_loader = configparser.RawConfigParser()
        self.pre_init()
        self.run_checker()

    def pre_init(self):
        self.set_title('NameChecker.py [Loading...]')
        self.setup_out_files()
        print(f'{blue}{Checker.logo}\n\n\n')
        print(f'{yellow}[i] Loading...')
        self.update_checker()
        needs_setup = None
        if not os.path.isfile('NameChecker.cfg'):
            needs_setup = True
        else:
            needs_setup = False
        if not needs_setup:
            self.config_loader.read(r'NameChecker.cfg')
            self.load_config()
            self.get_proxies()
            if len(Proxies.list) <= 1:
                clear()
                print(f'{red}{Checker.logo}\n\n\n')
                print(f'{red}[!] An error occured while scraping proxies, please re-launch.')
                exit()
            print(f'{green} > Scraped {len(Proxies.list)} {Proxies.type} proxies')
            sleep(2)
            clear()
            self.import_names()
            if Settings.threads > len(self.name_list):
                print(f'{red}[!] Your saved config has too many threads!')
                print(f'{yellow}[i] How many threads would you like to use?')
                try:
                    Settings.threads = int(input(''))
                except:
                    print(f'{red}[!] Invalid entry, please edit your config file and re-launch.')
                    exit()
        else:
            sleep(2)
            clear()
            self.import_names()
            self.setup_config()
            self.get_proxies()
        clear()

    def update_checker(self):
        latestVer = self.version
        try:
            reply = requests.get(url='https://raw.githubusercontent.com/GhostTypes/MC-NameChecker/main/version.txt', timeout=5)
            latestVer = str(reply.text)
        except:
            print(f'{yellow}[i] Failed to check latest version!')
            sleep(2.3)
        if f'{self.version}\n' != latestVer:
            print(f'{yellow}[i] There\'s an update ready! Your version: {self.version} | Latest Release: {latestVer}')
            print(f'{yellow}[i] Get the latest version from the Github Repo: https://github.com/GhostTypes/MC-NameChecker')
            print(f'{yellow}[i] Continuing with outdated version in 5 seconds, press CTRL + C to exit.')
            sleep(5)

    def load_config(self):
        try:
            proxy_type = self.config_loader.get('Config', 'proxy_type')
            checker_threads = self.config_loader.getint('Config', 'threads')
            checker_print_upcoming = self.config_loader.getboolean('Config', 'print_upcoming')
            checker_print_bad = self.config_loader.getboolean('Config', 'print_bad')
        except:
            clear()
            print(f'{red}{Checker.logo}\n\n\n')
            print(f'{red}[!] Your config file is invalid')
            exit()
        Settings.threads = checker_threads
        Settings.printUpcoming = checker_print_upcoming
        Settings.printBad = checker_print_bad
        Proxies.type = proxy_type.replace("'", "")

    def run_checker(self):
        clear()
        self.set_title(f'NameChecker.py | [Starting {Settings.threads} threads]')
        print(f'{green}{Checker.logo}\n\n\n')
        print(f'{green} > Starting...')
        mainpool = ThreadPool(processes=Settings.threads)
        self.start_time = timer()
        Thread(target=self.cpm_counter, daemon=True).start()
        Thread(target=self.eta_tracker, daemon=True).start()
        Thread(target=self.proxy_reloader, daemon=True).start()
        Thread(target=self.title_manager).start()
        print(f'{green} > Running!')
        #clear()
        mainpool.imap_unordered(func=self.check_name, iterable=self.name_list)
        mainpool.close()
        mainpool.join()
        self.is_running = False
        self.end_time = timer()
        total_runtime = self.convert_secs(self.end_time - self.start_time)
        clear()
        print(f'{green}{Checker.logo}\n\n\n')
        print(f'{green}> Name checking finished!')
        print(f'{green}==========[Stats]=========')
        print(f'{blue}Open Names: {Stats.good} (saved to open_names.txt)')
        print(f'{blue}Upcoming Names: {Stats.upcoming} (saved to upcoming_names.txt)')
        print(f'{blue}Claimed Names: {Stats.bad}')
        print(f'{blue}Blocked Names: {Stats.blocked}')
        print(f'{yellow}Total Runtime: {total_runtime}')
        exit()

    def setup_out_files(self):
        with open('open_names.txt', 'w') as f:
            f.write('')
        with open('upcoming_names.txt', 'w') as f:
            f.write('')

    def save_open_name(self, name):
        #lock.acquire()
        with open('open_names.txt', 'a') as f:
            f.write(f'{name}\n')
        #lock.release()
    
    def save_upcoming_name(self, name):
        #lock.acquire()
        with open('upcoming_names.txt', 'a') as f:
            f.write(f'{name}\n')
        #lock.release()

    def setup_config(self):
        proxies_setup = False
        threads_setup = False
        upcoming_setup = False
        bad_setup = False
        while not proxies_setup:
            clear()
            print(f'{blue}{Checker.logo}\n\n\n')
            print(f'{blue}Select your proxy type')
            print(f'{blue}[1] HTTP(S)')
            print(f'{blue}[2] SOCKS4 (Default)')
            print(f'{blue}[3] SOCKS5')
            try:
                choice = int(input('>'))
            except:
                choice = 0
            if choice == 1:
                Proxies.type = 'http'
                proxies_setup = True
            elif choice == 2:
                Proxies.type = 'socks4'
                proxies_setup = True
            elif choice == 3:
                Proxies.type = 'socks5'
                proxies_setup = True
            else:
                clear()
                print(f'{red}{Checker.logo}\n\n\n')
                print(f'{red}Invalid choice, please try again.')
                sleep(2)
        clear()
        print(f'{blue}{Checker.logo}\n\n\n')
        print(f'{yellow}Scraping {Proxies.type} proxies...')
        self.get_proxies()
        if len(Proxies.list) <= 1:
            print(f'{red}[!] An error occured while scraping proxies, please re-launch.')
            exit()
        print(f'{green} > Scraped {len(Proxies.list)} proxies!')
        sleep(2)
        threads = 0
        while not threads_setup:
            clear()
            print(f'{blue}{Checker.logo}\n\n\n')
            print(f'{blue}How many threads would you like to use?')
            try:
                threads = int(input('>'))
            except:
                threads = 0
            if threads <= self.total_names:
                    Settings.threads = threads
                    threads_setup = True
            else:
                print(f'{red}Too many threads!')
                sleep(2)
        print_upcoming = 'True'
        while not upcoming_setup:
            clear()
            print(f'{blue}{Checker.logo}\n\n\n')
            print(f'{blue}Print Upcoming Names? (Y/N)')
            choice = str(input('>')).lower()
            if choice == 'y':
                upcoming_setup = True
            elif choice == 'n':
                print_upcoming = 'False'
                upcoming_setup = True
            else:
                clear()
                print(f'{red}{Checker.logo}\n\n\n')
                print(f'{red}Invalid choice, please try again.')
                sleep(2)
        if print_upcoming == 'True':
            Settings.printUpcoming = True
        else:
            Settings.printUpcoming = False
        print_bad = 'False'
        while not bad_setup:
            clear()
            print(f'{blue}{Checker.logo}\n\n\n')
            print(f'{blue}Print Bad Names? (Y/N)')
            choice = str(input('>')).lower()
            if choice == 'y':
                bad_setup = True
            elif choice == 'n':
                print_bad = 'False'
                bad_setup = True
            else:
                clear()
                print(f'{red}{Checker.logo}\n\n\n')
                print(f'{red}Invalid choice, please try again.')
                sleep(2)
        if print_bad == 'True':
            Settings.printBad = True
        else:
            Settings.printBad = False
        with open('NameChecker.cfg', 'w') as f:
            f.write('[Config]\n')
            f.write(f"proxy_type = '{Proxies.type}'\n")
            f.write(f'threads = {threads}\n')
            f.write(f'print_upcoming = {print_upcoming}\n')
            f.write(f'print_bad = {print_bad}')
        clear()
        print(f'{blue}{Checker.logo}\n\n\n')
        print(f'{green}Setup Complete!')
        sleep(2)

    def get_proxies(self):
        self.set_title('NameChecker.py [Scraping Proxies...]')
        loader = requests.get(f'https://www.proxyscan.io/download?type={Proxies.type}').text.split('\n')
        Proxies.list = list(set([x.strip() for x in loader if ":" in x and x != '']))
    
    def proxy_reloader(self):
        while self.is_running:
            sleep(300)
            self.safe_print(f'{yellow}[i] Refreshing proxies...')
            loader = requests.get(f'https://www.proxyscan.io/download?type={Proxies.type}').text.split('\n')
            Proxies.list = list(set([x.strip() for x in loader if ":" in x and x != '']))
            if len(Proxies.list) > 1:
                self.safe_print(f'{yellow}[i] Got {len(Proxies.list)} fresh proxies')
            else:
                self.safe_print(f'{yellow}[!] Proxy refresh failed.')

    def eta_tracker(self):
        while self.is_running:
            if Stats.checked >= 1:
                cps = Stats.cpm / 60
                names_left = int(self.total_names - Stats.checked)
                try:
                    time_left = self.convert_secs(names_left / cps)
                except:
                    time_left = 0
                Stats.eta = time_left
                sleep(10)

    def cpm_counter(self):
        while self.is_running:
            if Stats.checked >= 1:
                now = Stats.checked
                sleep(3)
                Stats.cpm = (Stats.checked - now) * 20

    def convert_secs(self, seconds):
        seconds = round(seconds) % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def set_title(self, title):
        windll.kernel32.SetConsoleTitleW(title)
    
    def percentage(self, part, whole):
        return round(100 * float(part)/float(whole))
    
    def title_manager(self):
        while self.is_running:
            time_now = timer()
            time_elapsed = self.convert_secs(time_now - self.start_time)
            perc = self.percentage(Stats.checked, self.total_names)
            if Stats.checked < (self.total_names - (int(round(Settings.threads))) / 4):
                windll.kernel32.SetConsoleTitleW(
                    f'NameChecker.py @ {Settings.threads} threads | [{perc}% complete] ({Stats.checked} / {self.total_names})'
                    f' | CPM: {Stats.cpm}'
                    f' | Errors: {Stats.error}'
                    f' | Proxies: {len(Proxies.list)}'
                    f' | Hits: {Stats.good}'
                    f' | Dropping: {Stats.upcoming}'
                    f' | Bad: {Stats.bad}'
                    f' | Blocked: {Stats.blocked}'
                    f' | Running for: {time_elapsed}'
                    f' | ETA: {Stats.eta}'
                )
            else:
                windll.kernel32.SetConsoleTitleW(
                    f'NameChecker.py @ {Settings.threads} threads | [{perc}% complete] ({Stats.checked} / {self.total_names})'
                    f' | Waiting for threads to finish...'
                    f' | Running for: {time_elapsed}'
                )

    def import_names(self):
        self.set_title('NameChecker.py [Importing Names]')
        while True:
            try:
                print(f'{blue}{Checker.logo}\n\n\n')
                print(f'{blue}Import your names')
                sleep(0.3)
                loader = open(fileopenbox(title="Import Names", default="*.txt"), 'r', encoding="utf8", errors='ignore').read().split('\n')
                self.name_list = list(set(x.strip() for x in loader if x != ''))
                if len(self.name_list) == 0:
                    print(f'{red}File is empty!\n')
                    continue
                print(f"{green} > Loaded {len(self.name_list)} names")
                sleep(2)
                break
            except:
                exit()
        self.total_names = len(self.name_list)
        clear()

    def format_proxy(self, proxy):
        return {'http': f"{Proxies.type}://{proxy}", 'https': f"{Proxies.type}://{proxy}"}

    def get_user_agent(self):
        return {'User-Agent':str(checkerAgent.random)}
    
    def safe_print(self, s):
        lock.acquire()
        print(s)
        lock.release()

    #Checker Stuff
    def is_blocked(self, name):
        status = 0
        nurl = f'{mc_url}{name}'
        while status == 0:
            proxy = choice(Proxies.list)
            broxy = self.format_proxy(proxy)
            user_agent = self.get_user_agent()
            try:
                r = requests.get(url=nurl, headers=user_agent, proxies=broxy, timeout=4)
                #print(r.text)
                if r.text == 'AVAILABLE':
                    return False
                elif r.text == 'TAKEN':
                    status = True
                    return True
                else:
                    Stats.error += 1
            except:
                Stats.error += 1
                if len(Proxies.list) >= 1001:
                    try:
                        Proxies.list.remove(proxy)
                    except:
                        None

    def get_name_status(self, name):
        nstatus = 0
        nurl = f'{nmc_url}{name}'
        desc = ''
        n_status = {
            "type": "0",
            "searches": "0",
            "dropTime": "None"
        }
        while nstatus == 0:
            proxy = choice(Proxies.list)
            broxy = self.format_proxy(proxy)
            user_agent = self.get_user_agent()
            try:
                r = requests.get(url=nurl, headers=user_agent, proxies=broxy, timeout=4)
                if r.status_code == 200:
                    b = BeautifulSoup(r.text, features='html.parser')
                    desc = str(b.find(attrs={"name": re.compile(r'description', re.I)}))
                    break
                elif r.status_code == 429:
                    Stats.error += 1
                    sleep(10)
                else:
                    Stats.error += 1
                    sleep(5)
            except:
                Stats.error += 1
                if len(Proxies.list) >= 1001:
                    try:
                        Proxies.list.remove(proxy)
                    except:
                        None
        Stats.checked += 1
        try:
            n_status['searches'] = str(desc.split("Searches: ")[1].split("/")[0].replace(" ", ""))
        except:
            n_status['searches'] = 'Error'
        if "Available*" in desc and "Time Of" not in desc:
            if self.is_blocked(name):
                n_status['type'] = 4
            else:
                n_status['type'] = 1
        elif "Time of" in desc and "Unavailable" not in desc:
            n_status['type'] = 2
            dropTime = "Error"
            try:
                dS = desc.split(",")[0].split('"')[1].split(' ')[3].split('T')
                dropTime = f'{dS[0]}  {dS[1]}'
                dropTime = dropTime.replace('Z', '')
                n_status['dropTime'] = dropTime
            except:
                n_status['dropTime'] = dropTime
        else:
            n_status['type'] = 3
        return n_status

    def check_name(self, name):
        name_status = self.get_name_status(name)
        searches = name_status['searches']
        drop_time = name_status['dropTime']
        if name_status['type'] == 1:
            Stats.good += 1
            self.safe_print(f'{green}[H] {name} | Searches: {searches}')
            self.save_open_name(f'{name} ({searches} searches)')
        elif name_status['type'] == 2:
            Stats.upcoming += 1
            self.safe_print(f'{yellow}[D] {name} | Searches: {searches} | Dropping at: {drop_time}')
            self.save_upcoming_name(f'{name} ({searches} searches) (Dropping at: {drop_time})')
        elif name_status['type'] == 3:
            Stats.bad += 1
            if Settings.printBad:
                self.safe_print(f'{red}[C] {name} | Searches: {searches}')
        elif name_status['type'] == 4:
            Stats.blocked += 1
            self.safe_print(f'{red}[B] {name} | Searches: {searches}')
        else:
            None
        
if __name__ == '__main__':
    init()
    clear = lambda: os.system('cls')
    blue = Fore.LIGHTBLUE_EX
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    yellow = Fore.LIGHTYELLOW_EX
    lock = Lock()
    session = Session()
    nmc_url = 'https://namemc.com/search?q='
    mc_url = 'https://account.mojang.com/available/minecraft/'
    Main()