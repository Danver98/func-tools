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

from match import Match
from team import Team


def filter_leagues_by_pattern_and_then_apply_func(collection, pattern, pattern_condition_function, apply, *helper_args):
    filtered_collection = filter_with_pattern(
        collection, pattern_condition_function, pattern)
    apply_with_index_and_args(filtered_collection, apply, *helper_args)


def apply_with_index_and_args(collection, function, *helper_args):
    for i in range(len(collection)):
        function(collection[i], i, *helper_args)


def parse_leagues(driver, url):
    pattern = re.compile("^.*(Cup|Copa|Кубок|кубок).*$")
    for index, league in enumerate(driver.find_elements_by_class_name("head_ab")):
        league_name = league.find_element_by_class_name(
            "name").text.strip()
        when((league.find_element_by_tag_name('span').text == "Таблица" and pattern.search(league_name) == None), parse_single_league,
             url, driver, league, league_name, index)
             
#Вынесли условие проверки из when, абстрагировали сам паттерн
def item_is_table_and_out_of_pattern(pattern, item):
    name = item.find_element_by_class_name("name").text.strip()
    tag_elem = item.find_element_by_tag_name('span')
    if tag_elem.text == "Таблица" and pattern.search(name) == None:
        return True
    return False

#Фильтруем по функции, проверяющей на соответствие паттерну
def filter_with_pattern(collection, pattern_condition_function, pattern):
    new_collection = []
    for item in collection:
        when(pattern_condition_function(pattern, item), lambda new_collection,
             item: new_collection.append(item))
    return new_collection


def when(condition, then, *args):
    if(condition):
        then(*args)


def parse_single_league(league, index, url, driver):
    league_name = league.find_element_by_class_name("name").text.strip()
    league.find_element_by_tag_name('span').click()
    league_results(url, driver, league_name, index)


def parse_leagues(driver, url):
    collection = driver.find_elements_by_class_name("head_ab")
    pattern = re.compile("^.*(Cup|Copa|Кубок|кубок).*$")
    pattern_condition_function = item_is_table_and_out_of_pattern
    helper_args = [url, driver]
    filter_leagues_by_pattern_and_then_apply_func(
        collection, pattern, pattern_condition_function, parse_single_league, helper_args)


def get_prepared_driver(url):
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(url)
    driver.find_element_by_class_name("soccer").click()
    WebDriverWait(driver, timeout=30).until(
        lambda x: x.find_element_by_class_name("table-main"))
    return driver


def parse(url):
    while True:
        driver = None
        try:
            driver = getPreparedDriver(url)
            parse_leagues(driver, url)
            driver.close()
        except TimeoutError:
            print("=========Timeout error=========")
            if driver != None:
                if isinstance(driver, webdriver.Firefox):
                    driver.close()
            continue
        except OSError as e:
            print(e)
            print("=======Waiting...=======")
            if driver != None:
                if isinstance(driver, webdriver.Firefox):
                    driver.close()
            continue
        else:
            driver.quit()
            break


def league_results(url, driver, league_name, index):
    link_pattern = re.compile(".*\('(.+)'\);")
    # сохраним ссылку на родительское окно
    parent_window = driver.current_window_handle
    file_name = "leagues/league-{}.csv".format(index + 1)
    with open(file_name, 'a', encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(('Вид спорта', 'Лига', 'Команда',	'Матч',	'Дата', 'Итог',	'Счёт', 'Чёт/нечет', 'Тотал', 'Инд.тотал команды',
                        'Инд. чёт/ нечет', 'Тотал б/м [тотал]', 'Инд.тотал б/м [тотал]', 'Дом / Выезд', 'Овертайм', 'След. матч', 'Соперник'))
        for handle in driver.window_handles:
            if handle != parent_window:
                driver.switch_to_window(handle)
                WebDriverWait(driver, timeout=10).until(
                    lambda x: x.find_element_by_class_name("glib-stats-data"))
                # команды
                for span in driver.find_elements_by_class_name("team_name_span"):
                    team_name = span.find_element_by_tag_name(
                        "a").text.strip()  # ?
                    onclick = span.find_element_by_tag_name(
                        "a").get_attribute("onclick")
                    link = link_pattern.search(onclick).group(1)
                    current_window = driver.current_window_handle
                    driver.switch_to_window(parent_window)
                    driver.execute_script("window.open();")
                    tab_handle = None
                    for index, handle in enumerate(driver.window_handles):
                        if index == 1:
                            tab_handle = handle
                            driver.switch_to_window(handle)
                            driver.get(url+link+'results')
                            break
                    driver.switch_to_window(tab_handle)
                    next_ = str(url+link)
                    team = parse_football_team(
                        league_name, team_name, driver, next_)
                    write_team(writer, team)
                    driver.close()
                    driver.switch_to_window(current_window)
                driver.close()
    # переключение на родительское перенесено на более вложенный уровень
    driver.switch_to_window(parent_window)


def parse_football_team(league_name, team_name, driver):
    team = Team("soccer", league_name, team_name)
    WebDriverWait(driver, timeout=30).until(
        lambda x: x.find_element_by_id("fs-results"))
    soup = BeautifulSoup(driver.page_source, 'lxml')
    div = soup.find('div', id='fs-results')
    flag = False
    match_count = 0
    for tbody in div.find_all("tbody"):
        if flag == True:
            break
        for tr in tbody.find_all("tr"):
            match_count += 1
            if match_count > 15:
                flag = True
                break
            place = "дом"
            date = tr.find('td', class_='time').text.split()[0]
            team_self = tr.find('td', class_='team-home').text
            team_rival = tr.find('td', class_='team-away').text
            td_score = tr.find('td', class_='score')
            if len(td_score.contents) > 1:   # если есть доп время или пенальти
                self_score = int(td_score.contents[0].split(':')[0].strip())
                rival_score = int(td_score.contents[0].split(':')[1].strip())
                aet = td_score.find('span', class_='aet').text.strip()
                pat = re.compile("^\((.+)\)$")
                sc = pat.search(aet).group(1).strip().split(':')
                maintime = {
                    'home-score': int(sc[0].strip()), 'guest-score': int(sc[1].strip())}
            else:
                self_score = int(
                    tr.find('td', class_='score').text.split(':')[0].strip())
                rival_score = int(
                    tr.find('td', class_='score').text.split(':')[1].strip())
                maintime = None
            if re.search(team_name, team_rival):
                team_rival = team_self
                self_score, rival_score = rival_score, self_score
                if maintime:
                    maintime['home-score'], maintime['guest-score'] = maintime['guest-score'], maintime['home-score']
                place = "выезд"
            team.matches.append(
                Match(date, team_name, team_rival, self_score, rival_score, place, maintime))
    return team


def write_team(writer, team):
    for match in team.matches:
        writer.writerow((team.sport, team.league, team.name, match.rival, match.date, match.result(), match.match_score(), match.odd_even(
        ), match.total(), match.score, match.ind_odd_even(), '-', '-', match.place, match.overtime(), team.next['date'], team.next['rival']))


if __name__ == '__main__':
    parse("https://www.myscore.ru")
