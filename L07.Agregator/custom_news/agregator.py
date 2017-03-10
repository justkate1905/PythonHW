import time
import pickle
import re
from math import log
from sqlalchemy.ext.declarative import declarative_base
import requests
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker
from bottle import route, run, template, request
from bottle import redirect

from custom import get_news

domain = "https://news.ycombinator.com/"

Base = declarative_base()


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    class_label = Column(String)


engine = create_engine("sqlite:///newest_news.db")
Base.metadata.create_all(bind=engine)

session = sessionmaker(bind=engine)
s = session()
i = 0

r = requests.get(domain + "newest")
newsLst = get_news(r.text, 15)

for state in newsLst:
    row = s.query(News).filter(News.title == state['title'] and News.author == state['author']).count()
    news_base = []
    if row == 0:
        news = News(title=state['title'],
                    author=state['author'],
                    url=state['url'],
                    comments=state['comments'],
                    points=state['points'])
        news_base.append(news)
    s.add_all(news_base)
    s.commit()


@route('/')
@route('/news')
def news_list():
    s = session()
    rows = s.query(News).order_by(News.class_label).all()
    return template('agregator_news_template', rows=rows)


@route('/update_news')
def update_news():
    # 1. Получить данные с новостного сайта
    r = requests.get("https://news.ycombinator.com/newest")
    news_list = get_news(r.text, 10)
    for elem in news_list:
        # 2. Проверить каких новостей еще нет в БД. Будем считать,
        #    что каждая новость может быть уникально идентифицирована
        #    по совокупности двух значений: заголовка и автора
        row = s.query(News).filter(
            News.title == elem['title'] and News.author == elem['author']).count()
        # 3. Сохранить в БД те новости, которых там нет
        if row == 0:

            news = News(title=elem['title'],
                        author=elem['author'],
                        url=elem['url'],
                        comments=elem['comments'],
                        points=elem['points'])
            s.add(news)
            s.commit()
    definition_of_news_class()
    redirect('/news')


with open('data.pickle', 'rb') as f:
    data_new = pickle.load(f)


def definition_of_news_class():
    rows = s.query(News)
    good_p = data_new['good_mark']
    maybe_p = data_new['maybe_mark']
    never_p = data_new['never_mark']
    for row in rows:
        list_of_words = re.split(r'\W', row.title.lower() + ' ' + row.url.lower())
        for word in list_of_words:
            if data_new['good'].get(word) is None:
                continue
            else:
                good_p += log(data_new['good'][word])

            if data_new['maybe'].get(word) is None:
                continue
            else:
                maybe_p += log(data_new['maybe'][word])

            if data_new['never'].get(word) is None:
                continue
            else:
                never_p += log(data_new['never'][word])

        s.query(News).filter(News.id == row.id).update({'class_label': add_label_class(good_p, maybe_p, never_p, row)})
        s.commit()
        good_p = data_new['good_mark']
        maybe_p = data_new['maybe_mark']
        never_p = data_new['never_mark']


def add_label_class(g, m, n, _row):
    mark1 = ""
    if max(g, m, n) == g:
        mark1 = 'good'
    elif max(g, m, n) == m:
        mark1 = 'maybe'
    else:
        mark1 = 'never'

    return mark1

definition_of_news_class()
run(host='localhost', port=8080)
