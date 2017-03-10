import time
import pickle
import re
from bs4 import BeautifulSoup
from math import log
from sqlalchemy.ext.declarative import declarative_base
import requests
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker
from bottle import route, run, template, request
from bottle import redirect

domain = "https://news.ycombinator.com/"


# формирование списка словарей с информацией о новостях
def get_news(text, info_count):
    # список словарей
    info = []
    # список новостей
    list_of_news = []
    list_of_titles = []
    list_of_info = []

    newText = text
    while len(info) < info_count:
        page = BeautifulSoup(newText, 'html.parser')
        tbl_list = page.table.findAll('table')
        tr_list = tbl_list[1].findAll('tr')

        for tr in tr_list:
            if tr.get('class') == ['athing']:
                list_of_titles.append(tr)
            elif tr.get('class') is None and len(list_of_titles) - len(list_of_info) == 1:
                list_of_info.append(tr)
        for i in range(0, len(list_of_titles)):
            list_of_news.append([])
            list_of_news[i].append(list_of_titles[i])
            list_of_news[i].append(list_of_info[i])

        for new in list_of_news:
            title = new[0].find('a', attrs={'class': 'storylink'}).text
            if title.find('Ask HN') != -1:
                continue
            else:
                author = new[1].find('a', attrs={'class': 'hnuser'}).string
                a_lst = new[1].findAll('a')
                if len(a_lst[len(a_lst) - 1].text.split(' ')) > 1:
                    comments = int(a_lst[len(a_lst) - 1].text.split(' ')[0])
                else:
                    comments = 0
                points = int(new[1].find('span', attrs={'class': 'score'}).text.split(' ')[0])

                url = new[0].find('a', attrs={'class': "storylink"}).get('href')

                info.append({'author': author,
                             'comments': comments,
                             'points': points,
                             'title': title,
                             'url': url})
        list_of_info.clear()
        list_of_news.clear()
        list_of_titles.clear()
        newUrl = domain + page.find('a', attrs={'class': 'morelink'}).get('href')
        #time.sleep(20)
        print(newUrl)

        newText = requests.get(newUrl).text

    return info


Base = declarative_base()


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


engine = create_engine("sqlite:///news.db")
Base.metadata.create_all(bind=engine)

session = sessionmaker(bind=engine)
s = session()
i = 0


# r = requests.get(domain + "newest")
# newsLst = get_news(r.text,1000)

# for state in newsLst:
#     row = s.query(News).filter(News.title == state['title'] and News.author == state['author']).count()
#     news_base = []
#     if row == 0:
#         print(row)
#         news = News(title=state['title'],
#                     author=state['author'],
#                     url=state['url'],
#                     comments=state['comments'],
#                     points=state['points'])
#         news_base.append(news)
#     s.add_all(news_base)
#     s.commit()


@route('/')
@route('/news')
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route('/add_label')
def add_label():
    # 1. Получить значения параметров label и id из GET-запроса
    new_label = request.query.get('label')
    id_of_news = request.query.get('id')
    # 2. Получить запись из БД с соответствующим id (такая запись только одна!)
    # 3. Изменить значение метки записи на значение label
    s.query(News).filter(News.id == id_of_news).update({'label': new_label})
    # 4. Сохранить результат в БД
    s.commit()
    redirect('/news')


@route('/update_news')
def update_news():
    # 1. Получить данные с новостного сайта
    r = requests.get("https://news.ycombinator.com/newest")
    news_list = get_news(r.text)
    for elem in news_list:
        # 2. Проверить каких новостей еще нет в БД. Будем считать,
        #    что каждая новость может быть уникально идентифицирована
        #    по совокупности двух значений: заголовка и автора
        row = s.query(News).filter(News.title == elem['title'] and News.author == elem['author']).count()
        # 3. Сохранить в БД те новости, которых там нет
        if row == 0:
            print(row)
            news = News(title=elem['title'],
                        author=elem['author'],
                        url=elem['url'],
                        comments=elem['comments'],
                        points=elem['points'])
            s.add(news)
            s.commit()
    redirect('/news')


dict_for_classes = {}


def statistic_for_classes(label):
    dict_for_classes[label] = {}
    rows = s.query(News).filter(News.label == label)
    counter = 0
    for row in rows:
        list_of_words = re.split(r'\W', row.title.lower() + ' ' + row.url.lower())
        for word in list_of_words:
            if (word == ''):
                continue
            elif (dict_for_classes[label].get(word) is None):
                dict_for_classes[label][word] = 1
                counter += 1
            else:
                dict_for_classes[label][word] += 1
                counter += 1
    for key in dict_for_classes[label].keys():
        dict_for_classes[label][key] /= counter
        #dict_for_classes[label][key] = log(dict_for_classes[label][key])
    dict_for_classes[label + '_mark'] = log(rows.count() / s.query(News).count())


statistic_for_classes('good')
statistic_for_classes('maybe')
statistic_for_classes('never')

with open('data.pickle', 'wb') as f:
    pickle.dump(dict_for_classes, f)

#run(host='localhost', port=8080)
