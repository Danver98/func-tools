import csv
import os
import random
import re
import sys
import time
from datetime import datetime
from random import choice
import pandas
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from functools import partial

from match import Match
from team import Team


def item_has_text_and_out_of_pattern(item, text, pattern):
    name = item.find_element_by_class_name("name").text.strip()
    tag_elem = item.find_element_by_tag_name('span')
    if tag_elem.text == text and pattern.search(name) == None:
        return True
    return False


def parse_single_league(league, url, driver):
    league_name = league.find_element_by_class_name("name").text.strip()
    league.find_element_by_tag_name('span').click()
    parse_and_write_league_results(url, driver, league_name)


def parse_leagues(driver, url):
    collection = driver.find_elements_by_class_name("head_ab")
    pattern = re.compile("^.*(Cup|Copa|Кубок|кубок).*$")
    text = "Таблица"
    helper_args = [url, driver]
    filtered_leagues = list(filter(partial(item_has_text_and_out_of_pattern, text=text, pattern=pattern), collection)
    list(map(lambda league: parse_single_league(
        league, *helper_args), filtered_leagues))


def get_prepared_driver(url):
    driver=webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(url)
    driver.find_element_by_class_name("soccer").click()
    WebDriverWait(driver, timeout=30).until(
        lambda x: x.find_element_by_class_name("table-main"))
    return driver


def do_to_result(f):
    def wrapper(arg):
        while True:
            driver=None
            try:
                f(driver, arg)
            except TimeoutError as e:
                on_exception(driver, e.__class__.__name__)
                continue
            except OSError as e:
                on_exception(driver, e.__class__.__name__, e)
                continue
            else:
                driver.quit()
                break
    return wrapper


def parse(driver, url):
    driver=getPreparedDriver(url)
    parse_leagues(driver, url)
    driver.close()


def on_exception(driver, message,  exception=None):
    if(exception):
        print(exception)
    print(message)
    if (driver != None) and (isinstance(driver, webdriver.Firefox)):
        driver.close()


def process_team(item, driver, parent_window, url, league_name, writer):
    team_name=item.find_element_by_tag_name(
        "a").text.strip()  # ?
    onclick=item.find_element_by_tag_name(
        "a").get_attribute("onclick")
    link_pattern=re.compile(".*\('(.+)'\);")
    link=link_pattern.search(onclick).group(1)
    current_window=driver.current_window_handle
    driver.switch_to_window(parent_window)
    driver.execute_script("window.open();")
    tab_handle = driver.window_handles[1]
    driver.switch_to_window(tab_handle)
    driver.get(url+link+'results')
    driver.switch_to_window(tab_handle)
    next_=str(url+link)
    team=parse_football_team(
        league_name, team_name, driver, next_)
    write_team(writer, team)
    driver.close()
    driver.switch_to_window(current_window)


def process_teams(handle, driver, parent_window, url, league_name, writer):
    driver.switch_to_window(handle)
    WebDriverWait(driver, timeout=10).until(
        lambda x: x.find_element_by_class_name("glib-stats-data"))
    # команды
    teams=driver.find_elements_by_class_name("team_name_span")
    list(map(lambda team: process_team(team, driver,
         parent_window, url, league_name, writer), teams))
    driver.close()


def process_handle(handle, driver, parent_window, url, league_name, writer):
    if(handle == parent_window):
        return
    process_teams(handle, driver, parent_window, url, league_name, writer)

def parse_and_write_to_csv(file_name, f, *args):
    with open(file_name, 'a', encoding="utf-8", newline='') as csv_file:
        writer=csv.writer(csv_file)
        writer.writerow(('Вид спорта', 'Лига', 'Команда',	'Матч',	'Дата', 'Итог',	'Счёт', 'Чёт/нечет', 'Тотал', 'Инд.тотал команды',
                        'Инд. чёт/ нечет', 'Тотал б/м [тотал]', 'Инд.тотал б/м [тотал]', 'Дом / Выезд', 'Овертайм', 'След. матч', 'Соперник'))
        args_list=list(args)
        args_list.append(writer)
        f(*args_list)

def parse_and_write_league_results(url, driver, league_name):
    parent_window=driver.current_window_handle
    file_name="leagues/Лига-{}.csv".format(league_name)
    args=[driver, parent_window, url, league_name]
    parse_and_write_to_csv(file_name, map(
        lambda handle: process_handle(handle, *args), driver.window_handles))
    driver.switch_to_window(parent_window)


def parse_football_team(league_name, team_name, driver):
    team=Team("soccer", league_name, team_name)
    WebDriverWait(driver, timeout=30).until(
        lambda x: x.find_element_by_id("fs-results"))
    soup=BeautifulSoup(driver.page_source, 'lxml')
    div=soup.find('div', id='fs-results')
    flag=False
    match_count=0
    for tbody in div.find_all("tbody"):
        if flag == True:
            break
        for tr in tbody.find_all("tr"):
            match_count += 1
            if match_count > 15:
                flag=True
                break
            place="дом"
            date=tr.find('td', class_='time').text.split()[0]
            team_self=tr.find('td', class_='team-home').text
            team_rival=tr.find('td', class_='team-away').text
            td_score=tr.find('td', class_='score')
            if len(td_score.contents) > 1:   # если есть доп время или пенальти
                self_score=int(td_score.contents[0].split(':')[0].strip())
                rival_score=int(td_score.contents[0].split(':')[1].strip())
                aet=td_score.find('span', class_='aet').text.strip()
                pat=re.compile("^\((.+)\)$")
                sc=pat.search(aet).group(1).strip().split(':')
                maintime={
                    'home-score': int(sc[0].strip()), 'guest-score': int(sc[1].strip())}
            else:
                self_score=int(
                    tr.find('td', class_='score').text.split(':')[0].strip())
                rival_score=int(
                    tr.find('td', class_='score').text.split(':')[1].strip())
                maintime=None
            if re.search(team_name, team_rival):
                team_rival=team_self
                self_score, rival_score=rival_score, self_score
                if maintime:
                    maintime['home-score'], maintime['guest-score']=maintime['guest-score'], maintime['home-score']
                place="выезд"
            team.matches.append(
                Match(date, team_name, team_rival, self_score, rival_score, place, maintime))
    return team


def write_team(writer, team):
    for match in team.matches:
        writer.writerow((team.sport, team.league, team.name, match.rival, match.date, match.result(), match.match_score(), match.odd_even(
        ), match.total(), match.score, match.ind_odd_even(), '-', '-', match.place, match.overtime(), team.next['date'], team.next['rival']))


if __name__ == '__main__':
    # Обернём исходную функцию
    parse=do_to_result(parse)
    parse("https://www.myscore.ru")
