import requests , csv , time , lxml , os ,sys, team , re , pandas , my_score_parser as parser, test
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



def list_of_all_leagues_and_teams(url,driver,sports = "football"):
    _list = [] 
    driver.get(url + '/' + sports)
    ul = WebDriverWait(driver,timeout=30).until(
    lambda x : x.find_element_by_css_selector('ul.menu.country-list.tournament-menu'))
    _li = ul.find_element_by_class_name('show-more')
    _li.click()
    print("Нажал на раскрытие")
    WebDriverWait(driver,timeout = 30).until(
    lambda x : x.find_element_by_xpath("//li[@class='head'][text() = 'Другие соревнования']")
    )
    print("Нашёл полный список")
    ul_lists = driver.find_elements_by_css_selector('ul.menu.country-list.tournament-menu')
    print("Нашёл списки лиг")
    counter = 0 
    for index,ul in enumerate(ul_lists):     
        print(ul.text)

    for index,ul in enumerate(ul_lists):    
        lis = ul.find_elements_by_tag_name('li')
        li_count = 0
        for ind,li in enumerate(lis):
            print(f"Номер лиги: {ind}")
            if li.get_attribute('class') == "head":
                counter+=1
                if counter == 2:
                    break
                else:
                    continue                  
            _id = li.get_attribute('id')
            print(f"Id : {_id}") 
            li.click()  # попробовать через другую переменную
            temp = WebDriverWait(driver , timeout = 30).until(
            lambda x: x.find_element_by_xpath(f"//li[@id='{_id}'][@class='active']")
            ) 
            print(f"Лиги в стране : {li.text}")
            li_count+=1
            # задержку
            sub_ul = temp.find_element_by_class_name('submenu')          
            for li_ in sub_ul.find_elements_by_tag_name('li'):
                a = li_.find_element_by_tag_name('a')
                link = url + a.get_attribute('href') # уже со слешэм в конце
                league_name = a.text.strip()
                print(f" Лига: {league_name} , ссылка: {link}")
                _list.append({'league':league_name , 'link': link})
            temp.find_elements_by_tag_name('a')[0].click()
            print("Зыкрыли id: {}".format(_id)) 
            WebDriverWait(driver , timeout = 30).until(
            lambda x: x.find_element_by_xpath(f"//li[@id='{_id}'][@class='']")
            )

            """
            temp = WebDriverWait(driver , timeout = 30).until(
            lambda x: x.find_element_by_xpath(f"//li[@id='{_id}']"))
            
            temp.click()
            WebDriverWait(driver , timeout = 30).until('
            lambda x: x.find_element_by_xpath(f"//li[@id="{_id}']")
            )
            """
           
    return _list

def write_all_leagues_and_teams_to_file(url,_list,driver,sports="football"):
    for index,league in enumerate(_list):
        driver.get(league['link']+'teams')
        div = WebDriverWait(driver , timeout = 30).until(
        lambda x: x.find_element_by_id('tournament-page-participants'))
        tbody = div.find_element_by_tag_name('tbody')
        file_name = "{0}/all_teams/{1}.csv".format(sports,league['league'].replace(': ',' '))
        with open(file_name,'a',encoding="utf-8",newline='') as csv_file:
            writer = csv.writer(csv_file) 
            writer.writerow(('Лига','Команда','Ссылка'))
            for tr in tbody.find_elements_by_tag_name('tr'):
                link = url + tr.find_element_by_tag_name('a').get_attribute('href').strip() + '/'
                team = tr.find_element_by_tag_name('a').text.strip()
                writer.writerow((league['league'],team,link))
 

if __name__ =='__main__':
    
    url_test = "https://yandex.ru/internet/"
    url = 'https://www.myscore.ru'
    useragents = open('data/agents2','r',encoding='utf-8').read().split('\n')
    proxies = open('data/proxies','r',encoding='utf-8').read().split('\n')
    useragent = choice(useragents)
    proxy = choice(proxies).split(':')
    print(f"Proxy: IP: {proxy[0]} , port: {int(proxy[1])} , Useragent: {useragent} ")
    driver = webdriver.Firefox(firefox_profile = test.set_profile(useragent,proxy))
    driver.get(url_test)
    test.set_cookies(driver)
    attempts = 0
    while True:
        if attempts == 5:
            break
        try:
            _list = list_of_all_leagues_and_teams(url,driver,sports="hockey")
            write_all_leagues_and_teams_to_file(url,_list,driver, sports = "hockey")
        except TimeoutException as t:
            attempts+=1
            print(t)
            continue     
        else:
            break
    
    print("Число попыток: {}".format(attempts))  
    """
    num_arr = []
    number = int(input("Введите число:"))   
    while number > 0:
        remainder = number % 2 
        num_arr.append(remainder)
        number = number // 2      
    num_arr.reverse()
    print(''.join([str(i) for i in num_arr]))
    """

   

        






            
            
