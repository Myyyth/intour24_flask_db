from bs4 import BeautifulSoup
import urllib.request
import ssl
from datetime import *
import parsing.db_model as db
from re import split

# from postgre_connect import DBConnect as db

SITE_URL = 'http://kazantravel.ru'
HOME_URL = 'http://kazantravel.ru/tours/'

DAY_THRESHOLD = 30


def get_html(url):
    context = ssl._create_unverified_context()
    response = urllib.request.urlopen(url, context=context)
    return response.read()


def _parse(url):
    soup = BeautifulSoup(url, 'html.parser')
    tours_block = soup.find('section', class_='tours-list')
    tours = []
    for item in tours_block.find_all('div', class_='tour-header'):
        link_tour = SITE_URL + item.a['href']
        tours.extend(parse_tour(get_html(link_tour)))
    return tours


def parse_tour(html):
    tour_soup = BeautifulSoup(html, 'html.parser')
    return parse_dates(tour_soup, parse_title(tour_soup), parse_price(tour_soup))


def parse_title(tour_soup):
    return tour_soup.find('h3', class_="booking-tour-name").text


def parse_price(tour_soup):
    return tour_soup.find('span', class_='tour-price-value').text


def parse_dates(tour_soup, title, price):
    schedule_soup = tour_soup.find('dl', class_='dl dl-horizontal booking-tour-days')
    weekday_names = [weekday_num(w) for w in schedule_soup.find_all('dt')]
    weekday_params = schedule_soup.find_all('dd')
    tours = []
    if not len(weekday_names) == 0:
        for i in range(len(weekday_names)):
            times = weekday_params[i].find_all('b')
            periods = weekday_params[i].find_all('small')
            for j in range(len(periods)):
                day = datetime.today()
                last_day = datetime.today() + timedelta(days=DAY_THRESHOLD + 1)
                while day < last_day:
                    if day.weekday() == weekday_names[i] and day_in_period(day, periods[j].text):
                        tour = db.Tour()
                        tour.title = title
                        tour.price = price
                        tour.date = day.strftime('%d.%m')
                        tour.time = times[2 * j].text + '-' + times[2 * j + 1].text
                        tours.append(tour)
                    day += timedelta(days=1)
    return tours


def weekday_num(w):
    w = w.text
    if w == 'Понедельник':
        return 0
    if w == 'Вторник':
        return 1
    if w == 'Среда':
        return 2
    if w == 'Четверг':
        return 3
    if w == 'Пятница':
        return 4
    if w == 'Суббота':
        return 5
    if w == 'Воскресенье':
        return 6


def day_in_period(day, str_period):
    _, str_start_date, str_end_date, _ = split(r'[(]|[)]|[-]', str_period)
    start_date = datetime.strptime(str_start_date, '%d.%m.%Y')
    end_date = datetime.strptime(str_end_date, '%d.%m.%Y')
    if start_date <= day <= end_date:
        return True
    return False


def parse():
    return _parse(get_html(HOME_URL))


if __name__ == '__main__':
    db.migrate()
    # database = DBConnect('dbafp', 'user', 'pass')

    parse()

    # database.close()
