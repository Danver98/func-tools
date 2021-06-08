import requests , csv , time , lxml , os , random , team , re , pandas , my_score_parser as parser
from bs4 import BeautifulSoup
from selenium import webdriver
from random import choice
from team import Team
from match import Match
from basketball_match import BasketballMatch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException  
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime,date

PATH = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/"
def set_cookies(driver,cookies = None):
    if not cookies:
        driver.add_cookie({'name':'i','value':'z9cTUk2pJF1ELxlFkgS7OUljv6GfEakChCdVzkInkE7woJaVzDQIw9tJ8a2mB+XmuSEppDXBj1a0TufsIcKv90ncpBY='})
        driver.add_cookie({'name':'yp','value':'1847620823.yrtsi.1532260823#1565370567.zmblt.887'})
        driver.add_cookie({'name':'yandexuid','value':'2748174861532260806'})
        driver.add_cookie({'name':'my','value':'YwA='})
        driver.add_cookie({'name':'_ym_uid','value':'1532290188218230031'})
        driver.add_cookie({'name':'_ym_d','value':'1532290188'})
        driver.add_cookie({'name':'mda','value':'0'})
        driver.add_cookie({'name':'fuid01','value':'5b6c751e4564443a.4wqvqhuh3OxmGHHBX5jHkxeZ_HMlIClXCPXE-N09Dj_uk-36u-CvPv_8dL1T6_SiYatDtwW6-jiVv3vkENp3bzyys1OHKz3FMQHGz342l9TFGEb3Sb4UVJHPIhvXOCL9'})
        #driver.add_cookie({'name':'_ym_wasSynced','value':{"time":1533888293264,"params":{"webvisor":{"date":"2011-10-31 16:20:50"},"eu":0},"bkParams":{}}})
        driver.add_cookie({'name':'_ym_isad','value':'2'})
    else:
        for cookie in cookies:
            driver.add_cookie(cookie)

def set_profile(useragent,proxy,cache = False): 
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override",useragent)
    profile.set_preference("network.proxy.type",1)
    profile.set_preference("network.proxy.http",proxy[0])
    profile.set_preference("network.proxy.http_port",int(proxy[1]))
    if not cache:
        profile.set_preference("browser.cache.disc.enable",False)
        profile.set_preference("browser.cache.memory.enable",False)
        profile.set_preference("browser.cache.offline.enable",False)
        profile.set_preference("network.http.use-cache",False)
    profile.update_preferences()
    return profile

def set_time(duration):
    if (duration is None) or (duration == 0):
        return "00:00:00"
    minutes = duration // 60
    seconds = duration % 60
    if minutes < 10:
        minutes = f"0{minutes}"
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"00:{minutes}:{seconds}"

def write_songs():
    songs = []
    genres = [1,2,3,4,5,6]
    devices = [num for num in range(1,61)]
    #styles = ["","","","","","","",""]
    song_temps = ["quick","slow","energetic","calm"]
    languages = ["russian","english","spanish","french","arabic","italian"]
    file_name= PATH + "songs.csv"
    csv_file = open(file_name,'a',newline='',encoding ='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(('SongID','SongName','GenreID','Duration','DeviceID','Rating','Style','SongTemp','Language','TextAuthor','ReleaseYear'))
    for i in range(0,100):
        song_id= i+1
        song_name = f"Song-{random.randint(1,60)}" 
        genre_id =choice(genres)
        duration = set_time(random.randint(90,330))
        device_id = choice(devices)
        rating = random.randint(1,10)
        style = "-"
        song_temp = choice(song_temps)
        language =choice(languages)
        text_author = f"author-{random.randint(1,70)}"
        year = random.randint(1975,2018)
        month = random.randint(1,12)
        if month == 2:
            if ((year % 4 ==0) and (year % 100 !=0)):
                day = random.randint(1,29)
            else:
                day = random.randint(1,28)
        elif (month % 2 == 0):
            day =  random.randint(1,30)
        elif month == 7:
            day =  random.randint(1,31)
        else:
            day =  random.randint(1,31)
        if day < 10:
            day = f"0{day}"
        release_year = f"{year}-{month}-{day}"
        songs.append(song_id)
        writer.writerow((song_id,song_name,genre_id,duration,device_id,rating,style,song_temp,language,text_author,release_year))
    return songs

def write_artists():
    artists = []
    names = ["John","Steve","Alex","Michelle","Juliano","Robert","Ciara","Ali","Julia","Maria","Alexandr","Nolah","Ivan","Dmitriy","Sergio","Alfredo","Riccardo","Petro","Vanek","Tomash","Kurt","Yonas","Olli","Anna","Dudek","Dunk","Molly","Oscar","Lens","Georgio","Luka","Leonard","David","Celine","Mark","Octopus","Jeremy","Dora","Selena","Clara","Fred","Margo","Magda","Silvia","Nikola","Brandon","Zak","Chak","Michael","Glen","Calvin","August","Lily","Eva","Clermon","Mehdi","Qui","Sao","Will"]
    surnames = ["Snow","Bread","Gonsalez","Boligro","Harris","Olofson","Peterson","Gomez","Clear","Rompero","Wilson","Auga","Ferz","Zetterberg","Malcan","Fiala","Glutz","Ferero","Ing","Young","Sui Lon","Dzuki","Halla","Egnardson","Lipson","Eager","Cleverman","Wetland","Moris-Spivakovsky","Agnez","Frolini","Agostini","Laporollo","Bork","Lime","Orio","Tatcher","Odd","Bones","Krajac","Slavutic","Otcenash","Johnson","Magnusson","Lee","Laser","Nickson","Raider","Plazo","Sane","Giroux","Grid","Patana","Sundin","Unviar","Hley","Vital","Comma","Dotter","Jee Sun","Abrams","Elias", "Quinter"]
    file_name= PATH + "artists.csv"
    csv_file = open(file_name,'a',newline='',encoding ='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(('ArtistID','ArtistName','ArtistSurname','DateBirth','DateDeath','Age','ArtistInfo'))
    for i in range(0,50):
        cid = i+1
        name = choice(names)
        surname = choice(surnames)
        year = random.randint(1950,2000)
        month = random.randint(1,12)
        day = 0
        if month == 2:
            if ((year % 4 ==0) and (year % 100 !=0)):
                day = random.randint(1,29)
                sday = day
            else:
                day = random.randint(1,28)
        elif (month % 2 == 0):
            day =  random.randint(1,30)   
        elif month == 7:
            day =  random.randint(1,31)          
        else:
            day =  random.randint(1,31)           
        if day < 10:
            day = f"0{day}"
        birth = "{}-{}-{}".format(year,month,day)
        death = "\\N"
        today = date.today()
        age = today.year - year
        if ((today.month < month) or ((today.month==month) and (today.day < int(day)))):
            age-=1          
        text = "This is artist %s %s" % (name,surname)    
        artists.append(cid)
        writer.writerow((cid,name,surname,birth,death,age,text))
    return artists

def write_composers():
    composers = []
    names = ["John","Steve","Alex","Michelle","Juliano","Robert","Ciara","Ali","Julia","Maria","Alexandr","Nolah","Ivan","Dmitriy","Sergio","Alfredo","Riccardo","Petro","Vanek","Tomash","Kurt","Yonas","Olli","Anna","Dudek","Dunk","Molly","Oscar","Lens","Georgio","Luka","Leonard"]
    surnames = ["Snow","Bread","Gonsalez","Castro","Liquid","Range","Semyonov","Lucido","Al-Khanu","Weird","Gunzlauter","Martins","Paloli","Foltinen","Palola","Petrov","Versus","Ad-hoc","Lavander","Blanco","Tranquila","Jovetic","Savinic","Belykh","Milocido","Creaming"]
    file_name= PATH + "composers.csv"
    csv_file = open(file_name,'a',newline='',encoding ='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(('ComposerID','ComposerName','ComposerSurname','ComposerInfo'))
    for i in range(0,30):
        cid = i+1
        name = choice(names)
        surname = choice(surnames)
        text = "This is composer %s %s" % (name,surname)  
        composers.append(cid)  
        writer.writerow((cid,name,surname,text))
    return composers 

def write_devices():
    types = ["Casset", "CD", "Record", "USB"]
    file_name = PATH +"devices.csv"
    csv_file = open(file_name,'a',newline='',encoding ='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(('DeviceID','DeviceType','DeviceCapacity','DeviceInfo'))
    for i in range (0,60):
        did = i+1
        dtype = choice(types)
        if dtype == "Casset":
            capacity = random.randint(50,100)
        if dtype == "Record":
            capacity = random.randint(6,20)
        if dtype =="CD":
            capacity = random.randint(100,500)
        else:
            capacity = random.randint(400,1000)
        text = "This is %s numbered %d" % (dtype,did)
        writer.writerow((did,dtype,capacity,text))

def songs_and_artists(songs,artists):
    file_name = PATH + "songs_and_artists.csv"
    csv_file = open(file_name, 'a',newline = '',encoding='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(("SongID","ArtistID"))
    a_chosen = []
    for artist in artists:
        a_chosen.append({artist:0})

    for song in songs:
        r = random.randint(1,20)
        if ((r % 5 ==0 )and (r % 10 !=0)):
            amount = 2
        elif ( r % 10 == 0):
            amount = 3
        else:
            amount = 1
        a_for_song = []
        n = 0
        while n < amount:
            while True:        
                artist = choice(artists)
                i=0
                for index,a in enumerate(a_chosen):
                    if a.get(artist)!= None:
                        i = index
                        break
                if ((artist in a_for_song) or (a_chosen[i][artist] > 5)):    # как?
                    continue
                a_chosen[i][artist]+=1
                a_for_song.append(artist)
                break
            writer.writerow((song,artist))
            n+=1
        a_for_song.clear()

def songs_and_composers(songs , composers):
    file_name = PATH + "songs_and_composers.csv"
    csv_file = open(file_name, 'a',newline = '',encoding='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(("SongID","ComposerID"))
    c_chosen = []
    for composer in composers:
        c_chosen.append({composer:0})

    for song in songs:
        r = random.randint(1,20)
        if ((r % 5 ==0 )and (r % 10 !=0)):
            amount = 2
        elif ( r % 10 == 0):
            amount = 3
        else:
            amount = 1
        c_for_song = []
        n = 0
        while n < amount:
            while True:        
                composer = choice(composers)
                i=0
                for index,c in enumerate(c_chosen):
                    if c.get(composer)!= None:
                        i = index
                        break
                if ((composer in c_for_song) or (c_chosen[i][composer] > 5)):    # как?
                    continue
                c_chosen[i][composer]+=1
                c_for_song.append(composer)
                break
            writer.writerow((song,composer))
            n+=1
        c_for_song.clear()


if __name__ =='__main__':
    x1,x2,x3,x4 = 0,0,0,0
    i=10
    for r in range(0,100):
        i*=10
        x1,x2,x3,x4 = i,i,i,i
        print(3*(x2**2) - 11*x1 -3*x2 - x3)
        print("\n")
    #a = [21,3,20]
    #doit(a)
    
    """
    while True:
        try:
            useragents = open('data/agents2','r',encoding='utf-8').read().split('\n')
            proxies = open('data/proxies','r',encoding='utf-8').read().split('\n')
            useragent = choice(useragents)
            proxy = choice(proxies).split(':')
            print(f"Proxy: IP: {proxy[0]} , port: {int(proxy[1])} , Useragent: {useragent} ")
            options = webdriver.firefox.options.Options()
            options.set_headless(headless = True)
            profile = set_profile(useragent,proxy)
            #,firefox_options = options
            print("Pre-launch operations completed...")
            driver = webdriver.Firefox(firefox_profile = profile,firefox_options = options)
            driver.get('https://yandex.ru/internet/')
            set_cookies(driver)           
            driver.get('https://hidemyna.me/ru/proxy-list/')          
            driver.quit()    
        except OSError:
            print("Waiting...")
            continue
        else:
            break
    """ 
    #songs = write_songs()
    #artists = write_artists()
    #songs_and_artists(songs,artists)
    #composers = write_composers()
    #songs_and_composers(songs,composers)
    #write_devices()