import requests , csv , time , lxml , os ,sys, team , re , pandas , my_score_parser as parser
from bs4 import BeautifulSoup
from selenium import webdriver
from random import choice
from team import Team
from match import Match
from basketball_match import BasketballMatch
from hockey_match import HockeyMatch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException  
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime

PATH = "D:/Programming/Web/python-app"

def set_profile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.cache.disc.enable",False)
    profile.set_preference("browser.cache.memory.enable",False)
    profile.set_preference("browser.cache.offline.enable",False)
    profile.set_preference("network.http.use-cache",False)
    return profile

# здесь можно получить все ссылки на команды из избранных лиг
def list_of_league_teams(driver,url,league_link):
    teams = []
    driver.get(league_link + 'teams')
    div = WebDriverWait(driver,timeout=30).until(
    lambda x : x.find_element_by_id('tournament-page-participants'))
    tbody = div.find_element_by_tag_name('tbody')
    print(("\nLeague link : {}\n".format(league_link)))
    for tr in tbody.find_elements_by_tag_name('tr'):     # для каждой команды
        a = tr.find_element_by_tag_name('a')
        team_name = a.text.strip()
        link = a.get_attribute('href').strip()
        teams.append({'team':team_name , 'link':link})
        print(("team: {} , link: {}".format(team_name ,link)))
    return teams
                                                                                                           
def list_of_my_leagues(driver,url,count = 3):
    leagues = []
    #driver.get(url+'/basketball')
    WebDriverWait(driver,timeout=30).until(
    lambda x : x.find_element_by_class_name("table-main"))
    ul = driver.find_element_by_id('my-leagues-list')
    parent_window = driver.current_window_handle
    for li in ul.find_elements_by_tag_name('li')[:count]:
        league_name = li.get_attribute('title').strip()
        league_link =li.find_element_by_tag_name('a').get_attribute('href').strip()
        driver.execute_script("window.open();")
        for handle in driver.window_handles:
            if handle != parent_window:
                driver.switch_to_window(handle)
                print("SWITCHED")
                break         
        teams =list_of_league_teams(driver,url,league_link)
        driver.close()
        driver.switch_to_window(parent_window)
        leagues.append({'league':league_name , 'link':league_link, 'teams':teams})
    return leagues


def parse_basketball_match(driver,team_name):
    while True:
        try:
            WebDriverWait(driver,timeout=30).until(
            lambda x : x.find_element_by_id('parts'))
            soup = BeautifulSoup(driver.page_source,'lxml')
            table = soup.find('table',id = 'parts')
            this_team = table.find('tr',class_ ='odd')
            rival_team = table.find('tr',class_ ='even')
            place = "дом"
            self_score = []
            rival_score = []   
            #if rival_team.find('a').text.strip() == team_name:
            if re.search(team_name,rival_team.find('a').text.strip()):
                this_team ,rival_team = table.find('tr',class_ ='even') , table.find('tr',class_ ='odd')
                place = "выезд"
            date = soup.find('div',id='utime').text[:5]
            rival_name = rival_team.find('a').text.strip()
            for td in this_team.find_all('td',class_='score part')[:4]:
                self_score.append(int(td.text))
            if this_team.find('td',class_ = 'score part last').text.isdigit():  # overtime
                self_score.append(int(this_team.find('td',class_ = 'score part last').text))

            for td in rival_team.find_all('td',class_='score part')[:4]:
                rival_score.append(int(td.text))
            if rival_team.find('td',class_ = 'score part last').text.isdigit():  # overtime
                rival_score.append(int(rival_team.find('td',class_ = 'score part last').text))
    
            return BasketballMatch(date,team_name,rival_name,self_score,rival_score,place)
        except IndexError:
            driver.refresh()
            print("Index Error")
            continue
        except TimeoutException:
            driver.refresh()
            print("Timeout Error")
            continue

# образующая при парсинге результатов баскетбольной команды
def parse_basketball_team(driver,league,team_name,count = 10):
    while True:        
        try:    
            #driver.refresh()
            team = Team('basketball',league,team_name)
            match_count = 0
            flag = False
            div = WebDriverWait(driver,timeout = 30).until( lambda x : x.find_element_by_id("fs-results"))
            for tbody in div.find_elements_by_tag_name('tbody'):
                if flag == True:
                    break                    
                for tr in tbody.find_elements_by_tag_name('tr'):  # парсим каждый матч 
                    match_count+=1
                    if match_count > count:
                        flag = True
                        break
                    current_window = driver.current_window_handle
                    link= tr.get_attribute('id')
                    match_link = link[link.rfind('_') + 1 :]
                    driver.execute_script("window.open();")
                    #driver.find_element_by_tag_name('body').sendKeys(Keys.CONTROL +"t")
                    print("After opening a new window")
                    for handle in driver.window_handles:
                        if handle != current_window:
                            driver.switch_to_window(handle)
                            break
                    driver.get(url +'/match/' + match_link + '/#match-summary')          
                    team.matches.append(parse_basketball_match(driver,team_name))
                    driver.close()
                    driver.switch_to_window(current_window) 
            return team

        except TimeoutException:
            driver.refresh()
            print("Timeout Error")
            continue
# здесь написать парсинг матчей команды + запись в файл
def parse_basketball_teams_list(_list):
    pass


############################################################################
def parse_hockey_match(driver,team_name):
    while True:
        try:        
            WebDriverWait(driver,timeout=30).until(
            lambda x : x.find_element_by_id('summary-content'))   
            soup = BeautifulSoup(driver.page_source,'lxml')
            date = soup.find('div',id='utime').text[:5]
            div = soup.find('div',id = 'summary-content')  
            host_name = soup.find('div',class_='tname-home').a.text.strip()
            rival_name = soup.find('div',class_='tname-away').a.text.strip()
            self_score = []
            rival_score = []
            place = "дом"
    
            WebDriverWait(driver,timeout=30).until(
            lambda x : x.find_element_by_class_name('detailMS'))
            
            for header in div.find_all('div',class_ = 'detailMS__incidentsHeader'):
                self_score.append(int(header.find('span',class_=re.compile('home')).text))
                rival_score.append(int(header.find('span',class_=re.compile('away')).text))
            #if rival_team.find('a').text.strip() == team_name:
            if re.search(team_name,rival_name):
                rival_name = host_name
                self_score , rival_score = rival_score , self_score
                place = "выезд"
            print("Rival: " + rival_name)   
            return HockeyMatch(date,team_name,rival_name,self_score,rival_score,place)
        
        except IndexError:
            driver.refresh()
            print("Index Error")
            continue
        except TimeoutException:
            driver.refresh()
            print("Timeout Error")
            continue

def parse_hockey_team(driver,league,team_name,count = 3):
    while True:
        try:        
            #driver.refresh()
            team = Team('hockey',league,team_name)
            print("Now parsing " + team_name)
            match_count = 0
            flag = False
            div = WebDriverWait(driver,timeout = 30).until( lambda x : x.find_element_by_id("fs-results"))
            for tbody in div.find_elements_by_tag_name('tbody'):
                if flag == True:
                    break                    
                for tr in tbody.find_elements_by_tag_name('tr'):  # парсим каждый матч 
                    match_count+=1
                    if match_count > count:
                        flag = True
                        break
                    current_window = driver.current_window_handle
                    link= tr.get_attribute('id')
                    match_link = link[link.rfind('_') + 1 :]
                    driver.execute_script("window.open();")
                    for handle in driver.window_handles:
                        if handle != current_window:
                            driver.switch_to_window(handle)
                            break
                    driver.get(url +'/match/' + match_link + '/#match-summary')
                    team.matches.append(parse_hockey_match(driver,team_name))
                    driver.close()
                    driver.switch_to_window(current_window) 
            return team

        except TimeoutException:
            driver.refresh()
            print("Timeout Error")
            continue

############################################################################
def parse_football_match(tr,team_name):
    place = "дом"
    date = tr.find('td', class_ = 'time').text.split()[0]
    team_self = tr.find('td',class_ = 'team-home').text
    team_rival = tr.find('td',class_ = 'team-away').text
    td_score = tr.find('td',class_ = 'score')
    if len(td_score.contents) > 1:   # если есть доп время или пендали
        self_score = int(td_score.contents[0].split(':')[0].strip())
        rival_score = int(td_score.contents[0].split(':')[1].strip())
        aet = td_score.find('span',class_ = 'aet').text.strip()
        pat = re.compile("^\((.+)\)$")
        sc = pat.search(aet).group(1).strip().split(':')
        maintime = {'home-score': int(sc[0].strip()), 'guest-score':int(sc[1].strip())}
    else:
        self_score = int(tr.find('td',class_ = 'score').text.split(':')[0].strip())
        rival_score = int(tr.find('td',class_ = 'score').text.split(':')[1].strip())
        maintime = None
    if re.search(team_name,team_rival):
        team_rival = team_self 
        self_score , rival_score  = rival_score , self_score
        if maintime:       
            maintime['home-score'], maintime['guest-score'] = maintime['guest-score'] , maintime['home-score']
        place = "выезд"    
    return Match(date,team_name,team_rival,self_score,rival_score,place,maintime)

def parse_football_team(driver,league_name,team_name,count = 15,sports = "football"):
    # добавить refresh() ,если долго грузит
    team = Team(sports,league_name,team_name)
    WebDriverWait(driver,timeout = 30).until( lambda x : x.find_element_by_id("fs-results"))
    soup = BeautifulSoup(driver.page_source , 'lxml')
    div = soup.find('div' , id='fs-results')
    flag = False
    match_count = 0
    for tbody in div.find_all("tbody"):
        if flag ==True:
            break
        for tr in tbody.find_all("tr"):
            match_count+=1
            if match_count > count:
                flag = True
                break
            team.matches.append(parse_football_match(tr,team_name))
    return team

############################################################################
def write_team(writer,team,sports="football"):
    if sports == "football":
        for match in team.matches:
            writer.writerow((team.sport,team.league,team.name, match.rival , match.date ,match.result(), match.match_score(),match.odd_even() , match.total(), match.score, match.ind_odd_even(),'-','-',match.place, match.overtime()))
        writer.writerow((" "," "," "," "," "," "," "," ",-0.1,-0.1," "," "," "," "," "))
        writer.writerow((" "," "," "," "," "," "," "," ",-0.1,-0.1," "," "," "," "," "))
    else:
        if sports =="basketball":  # проверить
            for match in team.matches:
                writer.writerow((team.sport,team.league,team.name, match.rival , match.date ,match.result(), match.match_score(),match.odd_even() , match.total(), match.score, match.ind_odd_even(),'-','-',match.quarter_total(1),match.quarter_odd_even(1),match.quarters[0],match.ind_quarter_odd_even(1),'-','-',match.quarter_total(2),match.quarter_odd_even(2),match.quarters[1],match.ind_quarter_odd_even(2),'-','-',match.half_total(1),match.half_odd_even(1),match.ind_half_total(1),match.ind_half_odd_even(1),'-','-',match.quarter_total(3),match.quarter_odd_even(3),match.quarters[2],match.ind_quarter_odd_even(3),'-','-',match.quarter_total(4),match.quarter_odd_even(4),match.quarters[3],match.ind_quarter_odd_even(3),'-','-',match.half_total(2),match.half_odd_even(2),match.ind_half_total(2),match.ind_half_odd_even(2),'-','-',match.first_greater_second(),match.ind_first_greater_second(),match.place, match.overtime()))
            writer.writerow((" "," "," "," "," "," "," "," ",-0.1,-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," "," "," "," "," "))
            writer.writerow((" "," "," "," "," "," "," "," ",-0.1,-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," "," "," "," "," "))
        elif sports == "hockey":
            for match in team.matches:
                writer.writerow((team.sport,team.league,team.name, match.rival , match.date ,match.result(), match.match_score(),match.odd_even() , match.total(), match.score, match.ind_odd_even(),'-','-',match.period_total(1),match.period_odd_even(1),match.periods[0],match.ind_period_odd_even(1),'-','-',match.period_total(2),match.period_odd_even(2),match.periods[1],match.ind_period_odd_even(2),'-','-',match.period_total(3),match.period_odd_even(3),match.periods[2],match.ind_period_odd_even(3),'-','-',match.place, match.overtime()))
            writer.writerow((" "," "," "," "," "," "," "," ",-0.1,-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," "," "," "))
            writer.writerow((" "," "," "," "," "," "," "," ",-0.1,-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," ",-0.1," ",-0.1," "," "," "," "," "))

def add_color_format(workbook,total = 2.5 , ind_total = 1.5,match_count=3):
    total= 2.5
    ind_total = 1.5
    gap = workbook.add_format({'bg_color':'black','align':'center','border':2})
    t_more = workbook.add_format({'bg_color':"#ffdd03",'align':'center'}) # t more
    t_less = workbook.add_format({'bg_color':"#2bafe3",'align':'center'}) # t less
    victory = workbook.add_format({'bg_color':"#2ab53a",'align':'center'}) # victory
    draw = workbook.add_format({'bg_color':"#ffe62b",'align':'center'}) # draw
    loss = workbook.add_format({'bg_color':"#ff301a",'align':'center'}) # loss
    odd = workbook.add_format({'bg_color':"#ff6352",'align':'center'}) # odd 
    even = workbook.add_format({'bg_color':"#42c6ff",'align':'center'}) # even
    ind_more = workbook.add_format({'bg_color':"#558552",'align':'center'}) # ind t more
    ind_less = workbook.add_format({'bg_color':"#f0c0a1",'align':'center'}) # ind t less
    home =  workbook.add_format({'bg_color':"#ff5ce4",'align':'center'}) # home
    guest =  workbook.add_format({'bg_color':"#7746e0",'align':'center'}) # guest
    others = workbook.add_format({'bg_color':"#bae3f5",'align':'center','border':2}) # other cells
    header = workbook.add_format({'bg_color':"white",'align':'center','bold':'true'})
    numeric = workbook.add_format({'bg_color':"#bae3f5",'align':'center','border':2})
    #numeric.set_num_format(1)
    for worksheet in workbook.worksheets():
        worksheet.set_column('H:H',14,others)
        worksheet.set_column('Q:Q',15,others)
        worksheet.set_column('R:R',25,others)
        worksheet.set_column('C:C',40,others)
        worksheet.set_column('D:E',25,others)
        worksheet.set_column('B:B',15,others) 
        worksheet.set_column('F:F',10,others)
        worksheet.set_column('L:L',15,others)
        worksheet.set_column('P:P',10,others)
        worksheet.set_column('G:G',14,others)
        worksheet.set_column('I:I',14,others)
        worksheet.set_column('O:O',14,others)
        worksheet.set_column('J:J',15,others)
        worksheet.set_column('K:K',20,others)
        worksheet.set_column('M:M',20,others)
        worksheet.set_column('N:N',21,others)
        worksheet.write('M1','Тотал б/м [{}]'.format(total),header)
        worksheet.write('N1','Инд.Тотал б/м [{}]'.format(ind_total),header)
        worksheet.conditional_format('M2:M1000',{'type':'formula','criteria':"=AND($J2>{},ISNUMBER($J2))".format(total),'format':t_more})
        worksheet.conditional_format('M2:M1000',{'type':'formula','criteria':"=AND(ISNUMBER($J2),AND($J2<{},$J2>=0))".format(total),'format':t_less})
        worksheet.conditional_format('N2:N1000',{'type':'formula','criteria':"=AND($K2>{},ISNUMBER($K2))".format(ind_total),'format':ind_more})
        worksheet.conditional_format('N2:N1000',{'type':'formula','criteria':"=AND(ISNUMBER($K2),AND($K2<{},$K2>=0))".format(ind_total),'format':ind_less})
        #worksheet.conditional_format('M2:M1000',{'type':'text','criteria':"not containing",'value':'-','format':others}) 
        #worksheet.conditional_format('N2:N1000',{'type':'text','criteria':"not containing",'value':'-','format':others}) 
        worksheet.conditional_format('I2:I1000',{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
        worksheet.conditional_format('I2:I1000',{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        worksheet.conditional_format('L2:L1000',{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
        worksheet.conditional_format('L2:L1000',{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Победа",'format':victory})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Ничья",'format':draw})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Поражение",'format':loss})
        worksheet.conditional_format('O2:O1000',{'type':'text','criteria':'containing', 'value':"дом",'format':home})
        worksheet.conditional_format('O2:O1000',{'type':'text','criteria':'containing', 'value':"выезд",'format':guest})
        for i in range(match_count+2,545,match_count+2):
            worksheet.write("J{}".format(i),' ')
            worksheet.write("K{}".format(i),' ')
            worksheet.write("J{}".format(i+1),' ')
            worksheet.write("K{}".format(i+1),' ')
        worksheet.conditional_format('J2:J1000',{'type':'3_color_scale','min_value':0})
        worksheet.conditional_format('K2:K1000',{'type':'3_color_scale','min_value':0})
        worksheet.conditional_format('J2:J1000',{'type':'cell','criteria':"equal to",'value':-0.1,'format':others}) 
        worksheet.conditional_format('K2:K1000',{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})
        

   
def add_color_format_basketball(workbook,total = 200 , ind_total = 100,total_quarter = 55 , ind_total_quarter = 25 ,match_count = 3):
    t_more = workbook.add_format({'bg_color':"#ffdd03",'align':'center','border':2}) # t more
    t_less = workbook.add_format({'bg_color':"#2bafe3",'align':'center','border':2}) # t less
    victory = workbook.add_format({'bg_color':"#2ab53a",'align':'center','border':2}) # victory
    draw = workbook.add_format({'bg_color':"#ffe62b",'align':'center','border':2}) # draw
    loss = workbook.add_format({'bg_color':"#ff301a",'align':'center','border':2}) # loss
    odd = workbook.add_format({'bg_color':"#ff6352",'align':'center','border':2}) # odd 
    even = workbook.add_format({'bg_color':"#42c6ff",'align':'center','border':2}) # even
    ind_more = workbook.add_format({'bg_color':"#558552",'align':'center','border':2}) # ind t more
    ind_less = workbook.add_format({'bg_color':"#f0c0a1",'align':'center','border':2}) # ind t less
    home =  workbook.add_format({'bg_color':"#ff5ce4",'align':'center','border':2}) # home
    guest =  workbook.add_format({'bg_color':"#7746e0",'align':'center','border':2}) # guest
    others = workbook.add_format({'bg_color':"#bae3f5",'align':'center','border':2}) # other cells
    header = workbook.add_format({'bg_color':"white",'align':'center','bold':'true'})
    numeric = workbook.add_format({'bg_color':"#bae3f5",'align':'center','border':2})
    #numeric.set_num_format(1)
    colored_totals = ["O2" , "Q2" , "U2" , "W2"]
    d_colored_totals = ["AA2" , "AC2", "AG2 ", "AI2","AM2","AO2","AS2","AU2"]
    colored_odd_even= ["I2", "L2" ,"P2", "R2", "V2", "X2" ]
    d_colored_odd_even = ["AB2", "AD2", "AH2" , "AJ2","AN2" , "AP2", "AT2", "AV2"]
    colored_more_less = ["S2","Y2"]
    d_colored_more_less = ["AE2","AK2","AQ2","AW2"]
    colored_ind_more_less= ["T2","Z2"]
    d_colored_ind_more_less = ["AF2","AL2","AR2","AX2"]
    display = {'O2':'S2',  'U2':'Y2','AG2':'AK2', 'AM2':'AQ2'}
    idisplay = {'Q2':'T2','W2':'Z2','AI2':'AL2','AO2':'AR2'}
    disp_half = {'AA2':'AE2', 'AS2':'AW2'}
    idisp_half = {'AC2':'AF2','AU2':'AX2'}
    # AY2 , AZ2 - сравнение тоталов половин
    for worksheet in workbook.worksheets():
        
        worksheet.set_column('H:H',14,others)
        worksheet.set_column('Q:Q',15,others)
        worksheet.set_column('R:R',25,others)
        worksheet.set_column('C:C',40,others)
        worksheet.set_column('D:E',25,others)
        worksheet.set_column('B:B',15,others) 
        worksheet.set_column('F:F',10,others)
        worksheet.set_column('L:L',15,others)
        worksheet.set_column('P:P',10,others)
        worksheet.set_column('G:G',14,others)
        worksheet.set_column('I:I',14,others)
        worksheet.set_column('O:O',14,others)
        worksheet.set_column('J:J',15,others)
        worksheet.set_column('K:K',20,others)
        worksheet.set_column('M:M',20,others)
        worksheet.set_column('N:N',21,others)
        worksheet.set_column('AG:AG',15,others)
        worksheet.set_column('AH:AH',15,others)
        worksheet.set_column('AA:AA',25,others)
        worksheet.set_column('AC:AC',25,others)
        worksheet.set_column('AB:AB',20,others)
        worksheet.set_column('AD:AD',20,others)
        worksheet.set_column('AE:AE',20,others)
        worksheet.set_column('AF:AF',20,others)
        worksheet.set_column('AY:AY',30,others)
        worksheet.set_column('AZ:AZ',35,others)
        worksheet.set_column('BA:BA',15,others)
        worksheet.set_column('BB:BB',15,others)
        


        worksheet.write('M1','Тотал б/м [{}]'.format(total),header)
        worksheet.write('N1','Инд.Тотал б/м [{}]'.format(ind_total),header)
        
        
        for col in d_colored_totals:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),25,others)
        for col in d_colored_odd_even:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),20,others)
        for col in d_colored_more_less:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),27,others)
            worksheet.write('{}1'.format(col[:2]),'Тотал(четверть) б/м [{}]'.format(total_quarter),header)
        for col in d_colored_ind_more_less:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),27,others)
            worksheet.write('{}1'.format(col[:2]),'Инд.Тотал(четверть) б/м [{}]'.format(ind_total_quarter),header)
        for col in colored_totals:
            worksheet.set_column("{}:{}".format(col[0],col[0]),25,others)
        for col in colored_odd_even:
            worksheet.set_column("{}:{}".format(col[0],col[0]),20,others)
        for col in colored_more_less:
            worksheet.set_column("{}:{}".format(col[0],col[0]),27,others)
            worksheet.write('{}1'.format(col[0]),'Тотал(четверть) б/м [{}]'.format(total_quarter),header)
        for col in colored_ind_more_less:
            worksheet.set_column("{}:{}".format(col[0],col[0]),27,others)
            worksheet.write('{}1'.format(col[0]),'Инд.Тотал(четверть) б/м [{}]'.format(ind_total_quarter),header)
        
        for col in ['AE','AW']:
            worksheet.set_column("{}:{}".format(col,col),27,others)
            worksheet.write('{}1'.format(col),'Тотал(половина) б/м [{}]'.format(2 * total_quarter + 0.5),header)
        for col in ['AF','AX']:
            worksheet.set_column("{}:{}".format(col,col),30,others)
            worksheet.write('{}1'.format(col),'Инд. Тотал(половина) б/м [{}]'.format(2 * ind_total_quarter + 0.5),header)
        


            
        for col in colored_totals:
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'3_color_scale','min_value':0})
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})
        for col in d_colored_totals:
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'3_color_scale','min_value':0})
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})    
        for col in colored_odd_even:
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        for col in d_colored_odd_even:
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})


        for key in display:
            worksheet.conditional_format("{}:{}000".format(display[key],display[key]),{'type':'formula', 'criteria':"=AND(${}>{},ISNUMBER(${}))".format(key,total_quarter,key),'format':t_more})  
            worksheet.conditional_format("{}:{}000".format(display[key],display[key]),{'type':'formula', 'criteria':"=AND(ISNUMBER(${}),AND(${}<{},${}>=0))".format(key,key,total_quarter,key),'format':t_less})  
        for key in idisplay:
            worksheet.conditional_format("{}:{}000".format(idisplay[key],idisplay[key]),{'type':'formula', 'criteria':"=AND(${}>{},ISNUMBER(${}))".format(key,ind_total_quarter,key),'format':ind_more})  
            worksheet.conditional_format("{}:{}000".format(idisplay[key],idisplay[key]),{'type':'formula', 'criteria':"=AND(ISNUMBER(${}),AND(${}<{},${}>=0))".format(key,key,ind_total_quarter,key),'format':ind_less})

        for key in disp_half:
            worksheet.conditional_format("{}:{}000".format(disp_half[key],disp_half[key]),{'type':'formula', 'criteria':"=AND(${}>{},ISNUMBER(${}))".format(key,total_quarter*2 + 0.5,key),'format':t_more})  
            worksheet.conditional_format("{}:{}000".format(disp_half[key],disp_half[key]),{'type':'formula', 'criteria':"=AND(ISNUMBER(${}),AND(${}<{},${}>=0))".format(key,key,total_quarter*2 + 0.5,key),'format':t_less})  
        for key in idisp_half:
            worksheet.conditional_format("{}:{}000".format(idisp_half[key],idisp_half[key]),{'type':'formula', 'criteria':"=AND(${}>{},ISNUMBER(${}))".format(key,ind_total_quarter*2 + 0.5,key),'format':ind_more})  
            worksheet.conditional_format("{}:{}000".format(idisp_half[key],idisp_half[key]),{'type':'formula', 'criteria':"=AND(ISNUMBER(${}),AND(${}<{},${}>=0))".format(key,key,ind_total_quarter*2 + 0.5,key),'format':ind_less})
        

    
        elim = ['J','K','O','Q','U','W','AA','AC','AG','AI','AM','AO','AS','AU']
        for i in range(match_count+2,545,match_count+2):
            for el in elim:
                worksheet.write("{}{}".format(el,i),' ')
                worksheet.write("{}{}".format(el,i+1),' ')
          
        worksheet.conditional_format('M2:M1000',{'type':'formula','criteria':"=AND($J2>{},ISNUMBER($J2))".format(total),'format':t_more})
        worksheet.conditional_format('M2:M1000',{'type':'formula','criteria':"=AND(ISNUMBER($J2),AND($J2<{},$J2>=0))".format(total),'format':t_less})
        worksheet.conditional_format('N2:N1000',{'type':'formula','criteria':"=AND($K2>{},ISNUMBER($K2))".format(ind_total),'format':ind_more})
        worksheet.conditional_format('N2:N1000',{'type':'formula','criteria':"=AND(ISNUMBER($K2),AND($K2<{},$K2>=0))".format(ind_total),'format':ind_less})
        worksheet.conditional_format('J2:J1000',{'type':'3_color_scale','min_value':0})
        worksheet.conditional_format('K2:K1000',{'type':'3_color_scale','min_value':0})
        worksheet.conditional_format('J2:J1000',{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})
        worksheet.conditional_format('K2:K1000',{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})
        worksheet.conditional_format('I2:I1000',{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
        worksheet.conditional_format('I2:I1000',{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        worksheet.conditional_format('L2:L1000',{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
        worksheet.conditional_format('L2:L1000',{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Победа",'format':victory})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Ничья",'format':draw})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Поражение",'format':loss})
        worksheet.conditional_format('AY2:AY1000',{'type':'text','criteria':'containing', 'value':"нет",'format':home}) 
        worksheet.conditional_format('AY2:AY1000',{'type':'text','criteria':'containing', 'value':"да",'format':guest}) 
        worksheet.conditional_format('AZ2:AZ1000',{'type':'text','criteria':'containing', 'value':"нет",'format':ind_less}) 
        worksheet.conditional_format('AZ2:AZ1000',{'type':'text','criteria':'containing', 'value':"да",'format':ind_more}) 
        worksheet.conditional_format('BB2:BB1000',{'type':'text','criteria':'containing', 'value':"нет",'format':home}) 
        worksheet.conditional_format('BB2:BB1000',{'type':'text','criteria':'containing', 'value':"да",'format':guest}) 

def add_color_format_hockey(workbook,total = 5.5 , ind_total = 2.5 ,total_period = 1.5 , ind_total_period = 0.5 , match_count = 3):
    t_more = workbook.add_format({'bg_color':"#ffdd03",'align':'center','border':2}) # t more
    t_less = workbook.add_format({'bg_color':"#2bafe3",'align':'center','border':2}) # t less
    victory = workbook.add_format({'bg_color':"#2ab53a",'align':'center','border':2}) # victory
    draw = workbook.add_format({'bg_color':"#ffe62b",'align':'center','border':2}) # draw
    loss = workbook.add_format({'bg_color':"#ff301a",'align':'center','border':2}) # loss
    odd = workbook.add_format({'bg_color':"#ff6352",'align':'center','border':2}) # odd 
    even = workbook.add_format({'bg_color':"#42c6ff",'align':'center','border':2}) # even
    ind_more = workbook.add_format({'bg_color':"#558552",'align':'center','border':2}) # ind t more
    ind_less = workbook.add_format({'bg_color':"#f0c0a1",'align':'center','border':2}) # ind t less
    home =  workbook.add_format({'bg_color':"#ff5ce4",'align':'center','border':2}) # home
    guest =  workbook.add_format({'bg_color':"#7746e0",'align':'center','border':2}) # guest
    others = workbook.add_format({'bg_color':"#bae3f5",'align':'center','border':2}) # other cells
    header = workbook.add_format({'bg_color':"white",'align':'center','bold':'true'})
    numeric = workbook.add_format({'bg_color':"#bae3f5",'align':'center','border':2})
    #numeric.set_num_format(1)
    colored_totals = ["O2" , "Q2" , "U2" , "W2"]
    d_colored_totals = ["AA2" , "AC2"]
    colored_odd_even= ["P2", "R2", "V2", "X2"]
    d_colored_odd_even = ["AB2", "AD2"]
    colored_more_less = ["S2","Y2"]
    d_colored_more_less = ["AE2"]
    colored_ind_more_less = ["T2","Z2"]
    d_colored_ind_more_less = ["AF2"]
    display = {'O2':'S2',  'U2':'Y2', 'AA2':'AE2'}
    idisplay = {'Q2':'T2','W2':'Z2','AC2':'AF2'}
    for worksheet in workbook.worksheets():
        
               
        worksheet.set_column('H:H',14,others)
        worksheet.set_column('Q:Q',15,others)
        worksheet.set_column('R:R',25,others)
        worksheet.set_column('C:C',40,others)
        worksheet.set_column('D:E',25,others)
        worksheet.set_column('B:B',15,others) 
        worksheet.set_column('F:F',10,others)
        worksheet.set_column('L:L',15,others)
        worksheet.set_column('P:P',10,others)
        worksheet.set_column('G:G',14,others)
        worksheet.set_column('I:I',14,others)
        worksheet.set_column('O:O',14,others)
        worksheet.set_column('J:J',15,others)
        worksheet.set_column('K:K',20,others)
        worksheet.set_column('M:M',20,others)
        worksheet.set_column('N:N',21,others)
        worksheet.set_column('AG:AG',15,others)
        worksheet.set_column('AH:AH',15,others)
        worksheet.set_column('AA:AA',25,others)
        worksheet.set_column('AC:AC',25,others)
        worksheet.set_column('AB:AB',20,others)
        worksheet.set_column('AD:AD',20,others)
        worksheet.set_column('AE:AE',20,others)
        worksheet.set_column('AF:AF',20,others)
        
        worksheet.write('M1','Тотал б/м [{}]'.format(total),header)
        worksheet.write('N1','Инд.Тотал б/м [{}]'.format(ind_total),header)
        for col in d_colored_totals:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),25,others)
        for col in d_colored_odd_even:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),20,others)
        for col in d_colored_more_less:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),27,others)
            worksheet.write('{}1'.format(col[:2]),'Тотал(период) б/м [{}]'.format(total_period),header)
        for col in d_colored_ind_more_less:
            worksheet.set_column("{}:{}".format(col[:2],col[:2]),27,others)
            worksheet.write('{}1'.format(col[:2]),'Инд.Тотал(период) б/м [{}]'.format(ind_total_period),header)
        for col in colored_totals:
            worksheet.set_column("{}:{}".format(col[0],col[0]),25,others)
        for col in colored_odd_even:
            worksheet.set_column("{}:{}".format(col[0],col[0]),20,others)
        for col in colored_more_less:
            worksheet.set_column("{}:{}".format(col[0],col[0]),27,others)
            worksheet.write('{}1'.format(col[0]),'Тотал(период) б/м [{}]'.format(total_period),header)
        for col in colored_ind_more_less:
            worksheet.set_column("{}:{}".format(col[0],col[0]),27,others)
            worksheet.write('{}1'.format(col[0]),'Инд.Тотал(период) б/м [{}]'.format(ind_total_period),header)

            
        for col in colored_totals:
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'3_color_scale','min_value':0})
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})
        for col in d_colored_totals:
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'3_color_scale','min_value':0})
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'cell','criteria':"equal to",'value':-0.1,'format':others}) 
        for col in colored_odd_even:
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
            worksheet.conditional_format("{}:{}1000".format(col,col[0]),{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        for col in d_colored_odd_even:
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
            worksheet.conditional_format("{}:{}1000".format(col,col[:2]),{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})




        for key in display:
            worksheet.conditional_format("{}:{}000".format(display[key],display[key]),{'type':'formula', 'criteria':"=AND(${}>{},ISNUMBER(${}))".format(key,total_period,key),'format':t_more})  
            worksheet.conditional_format("{}:{}000".format(display[key],display[key]),{'type':'formula', 'criteria':"=AND(ISNUMBER(${}),AND(${}<{},${}>=0))".format(key,key,total_period,key),'format':t_less})  
        for key in idisplay:
            worksheet.conditional_format("{}:{}000".format(idisplay[key],idisplay[key]),{'type':'formula', 'criteria':"=AND(${}>{},ISNUMBER(${}))".format(key,ind_total_period,key),'format':ind_more})  
            worksheet.conditional_format("{}:{}000".format(idisplay[key],idisplay[key]),{'type':'formula', 'criteria':"=AND(ISNUMBER(${}),AND(${}<{},${}>=0))".format(key,key,ind_total_period,key),'format':ind_less})
        
        elim = ['J','K','O','Q','U','W','AA','AC']
        for i in range(match_count+2,545,match_count+2):
            for el in elim:
                worksheet.write("{}{}".format(el,i),' ')
                worksheet.write("{}{}".format(el,i+1),' ')
          
        worksheet.conditional_format('M2:M1000',{'type':'formula','criteria':"=AND($J2>{},ISNUMBER($J2))".format(total),'format':t_more})
        worksheet.conditional_format('M2:M1000',{'type':'formula','criteria':"=AND(ISNUMBER($J2),AND($J2<{},$J2>=0))".format(total),'format':t_less})
        worksheet.conditional_format('N2:N1000',{'type':'formula','criteria':"=AND($K2>{},ISNUMBER($K2))".format(ind_total),'format':ind_more})
        worksheet.conditional_format('N2:N1000',{'type':'formula','criteria':"=AND(ISNUMBER($K2),AND($K2<{},$K2>=0))".format(ind_total),'format':ind_less})
        worksheet.conditional_format('J2:J1000',{'type':'3_color_scale','min_value':0})
        worksheet.conditional_format('K2:K1000',{'type':'3_color_scale','min_value':0})
        worksheet.conditional_format('J2:J1000',{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})
        worksheet.conditional_format('K2:K1000',{'type':'cell','criteria':"equal to",'value':-0.1,'format':others})
        worksheet.conditional_format('I2:I1000',{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
        worksheet.conditional_format('I2:I1000',{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        worksheet.conditional_format('L2:L1000',{'type':'text','criteria':'containing', 'value':"Чёт",'format':even})
        worksheet.conditional_format('L2:L1000',{'type':'text','criteria':'containing', 'value':"Нечет",'format':odd})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Победа",'format':victory})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Ничья",'format':draw})
        worksheet.conditional_format('G2:G1000',{'type':'text','criteria':'containing', 'value':"Поражение",'format':loss})
        worksheet.conditional_format('AH2:AH1000',{'type':'text','criteria':'containing', 'value':"нет",'format':home}) # или на AG
        worksheet.conditional_format('AH2:AH1000',{'type':'text','criteria':'containing', 'value':"да",'format':guest}) # или на AG 

def write_to_excel(directory,sports="football",t = 2.5 , i_t = 1.5 , t_p = 1.5 , i_t_p = 0.5, count = 3):
    excel_file = "{}/{}_parsed.xlsx".format(sports,sports)
    excel_writer = pandas.ExcelWriter(excel_file,engine = 'xlsxwriter') 
    for index,file_name in enumerate(os.listdir(directory)):
        #,keep_default_na = False , converters = {'Тотал': int , 'Инд. тотал команды': int} , ,engine='python'
        #f_name = "{0}/match_day/{1}".format(sports,file_name)
        f_name = "{0}/match_day/{1}".format(sports,file_name)        
        df = pandas.read_csv(f_name,sep = ',' , keep_default_na = False,encoding='utf-8',engine='python') # о чудо!
        sheet = "Sheet-{}".format(index +1)
        df.to_excel(excel_writer, sheet_name = sheet) 
        print(f"Завершено {(index+1) / len(os.listdir(directory)) * 100} %")
    workbook = excel_writer.book    
    if sports == "football":
        add_color_format(workbook,total = t , ind_total = i_t , match_count = count)
    if sports == 'basketball':
        add_color_format_basketball(workbook ,total = t , ind_total = i_t , total_quarter = t_p , ind_total_quarter = i_t_p , match_count = count)
    if sports == 'hockey':
        add_color_format_hockey(workbook,total = t , ind_total = i_t , total_period = t_p , ind_total_period = i_t_p ,match_count = count)
    excel_writer.save()
##########################################################################
def suite(pattern,league):             # передаём table
    head = league.find_element_by_class_name('head_ab')
    league_name = head.find_element_by_class_name("name").text.strip()  # ?    
    header = head.find_element_by_tag_name('span').text.strip()                                         
    return bool((header == "Таблица" or header == "Таблица Live" ) and pattern.search(league_name) == None)

def not_status(status):
    if status == "Завершен" or status == "После овертайма" or status == "Прерван" or status == "Перенесен" or status == "Перерыв" or status == "Отменен" or status.isdigit():
        return True
    else:
        return False

def get_teams_links(driver,url):
    teams_dict = []
    link_pattern = re.compile(".*\('(.+)'\);.*") # сразу со слэшем
    div = WebDriverWait(driver,timeout=30).until(
    lambda x : x.find_element_by_id('flashscore'))
    for team in [div.find_element_by_class_name('tname-home') , div.find_element_by_class_name('tname-away')]:
        name = team.find_element_by_tag_name('a').text.strip()
        while name=="" or name == None:
            name = team.find_element_by_tag_name('a').text.strip()
        link = url + link_pattern.search(team.find_element_by_tag_name('a').get_attribute('onclick')).group(1)+'/'
        print(f"Team: {name} , link: {link}")
        teams_dict.append({'team': name , 'link': link})
        name = ""
    return teams_dict


def list_of_day_teams(driver,url,sports="football"): 
    compound_list = []
    driver.get(url+ f"/{sports}")  
    div = WebDriverWait(driver,timeout=30).until(
    lambda x : x.find_element_by_class_name('table-main'))   
    pattern = re.compile("^.*(Cup|Copa|Кубок|кубок|Квалификация).*$")
    tables = div.find_elements_by_tag_name('table')        # сначала получить ссылки команд   
    leagues =[table for table in tables if suite(pattern,table)]  # ищем подходящие лиги 
    parent_window = driver.current_window_handle
    for league in leagues:
        teams_dict = []
        league_name = league.find_element_by_class_name('head_ab').find_element_by_class_name("name").text.strip()
        #if league.find_element_by_class_name('expand-league-link').size()!=0:
            #expand = league.find_element_by_class_name('expand-league-link') 
            #tbody = WebDriverWait(driver,5).until(league.find_element_by_tag_name('tbody'))
        tbody =  league.find_element_by_tag_name('tbody')
        print(f"\nLeague: {league_name}\n")
        trs = [ tr for tr in tbody.find_elements_by_tag_name('tr') if tr.get_attribute('class')!="blank-line"]
        for index,tr in enumerate(trs):      # непосредственно матчи лиги
            if ((sports == "football") or (((index+1) % 2)==1)):
                status = tr.find_element_by_class_name('cell_aa').text.strip()
                if not_status(status):
                    continue
            else:
                continue
            link = tr.get_attribute('id')
            match_link = link[link.rfind('_') + 1 :]
            driver.execute_script("window.open();")
            for handle in driver.window_handles:
                if handle != parent_window:
                    driver.switch_to_window(handle)
                    break
            driver.get(url +'/match/' + match_link + '/#match-summary')
            teams_dict.extend(get_teams_links(driver,url)) 
            driver.close()
            driver.switch_to_window(parent_window)
        compound_list.append({'league':league_name, 'teams': teams_dict})
    return compound_list

def write_day_teams_to_file(driver,url,sports="football"):
    print(url+ f"/{sports}")
    driver.get(url+ f"/{sports}")  
    div = WebDriverWait(driver,timeout=30).until(
    lambda x : x.find_element_by_class_name('table-main'))   
    pattern = re.compile("^.*(Cup|Copa|Кубок|кубок|Квалификация).*$")
    tables = div.find_elements_by_tag_name('table')        # сначала получить ссылки команд   
    #leagues =[table for table in tables if suite(pattern,table)]  # ищем подходящие лиги 
    parent_window = driver.current_window_handle
    file_name = "{}/day_teams/teams.csv".format(sports)
    csv_file = open(file_name,'a',encoding="utf-8",newline='')
    writer = csv.writer(csv_file)
    writer.writerow(('Лига','Команда','Ссылка'))
    for index,league in enumerate(tables):
         #закомментить про index == number 
        if index == 1:
            break
        teams_dict = []
        league_name = league.find_element_by_class_name('head_ab').find_element_by_class_name("name").text.strip()
        if suite(pattern,league):
            #if league.find_element_by_class_name('expand-league-link').size()!=0:
                #expand = league.find_element_by_class_name('expand-league-link') 
                #tbody = WebDriverWait(driver,5).until(league.find_element_by_tag_name('tbody'))
            tbody =  league.find_element_by_tag_name('tbody')
            print(f"\nLeague: {league_name}\n")
            trs = [ tr for tr in tbody.find_elements_by_tag_name('tr') if tr.get_attribute('class')!="blank-line"]
            for index,tr in enumerate(trs):      # непосредственно матчи лиги
                if ((sports == "football") or (((index+1) % 2)==1)):
                    status = tr.find_element_by_class_name('cell_aa').text.strip()
                    if not_status(status):
                        continue
                else:
                    continue
                link= tr.get_attribute('id')
                match_link = link[link.rfind('_') + 1 :]
                driver.execute_script("window.open();")
                for handle in driver.window_handles:
                    if handle != parent_window:
                        driver.switch_to_window(handle)
                        break
                driver.get(url +'/match/' + match_link + '/#match-summary')
                teams = get_teams_links(driver,url)
                for team in teams:
                    writer.writerow((league_name,team['team'],team['link']))               
                driver.close()
                driver.switch_to_window(parent_window)     
    writer.writerow(('#','#','#'))      
    csv_file.close()

def load_day_teams_from_file(sports="football"):
    file_name = "{}/day_teams/teams.csv".format(sports)
    compound_list = []
    with open(file_name,'r',encoding='utf-8',newline='') as csv_file:  
        reader = csv.reader(csv_file)
        reader.__next__() # headers?
        row= reader.__next__()
        teams = []
        league_name = row[0] 
        teams.append({'team': row[1] ,'link':row[2]}) 
        for index , row in enumerate(csv.reader(csv_file)):
            if row[0] =='#':
                compound_list.append({'league':league_name , 'teams': teams})
                break
            elif row[0] == league_name:
                teams.append({'team':row[1],'link':row[2]})
            else:
                compound_list.append({'league':league_name , 'teams': teams})
                teams = []
                league_name = row[0]
                teams.append({'team': row[1] ,'link':row[2]})
        
    return compound_list

##########################################################################
# парсинг текущего дня полностью(с записью в excel)

def parse_teams_list(driver,_list,sports="football"):
    for index,el in enumerate(_list):
        print(f"\n{el['league']}\n") 
        #file_name = f"league-{index+1}"
        file_name = "{0}/match_day/{1}.csv".format(sports,el['league'].replace(': ',' '))
        print(f"Filename: {file_name}")
        with open(file_name,'a',encoding="utf-8",newline='') as csv_file:
            writer = csv.writer(csv_file)
            if sports == 'football':
                writer.writerow(('Вид спорта','Лига','Команда',	'Матч',	'Дата','Итог',	'Счёт', 'Чёт/нечет','Тотал','Инд.тотал команды','Инд. чёт/ нечет','Тотал б/м [тотал]','Инд.тотал б/м [тотал]','Дом / Выезд','Овертайм'))  
                for team in el['teams']:
                    driver.get(team['link'] + 'results')
                    t = parse_football_team(driver,el['league'],team['team'],sports = sports)
                    write_team(writer,t)
            elif sports =="basketball":
                writer.writerow(('Вид спорта','Лига','Команда',	'Матч',	'Дата','Итог',	'Счёт', 'Чёт/нечет','Тотал','Инд.тотал команды','Инд. чёт/ нечет','Тотал б/м [тотал]','Инд.тотал б/м [тотал]','Тотал 1-ой четверти','Чёт/нечет','Инд. тотал 1-ой четверти','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 2-ой четверти','Чёт/нечет','Инд. тотал 2-ой четверти','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 1-ой половины','Чёт/нечет','Инд. тотал 1-ой половины','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 3-ой четверти','Чёт/нечет','Инд. тотал 3-ой четверти','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 4-ой четверти','Чёт/нечет','Инд. тотал 4-ой четверти','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 2-ой половины','Чёт/нечет','Инд. тотал 2-ой  половины','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 1-половины > 2 половины', 'Инд. тотал 1-половины > 2 половины','Дом / Выезд','Овертайм'))
                for team in el['teams']:
                    driver.get(team['link'] + 'results') # если что,добавить '/' перед 'results'
                    t = parse_basketball_team(driver,el['league'],team['team'])
                    write_team(writer,t,'basketball')
            elif sports =="hockey":
                print("Writing hockey")
                writer.writerow(('Вид спорта','Лига','Команда',	'Матч',	'Дата','Итог',	'Счёт', 'Чёт/нечет','Тотал','Инд.тотал команды','Инд. чёт/ нечет','Тотал б/м [тотал]','Инд.тотал б/м [тотал]','Тотал 1-го периода','Чёт/Нечет','Инд. тотал 1-го периода','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 2-го периода','Чёт/Нечет','Инд. тотал 2-го периода','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Тотал 3-го периода','Чёт/Нечет','Инд. тотал 3-го периода','Инд. чёт/нечет','Тотал больше[тотал]','Инд. тотал больше[тотал]','Дом / Выезд','Овертайм'))  
                for team in el['teams']:
                    driver.get(team['link'] + 'results')
                    t = parse_hockey_team(driver,el['league'],team['team'])
                    write_team(writer,t,"hockey")

def parse_match_day(driver,url,sports="football"):
    parse_teams_list(driver,list_of_day_teams(driver,url,sports),sports)
    write_to_excel(("C:/python-app/{}}/match_day/".format(sports)))


##############################################################################
def league_teams_links(url,driver,league_name,index,sport="football"):
    teams = [] 
    link_pattern = re.compile(".*\('(.+)'\);")
    file_name = "{0}/all_teams/{1}.csv".format(sport,league_name.replace(': ',' '))
    with open(file_name,'a',encoding="utf-8",newline='') as csv_file:
        writer = csv.writer(csv_file)    
        writer.writerow(('Лига','Команда','Ссылка'))    
        WebDriverWait(driver,timeout=10).until(
        lambda x: x.find_element_by_class_name("glib-stats-data"))
        for span in driver.find_elements_by_class_name("team_name_span"):# команды 
            team = span.find_element_by_tag_name("a").text.strip() # ?
            onclick = span.find_element_by_tag_name("a").get_attribute("onclick")
            link = url + link_pattern.search(onclick).group(1)
            print("Team : " + team + " link: " + link)
            # namer = league_name.replace(': ',' ')
            writer.writerow((league_name,team,link))  
            teams.append({ 'team': team ,'link': link})       
    return {'league':league_name,'teams':teams}

def teams_links_from_tables(url,sport = "football", profile = None, file_path = None):
    start = datetime.now()
    leagues = []
    while True:
        driver = None
        try:
            driver = webdriver.Firefox(firefox_profile = profile)
            driver.implicitly_wait(10)
            driver.get(url)
            div = WebDriverWait(driver,timeout=30).until(
            EC.presence_of_element_located((By.CLASS_NAME,'table-main')),message="table-main for today")
            parent_window = driver.current_window_handle          
            pattern = re.compile("^.*(Cup|Copa|Кубок|кубок|Квалификация).*$")
            leagues = div.find_elements_by_class_name("head_ab")    
            print("Количество найденных :" + str(len(leagues)))
            for index,league in enumerate(leagues):

                WebDriverWait(driver,timeout=30).until(
                EC.presence_of_element_located((By.CLASS_NAME,'head_ab')),message="head_ab in league")

                WebDriverWait(driver,timeout=30).until(
                lambda x : x.find_element_by_css_selector(".stats-link.link-tables"),message="stats-link")  
                
                league_name = league.find_element_by_class_name("name").text.strip()  # ? 
                head =league.find_element_by_tag_name('span').text.strip()                                        
                if (head == "Таблица" or head =="Таблица Live") and pattern.search(league_name) == None:               
                    os.system("cls") 
                    print("\n\nLeague : " + league_name + "\n")
                    WebDriverWait(driver,timeout=30).until(
                    lambda x : x.find_element_by_class_name("stats"))  
                    league.find_element_by_tag_name('span').click()
                    for handle in driver.window_handles:                       
                        if handle != parent_window:
                            driver.switch_to_window(handle)                             
                            break                  
                    leagues.append(league_teams_links(url,driver,league_name,index,sport))
                    driver.close()       
                    driver.switch_to_window(parent_window)
                print("Index: " + str(index+1))
                print("\n Processing... \n" + str(datetime.now() - start) + '\n')                                                            
        except AttributeError as e:
            print(e)
            if driver!= None:               
                driver.quit()
            break
        except OSError as e :
            print(e)
            print("=======Waiting...=======")
            #что-нить ещё сделать, например поменять profile?
            if driver!= None:               
                driver.quit()
            continue
        else:
            driver.quit()
            break
        finally:
            if driver!= None:               
                driver.quit()
    return leagues
    print("\n\n Время: " + str(datetime.now() - start) + '\n')        

def all_teams_files_to_excel(directory='D:/Programming/Web/python-app/football/all_teams',sports="football"):
    print("Внутри all_teams_files_to_excel")  
    excel_file = 'teams_list.xlsx'    
    excel_writer = pandas.ExcelWriter(excel_file,engine = 'xlsxwriter')    
    for index,f in enumerate(os.listdir(directory)):        
        print("File: %s" % f)
        f_name = "{0}/all_teams/{1}".format(sports,f)
        df = pandas.read_csv(f_name , sep=',', engine="python", encoding="utf-8")
        sheet = "Sheet-{}".format(index +1)  
        df.to_excel(excel_writer,sheet_name = sheet)
    workbook = excel_writer.book
    header = workbook.add_format({'bg_color':"white",'align':'center','bold':'true'})
    others = workbook.add_format({'align':'center','border':2})
    for worksheet in workbook.worksheets():
        #worksheet.set_row(0,header)
        worksheet.set_column('C:C',40,others)
        worksheet.set_column('D:D',60,others)
        worksheet.set_column('B:B',40,others) 
        
    excel_writer.save()

if __name__ =='__main__':
    sports = "basketball"
    total , ind_total = 2.5 , 1.5
    match_count = 3
    url = "https://www.myscore.ru"
    attempts = 0  
    if sports =="hockey":
        total , ind_total = 5.5,2.5
    if sports =="basketball":
        total , ind_total = 200.5,100.5
    if len(sys.argv) == 5:
        sports = sys.argv[1]
        total = int(sys.argv[2])
        ind_total = int(sys.argv[3])
        match_count = int(sys.argv[4])
    elif len(sys.argv) ==3:
        sports = sys.argv[1]
        total = int(sys.argv[2])
    elif len(sys.argv) ==2:
        if sys.argv[1].isdigit():
            total =sys.argv[1]
        else: 
            sports = sys.argv[1]
    
    write_to_excel(("D:/Programming/Web/python-app/{}/match_day/".format(sports)),sports = sports,count = match_count)
    #teams_links_from_tables(url) 
    #all_teams_files_to_excel()
    """
    while True:
        try:
            options = webdriver.firefox.options.Options()
            options.set_headless(headless = True)
            profile = set_profile()
            driver = webdriver.Firefox(firefox_options = options,firefox_profile = profile)  
            print("driver is on...")
            #write_day_teams_to_file(driver,url,sports)
            #_list = load_day_teams_from_file(sports)
            #parse_teams_list(driver,_list,sports)
            write_to_excel(("D:/Programming/Web/python-app/{}/match_day/".format(sports)),sports)
        except OSError as e:
            print(e)
            if driver != None:
                driver.quit()
            continue
        except TimeoutException as e:
            attempts+=1
            print(e)
            if attempts > 5:
                break
            else:
                continue
        else:
            break
        finally:
            driver.quit()
    """
   
    