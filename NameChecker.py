import os, re, random, string
from re import S
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

class Results:
    good = []
    upcoming = []

class Main:
    def __init__(self):
        clear()
        self.version = '2.1'
        self.isRunning = False
        self.proxylist = []
        self.namelist = []
        self.namelistsize = 0
        self.startTime = 0
        self.endTime = 0
        self.saveUpcoming = True
        self.printUpcoming = True
        self.printBad = False #slows the checker down
        self.threads = 85
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
                                       ░                       ░                                 ░           ░ ░                                                                                                                 
"""
        self.prep()
        self.initiate()
        exit()

    def prep(self):
        clear()
        self.setTitle('NameChecker.py v2 | [Coded by NotGhostTypes#0872]')
        print(f'{blue}{self.logo}\n\n\nLoading...')
        self.loadProxy()
        self.checkForUpdate()
        sleep(1.4)
        self.loadNameMenu()
        self.isRunning = True
    
    def initiate(self):
        clear()
        self.setTitle(f'NameChecker.py v2 | [Starting {self.threads} threads]')
        print(f'{blue}{self.logo}\n\n\n')
        print(f'{blue} > Starting {self.threads} threads...')
        mainpool = ThreadPool(processes=self.threads)
        Thread(target=self.cpmCounter, daemon=True).start()
        Thread(target=self.title).start()
        clear()
        self.startTime = timer()
        mainpool.imap_unordered(func=self.checkName, iterable=self.namelist)
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

    def checkForUpdate(self):
        latestVer = self.version
        try:
            reply = requests.get(url='https://raw.githubusercontent.com/GhostTypes/MC-NameChecker/main/version.txt', timeout=5)
            latestVer = str(reply.text)
        except:
            print(f'{yellow}[/] Failed to check latest version!')
            sleep(2.3)
        if f'{self.version}\n' != latestVer:
            print(f'{yellow}[/] There\'s an update ready! Your version: {self.version} | Latest Release: {latestVer}')
            print(f'{yellow}Get the latest version from the Github: https://github.com/GhostTypes/MC-NameChecker')
            sleep(5)
        clear()

    def loadNameMenu(self):
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

    def title(self):
        while self.isRunning:
            if Stats.checked < (self.namelistsize - (int(round(self.threads)) / 4)):
                perc = self.percentage(Stats.checked, self.namelistsize)
                timeNow = timer()
                runTime = self.convertSec(timeNow - self.startTime)
                windll.kernel32.SetConsoleTitleW(
                    f'NameChecker.py v2 @ {self.threads} threads | [{perc}%] ({Stats.checked} / {self.namelistsize}'
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

    def loadNames(self):
        self.setTitle('NameChecker.py v2 (Loading Name List)')
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

    def generateNames(self):
        self.setTitle('NameChecker.py v2 (Generating Name List)')
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

    def safePrint(self, line):
        lock.acquire()
        print(line)
        lock.release()

    def loadProxy(self):
        #if self.isDebug:
            #print(f'{yellow}[Debug] Requesting Proxies...')
        loader = requests.get('https://www.proxyscan.io/download?type=socks4').text.split('\n')
        #if self.isDebug:
            #print(f'{yellow}[Debug] Request returned {len(loader)} proxies, sorting.')
        self.proxylist = list(set([x.strip() for x in loader if ":" in x and x != '']))
        #if self.isDebug:
            #print(f'{yellow}[Debug] Proxylist size after sorting: {len(self.proxylist)}')
            #print(f'{yellow}[Debug] Sleeping for 5 seconds')
            #sleep(5)
    
    def formatProxy(self, proxy):
        return {'http': f"socks4://{proxy}", 'https': f"socks4://{proxy}"}

    def getUserAgent(self):
        return {'User-Agent':str(checkerAgent.random)}

    def isBlocked(self, name):
        status = 0
        nameUrl = f'{mcUrl}{name}'
        while status == 0:
            proxy = choice(self.proxylist)
            broxy = self.formatProxy(proxy)
            userAgent = self.getUserAgent()
            try:
                reply = requests.get(url=nameUrl, headers=userAgent, proxies=broxy, timeout=4)
                if reply.text == 'AVAILABLE':
                    status = False
                    break
                elif reply.text == 'TAKEN':
                    status = True
                    break
                else:
                    status = 0
                    Stats.error += 1
            except:
                Stats.error += 1
                if len(self.proxylist) >= 1001:
                    try:
                        self.proxylist.remove(proxy)
                    except:
                        None
        return status
    
    def getNameStatus(self, name):
        status = 0
        nameUrl = f'{nameMCurl}{name}'
        desc = ''
        cap = ''
        ntype = 0 #1 = Open | 2 = Dropping | 3 = Claimed/Blocked
        while status == 0:
            proxy = choice(self.proxylist)
            broxy = self.formatProxy(proxy)
            userAgent = self.getUserAgent()
            try:
                reply = requests.get(url=nameUrl, headers=userAgent, proxies=broxy, timeout=4)
                if reply.status_code == 200:
                    b = BeautifulSoup(reply.text, features='html.parser')
                    desc = str(b.find(attrs={"name": re.compile(r'description', re.I)}))
                    break
                elif reply.status_code == 429:
                    sleep(10)
                    status = 0
                    Stats.error += 1
                else:
                    status = 0
                    Stats.error += 1
            except:
                Stats.error += 1
                if len(self.proxylist) >= 1001:
                    try:
                        self.proxylist.remove(proxy)
                    except:
                        None
        try:
            searches = str(desc.split("Searches: ")[1].split("/")[0].replace(" ", ""))
        except:
            searches = 'Error'
        if "Available*" in desc and "Time of" not in desc:
            if not self.isBlocked(name):
                ntype = 1
                cap = f'[/] {name} is claimable, and has {searches} searches'
            else:
                ntype = 3
                cap = f'[~] {name} is blocked, and has {searches} searches'
        elif "Time of" in desc and "Unavailable" not in desc:
            try:
                dS = desc.split(",")[0].split('"')[1].split(' ')[3].split('T')
            except:
                dS = 'Err'
            if dS != 'Err':
                dropTime = f'{dS[0]} / {dS[1]}'
            else:
                dropTime = 'Error'
            ntype = 2
            cap = f'[#] {name} will be available at {dropTime}'
        else:
            cap = ''
            ntype = 3
        return [ntype, cap]
    
    def checkName(self, name):
        nameStatus = self.getNameStatus(name)
        nameType = nameStatus[0]
        nameCap = nameStatus[1]
        if nameType == 1:
            Stats.good += 1
            Results.good.append(nameCap)
            self.safePrint(f'{green}{nameCap}')
        elif nameType == 2:
            Stats.upcoming += 1
            Results.upcoming.append(nameCap)
            self.safePrint(f'{yellow}{nameCap}')
        else:
            Stats.bad += 1
            if 'blocked' in nameCap:
                self.safePrint(f'{red}{nameCap}')
                Stats.blocked += 1
            if self.printBad:
                self.safePrint(f'{red}[X] {name} is claimed')
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
    nameMCurl = 'https://namemc.com/search?q='
    mcUrl = 'https://account.mojang.com/available/minecraft/'
    Main()