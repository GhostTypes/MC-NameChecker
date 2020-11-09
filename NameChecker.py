import os, re
from time import sleep
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore, init
from ctypes import windll
import requests
from requests import Session
from random import choice
from threading import Thread, Lock
from easygui import fileopenbox

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

class Main:
    def __init__(self):
        self.isRunning = True
        self.proxylist = []
        self.namelist = []
        self.namelistsize = 0
        self.loadProxy()
        self.loadNames()
        Thread(target=self.cpmCounter, daemon=True).start()
        self.initiate()
        self.saveHits()
        exit()

    def initiate(self):
        clear()
        mainpool = ThreadPool(processes=int(input('Threads?: ')))
        Thread(target=self.title).start()
        clear()
        mainpool.imap_unordered(func=self.checkName, iterable=self.namelist)
        mainpool.close()
        mainpool.join()
        self.isRunning = False
        clear()
        print(f'{blue}Hits: {Stats.good}\nUpcoming: {Stats.upcoming}\nBad: {Stats.bad}')

    def title(self):
        while self.isRunning:
            windll.kernel32.SetConsoleTitleW(
                f'NameChecker by NotGhostTypes#0872'
                f' | [{Stats.checked} / {self.namelistsize}'
                f' | Hits: {Stats.good}'
                f' | Upcoming: {Stats.upcoming}'
                f' | Error: {Stats.error}'
                f' | Bad: {Stats.bad}'
                f' | Blocked: {Stats.blocked}'
                f' | CPM: {Stats.cpm}'
                f' | Proxies: {len(self.proxylist)}'
            )

    def loadNames(self):
        while True:
            try:
                print(f"{blue}Load your name list...")
                sleep(0.3)
                loader = open(fileopenbox(title="Load Name List", default="*.txt"), 'r', encoding="utf8", errors='ignore').read().split('\n')
                self.namelist = list(set(x.strip() for x in loader if x != ''))
                if len(self.namelist) == 0:
                    print(f'{red}No names found!\n')
                    continue
                print(f"Imported {len(self.namelist)} lines")
                break
            except:
                exit()
        self.namelistsize = len(self.namelist)

    def cpmCounter(self):
        while self.isRunning:
            if Stats.checked >= 1:
                now = Stats.checked
                sleep(3)
                Stats.cpm = (Stats.checked - now) * 20

    def prints(self, line):
        lock.acquire()
        print(line)
        lock.release()

    def loadProxy(self):
        loader = requests.get('https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all').text.split('\n')
        self.proxylist = list(set([x.strip() for x in loader if ":" in x and x != '']))

    def formatProxy(self, proxy):
        return {'http': f"socks4://{proxy}", 'https': f"socks4://{proxy}"}

    def checkName(self, name):
        validRequest = False
        while not validRequest:
            proxy = choice(self.proxylist)
            broxy = self.formatProxy(proxy)
            try:
                r = requests.get(url=f'{nameUrl}{name}', proxies=broxy, timeout=3)
                if r.status_code == 200:
                        break
            except:
                if len(self.proxylist) >= 1000:
                    try:
                        self.proxylist.remove(proxy)
                    except:
                        None
        b = BeautifulSoup(r.text, features='html.parser')
        d = str(b.find(attrs={"name": re.compile(r'description', re.I)}))
        try:
            searches = str(d.split("Searches: ")[1].split("/")[0].replace(" ", ""))
        except:
            searches = "Err"
        if "Available*" in d and "Time of" not in d:
            if int(searches) < 100:
                Stats.good += 1
                Results.good.append(f'{name} | Searches: {searches}')
                self.prints(f'{green}[OPEN] {name} | {blue}Searches: {yellow}{searches}')
            else:
                Stats.blocked += 1
                self.prints(f'{red}[BLOCKED] {name} | {blue}Searches: {yellow}{searches}')
        elif "Time of" in d and "Unavailable" not in d:
            try:
                dt = d.split(",")[0].split('"')[1].split(' ')[3].split('T')
            except:
                dt = "Err"
            self.prints(f'{yellow}[DROPPING] {name} | {blue}Drop Time: {green} {dt[0]} / {dt[1]} | {blue} Searches: {yellow}{searches}')
            Stats.upcoming += 1
            Results.upcoming.append(f'{name} | {dt[0]} / {dt[1]} | Searches: {searches}')
        else:
            Stats.bad += 1
        Stats.checked += 1

    def saveHits(self):
        if Stats.good >= 1:
            with open('open_names.txt', 'w') as f:
                for name in Results.good:
                    f.write(f'{name}\n')
        if Stats.upcoming >= 1:
            with open('upcoming_names.txt', 'w') as f:
                for name in Results.upcoming:
                    f.write(f'{name}\n')


if __name__ == '__main__':
    init()
    clear = lambda: os.system('cls')
    blue = Fore.LIGHTBLUE_EX
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    yellow = Fore.LIGHTYELLOW_EX
    lock = Lock()
    session = Session()
    nameUrl = 'https://namemc.com/search?q='
    windll.kernel32.SetConsoleTitleW('NameChecker by NotGhostTypes#0872')
    Main()