import requests, string, random, time, json, os, re, easygui
from bs4 import BeautifulSoup
from colorama import init
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore, Back, Style
from ctypes import windll
clear = lambda: os.system('cls')
clear()
init(autoreset=True)

#Init
windll.kernel32.SetConsoleTitleW(f'NameChecker by NotGhostTypes#0872')
green = Fore.LIGHTGREEN_EX
red = Fore.LIGHTRED_EX
blue = Fore.LIGHTBLUE_EX
print(f'{green}Name Checker starting...')
proxyList = requests.get('https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=4000&country=all&ssl=all&anonymity=all').text.splitlines()
print(f'{green}Scraped {len(proxyList)} proxies.')
goodAccounts = []
badAccounts = []
upcomingAccounts = []
time.sleep(2)
clear()

def getProxy():
    proxy = random.choice(proxyList)
    line = f"socks4://{proxy}"
    proxy_form = {'http': line, 'https': line}
    return proxy, proxy_form

def genNames(min, max, total):
    nameList = []
    dict = string.ascii_letters + string.digits
    while len(nameList) < total:
        n = ''.join((random.choice(dict) for i in range(random.randint(min, max))))
        if n not in nameList:
            nameList.append(n)
    return nameList

def saveList(list, outPath): #Save list to file
    with open(outPath, 'w') as f:
        f.write("\n".join(str(item) for item in list))
    return


choice = "invalid"
while choice == "invalid":
    print(f'{blue}NameChecker by NotGhostTypes#0872')
    print(f'{blue}[1] Generate Names')
    print(f'{blue}[2] Load Names from File')
    print(f'{red}[3] Exit')
    x = input()
    if "1" in x:
        print(f'{blue}Min Username Length?')
        minLen = int(input())
        print(f'{blue}Max Username Length?')
        maxLen = int(input())
        print(f'{blue}Total Usernames?')
        total = int(input())
        nameList = genNames(minLen, maxLen, total)
        clear()
        print(f'{green}Generated {len(nameList)} names')
        nameListSize = len(nameList)
        break
    elif "2" in x:
        nameList = open(easygui.fileopenbox(title="Load Name List", default="*.txt"), 'r').read().splitlines()
        nameListSize = len(nameList)
        os.system('cls')
        print(f'{green}Loaded {len(nameList)} names from file')
        break
    elif "3" in x:
        clear()
        print(f'{red}See you next time!')
        exit()
    else:
        choice == "invalid"
        print(f'{Fore.LIGHTRED_EX}Invalid choice. Please try again.')
        time.sleep(3)

def checkName(name):
    checked = len(badAccounts) + len(goodAccounts)
    windll.kernel32.SetConsoleTitleW(f'NameChecker by NotGhostTypes#0872 | Checked: [{checked} / {nameListSize}] | Good: {len(goodAccounts)} | Bad: {len(badAccounts)} | Upcoming: {len(upcomingAccounts)}')
    validRequest = False
    retries = 0
    while not validRequest:
        proxy = getProxy()
        try:
            r = requests.get(url=f'https://namemc.com/search?q={name}', proxies=proxy[1], timeout=3)
            if r.status_code == 200:
                validRequest = True
        except:
            if len(proxyList) >= 1000:
                try:
                    proxyList.remove(proxy[0])
                except:
                    None
    del proxy
    b = BeautifulSoup(r.text, features='html.parser')
    d = str(b.find(attrs={"name": re.compile(r'description', re.I)}))
    try:
        searches = str(d.split("Searches: ")[1].split("/")[0].replace(" ", ""))
    except:
        searches = "Err"
    if "Available*" in d and "Time of" not in d:
        if int(searches) > 100:
            print(f'{red}[BLOCKED] {name} | Searches: {searches}')
            badAccounts.append(name)
        else:
            print(f'{green}[OPEN] {name}')
            goodAccounts.append(f'{name} | Searches: {searches}')
    elif "Time of" in d and "Unavailable" not in d:
        try:
            dt = d.split(",")[0].split('"')[1].split(' ')[3].split('T')
        except:
            dt = "Err"
        print(f'{red}[DROPPING] {name} AT {dt[0]} | {dt[1]}')
        upcomingAccounts.append(f'{name} opens at {dt}| Searches: {searches}')
    else:
        badAccounts.append(name)

time.sleep(2)
clear()
print(f'{Fore.LIGHTCYAN_EX}Threads?')
threads = int(input())
print(f'{green}Starting threads...')
pool = ThreadPool(threads)
clear()
results = pool.map(checkName, nameList)
pool.close()
pool.join()
print(f'{green}Checker finished.')
if len(goodAccounts) >= 1:
    saveList(goodAccounts, 'open_names.txt')
if len(upcomingAccounts) >= 1:
    saveList(upcomingAccounts, 'upcoming_names.txt')