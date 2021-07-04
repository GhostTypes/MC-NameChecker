import os, re, random, string, json, configparser
from time import sleep
#from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore, init
from ctypes import windll
import requests
from requests import Session
from random import choice
from threading import Thread, Lock
from easygui import fileopenbox
from timeit import default_timer as timer

class Stats:
    cpm = 0
    good = 0
    bad = 0
    upcoming = 0
    error = 0
    blocked = 0
    checked = 0

class Results:
    good = []
    upcoming = []

class Name:
    status = ''
    droptime = ''

class Main:
    def __init__(self):
        clear()
        self.config_loader = configparser.RawConfigParser()
        self.isRunning = False
        self.proxylist = []
        self.namelist = []
        self.namelistsize = 0
        self.startTime = 0
        self.endTime = 0
        self.threads = 85
        self.proxy_reload_wait = 300
        self.logo = """
 ███▄    █  ▄▄▄       ███▄ ▄███▓▓█████  ▄████▄   ██░ ██ ▓█████  ▄████▄   ██ ▄█▀▓█████  ██▀███        ██▓███ ▓██   ██▓
 ██ ▀█   █ ▒████▄    ▓██▒▀█▀ ██▒▓█   ▀ ▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒     ▓██░  ██▒▒██  ██▒
▓██  ▀█ ██▒▒██  ▀█▄  ▓██    ▓██░▒███   ▒▓█    ▄ ▒██▀▀██░▒███   ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒     ▓██░ ██▓▒ ▒██ ██░
▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄ ▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒▓▓▄ ▄██▒▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄       ▒██▄█▓▒ ▒ ░ ▐██▓░
▒██░   ▓██░ ▓█   ▓██▒▒██▒   ░██▒░▒████▒▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒ ▓███▀ ░▒██▒ █▄░▒████▒░██▓ ▒██▒ ██▓ ▒██▒ ░  ░ ░ ██▒▓░
░ ▒░   ▒ ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ░▒ ▒  ░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░ ▒▓▒ ▒▓▒░ ░  ░  ██▒▒▒ 
░ ░░   ░ ▒░  ▒   ▒▒ ░░  ░      ░ ░ ░  ░  ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░  ▒   ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░ ░▒  ░▒ ░     ▓██ ░▒░ 
   ░   ░ ░   ░   ▒   ░      ░      ░   ░         ░  ░░ ░   ░   ░        ░ ░░ ░    ░     ░░   ░  ░   ░░       ▒ ▒ ░░  
         ░       ░  ░       ░      ░  ░░ ░       ░  ░  ░   ░  ░░ ░      ░  ░      ░  ░   ░       ░           ░ ░     
                                       ░                       ░                                 ░           ░ ░"""
        self.prep()
        self.start()
    
    def prep(self):
        clear()
        self.setTitle('NameChecker.py v2 | by NotGhostTypes#0872')
        print(f'{blue}{self.logo}\n\n\nLoading...')
        self.loadConfig()
        self.loadProxy()
        self.loadNameMenu()
        self.isRunning = True
    
    def start(self):
        clear()
        self.setTitle(f'NameChecker.py v2 | [Starting {self.threads} threads]')
        print(f'{blue}{self.logo}\n\n\n')
        print(f'{blue} > Starting {self.threads} threads...')
        mainpool = ThreadPool(processes=self.threads)
        Thread(target=self.cpmCounter, daemon=True).start()
        Thread(target=self.proxyReloader, daemon=True).start()
        Thread(target=self.title).start()
        clear()
        print(f'{blue}{self.logo}\n\n\n')
        self.startTime = timer()
        mainpool.imap_unordered(func=self.checkNames, iterable=self.namelist)
        mainpool.close()
        mainpool.join()
        self.isRunning = False
        self.endTime = timer()
        clear()
        print(f'{blue}{self.logo}\n\n\n')
        print(f'{green}Name Checker Finished!')
        print(f'{blue}Open Names: {Stats.good}')
        print(f'{blue}Upcoming Names: {Stats.upcoming}')
        print(f'{blue}Claimed Names: {Stats.bad}')
        print(f'{yellow}Total Runtime: {self.convertSec(self.endTime - self.startTime)}')
        self.saveHits()

    def safePrint(self, line):
        lock.acquire()
        print(line)
        lock.release()


    def loadConfig(self):
        if not os.path.isfile('NameChecker.cfg'):
            print(f'{yellow}[i] Config file not found, creating default config.')
            with open('NameChecker.cfg', 'w') as f:
                f.write('[Config]\nthreads = 150\nproxy_reload = 300')
        self.config_loader.read(r'NameChecker.cfg')
        try:
            threads = self.config_loader.getint('Config', 'threads')
        except:
            print(f'{red}[!] threads setting is invalid or does not exist, check your config file!')
            exit()
        try:
            proxy_reload_wait = self.config_loader.getint('Config', 'proxy_reload_wait')
        except:
            print(f'{red}[!] proxy_reload_wait setting is invalid or does not exist, check your config file!')
            exit()
        self.threads = threads
        self.proxy_reload_wait = proxy_reload_wait

    def loadProxy(self):
        loader = requests.get('https://www.proxyscan.io/download?type=socks4').text.split('\n')
        self.proxylist = list(set([x.strip() for x in loader if ":" in x and x != '']))
    
    def proxyReloader(self):
        while self.isRunning:
            if Stats.checked >= 1:
                sleep(self.proxy_reload_wait)
                self.safePrint(f'{yellow}[i] Refreshing proxies...')
                try:
                    self.loadProxy()
                except:
                    self.safePrint(f'{red}[!] Unable to refresh proxies!')
    
    def formatProxy(self, proxy):
        return {'http': f"socks4://{proxy}", 'https': f"socks4://{proxy}"}

    def saveHits(self):
        if Stats.good >= 1:
            with open('open_names.txt', 'w') as f:
                for name in Results.good:
                    f.write(f'{name}\n')
        if Stats.upcoming >= 1:
            with open('upcoming_names.txt', 'w') as f:
                for name in Results.upcoming:
                    f.write(f'{name}\n')

    def cpmCounter(self):
        while self.isRunning:
            if Stats.checked >= 1:
                now = Stats.checked
                sleep(3)
                Stats.cpm = (Stats.checked - now) * 20

    def percentage(self, part, whole):
        return round(100 * float(part)/float(whole))

    def convertSec(self, seconds):
        seconds = round(seconds)
        seconds = seconds % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def setTitle(self, title):
        windll.kernel32.SetConsoleTitleW(title)

    def loadNames(self):
        self.setTitle('NameChecker.py v2 | Importing Name List')
        while True:
            try:
                print(f'{blue}{self.logo}\n\n\n')
                print(f"{blue}Load your name list...")
                sleep(0.3)
                loader = open(fileopenbox(title="Load Name List", default="*.txt"), 'r', encoding="utf8", errors='ignore').read().split('\n')
                self.namelist = list(set(x.strip() for x in loader if x != ''))
                if len(self.namelist) == 0:
                    print(f'{red}No names found!\n')
                    continue
                print(f"{green} > Loaded {len(self.namelist)} names")
                sleep(2)
                break
            except:
                exit()
        self.namelistsize = len(self.namelist)
        if self.threads > self.namelistsize:
            print(f'{yellow}[i] Your # of threads is larger than your name list, fixing!')
            self.threads = self.namelistsize

    def generateNames(self):
        self.setTitle('NameChecker.py v2 | Generating Name List')
        clear()
        def genName(length):
            return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
        print(f'{blue}{self.logo}\n\n\n')
        namesToGen = int(input('Names to Generate?: '))
        nameLength = int(input('Name Length?: '))
        clear()
        print(f'{blue}{self.logo}\n\n\n')
        print(f'{blue}Generating {namesToGen} names...')
        tempNameList = []
        while len(tempNameList) <= namesToGen:
            name = genName(nameLength)
            if name not in tempNameList:
                tempNameList.append(name)
        print(f'{green} > Done!')
        sleep(2)
        self.namelist = tempNameList
        self.namelistsize = len(self.namelist)
        clear()

    def loadNameMenu(self):
        self.setTitle('NameChecker.py v2 | Idle')
        choice = 0
        while choice == 0:
            clear()
            print(f'{blue}{self.logo}\n\n\n')
            print(f'{blue}[1] Load names from file')
            print(f'{blue}[2] Generate random names')
            x = int(input('>'))
            if x == 1:
                clear()
                self.loadNames()
                break
            elif x == 2:
                clear()
                self.generateNames()
                break
            else:
                clear()
                print(f'{red}{self.logo}\n\n\n')
                print(f'{red} > Invalid Choice, please try again.')
                sleep(3)
        clear()

    def title(self):
        while self.isRunning:
            if Stats.checked < (self.namelistsize - (int(round(self.threads)) / 4)):
                perc = self.percentage(Stats.checked, self.namelistsize)
                timeNow = timer()
                runTime = self.convertSec(timeNow - self.startTime)
                windll.kernel32.SetConsoleTitleW(
                    f'NameChecker.py v2 @ {self.threads} threads | [{perc}%] ({Stats.checked} / {self.namelistsize})'
                    #f' | [{Stats.checked} / {self.namelistsize}'
                    f' | CPM: {Stats.cpm}'
                    f' | Open: {Stats.good}'
                    f' | Upcoming: {Stats.upcoming}'
                    f' | Claimed: {Stats.bad}'
                    f' | Blocked: {Stats.blocked}'
                    f' | Errors: {Stats.error}'
                    f' | Proxies: {len(self.proxylist)}'
                    f' | {runTime} Elapsed'
                    )
            else:
                timeNow = timer()
                runTime = self.convertSec(timeNow - self.startTime)
                windll.kernel32.SetConsoleTitleW(
                    f'NameChecker.py v2'
                    f' | ({Stats.checked} / {self.namelistsize})'
                    f' | Waiting for threads to finish...'
                    f' | {runTime} Elapsed'
                )

    def checkName(self, name):
        nameInfo = Name
        nurl = f'{checkUrl}{name}'
        rcode = 0
        rjson = ''
        proxy = random.choice(self.proxylist)
        broxy = self.formatProxy(proxy)
        try:
            r = requests.get(url=nurl, proxies=broxy, timeout=5)
            rcode = r.status_code
            rjson = json.loads(r.text)
        except:
            #self.safePrint(e)
            if len(self.proxylist) >= 1001:
                try:
                    self.proxylist.remove(proxy)
                except:
                    None
            nameInfo.status = 'retry'
            return nameInfo
        if rcode == 429:
            sleep(10)
            nameInfo.status = 'retry'
            return nameInfo
        if rcode != 200:
            nameInfo.status = 'retry'
            return nameInfo
        try:
            status = rjson['status']
        except:
            nameInfo.status = 'retry'
            return nameInfo
        if status == 'available':
            nameInfo.status = 'Open'
            return nameInfo
        elif status == 'blocked':
            nameInfo.status = 'Blocked'
            return nameInfo
        elif status == 'soon':
            nameInfo.status = 'Upcoming'
            nameInfo.droptime = rjson['drop_time']
            return nameInfo
        elif status == 'taken':
            nameInfo.status = 'taken'
            return nameInfo
        else:
            nameInfo.status = 'retry'
            return nameInfo
    
    def checkNames(self, name):
        nameStatus = 'retry'
        nameInfo = None
        while nameStatus == 'retry':
            nameInfo = self.checkName(name)
            nameStatus = nameInfo.status
            Stats.error += 1
        Stats.checked += 1
        if nameInfo.status == 'Open':
            self.safePrint(f'{green}[Open] {name}')
            Results.good.append(name)
            Stats.good += 1
        elif nameInfo == 'Blocked':
            self.safePrint(f'{red}[Blocked] {name}')
            Stats.blocked += 1
        elif nameInfo == 'Upcoming':
            self.safePrint(f'{yellow}[Upcoming] {name}')
            Stats.upcoming += 1
        else:
            Stats.bad += 1

if __name__ == '__main__':
    init()
    clear = lambda: os.system('cls')
    blue = Fore.LIGHTBLUE_EX
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    yellow = Fore.LIGHTYELLOW_EX
    lock = Lock()
    session = Session()
    checkUrl = 'https://api.gapple.pw/blocked/'
    Main()