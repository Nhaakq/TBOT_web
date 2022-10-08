import os, logging, argparse, glob, cloudscraper
import sqlite3
from sqlite3 import Error
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup as BSHTML
from urllib.request import Request, urlopen

app = Flask(__name__)
#app.config[SQLALCHEMY_TRACK_MODIFICATIONS] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
db = SQLAlchemy(app)
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW...'
scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        }
    )


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id



@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        input_user = request.form['content']
        url_search= 'https://new.reaperscans.fr/?s='
        url_post= '&post_type=wp-manga'
        
        url=url_search+input_user.replace(' ','+')+url_post
        req = Request(url)
        req.add_header('User-Agent',user_agent)
        page = urlopen(req)
        soup = BSHTML(page,features="html.parser")
        images = soup.findAll('div', {'class': 'post-title'})
        manga_names=[]
        for image in images:
            manga_names.append(image.find('a').contents[0])      
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/admin', methods=['POST','GET'])
def admin_page():
    return render_template('admin.html')

@app.route('/todolist', methods=['POST','GET'])
def todolist_page():
    return render_template('todolist.html')

@app.route('/mangas', methods=['POST','GET'])
def mangas_page():
    if request.method == ['POST']:
        return 'le IF fonctionne'
    else:
        
        list_manga=[]
        db_file = '/data/Dockers/TOOLS/Komga/database.sqlite'
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            return e
        cur = conn.cursor()
        cur.execute("SELECT NAME, ID FROM SERIES;")
        rows = cur.fetchall()
        cura = conn.cursor()
        cura.execute("SELECT max(READ_PROGRESS.READ_DATE) as Last_Date,BOOK.NAME as Numero_Chap,SERIES.NAME as Name FROM READ_PROGRESS INNER JOIN BOOK ON BOOK.ID = READ_PROGRESS.BOOK_ID INNER JOIN SERIES ON SERIES.ID = BOOK.SERIES_ID WHERE COMPLETED=1 AND SERIES.NAME='arcane-sniper' GROUP BY SERIES.NAME;")
        infos_komga = cura.fetchall()
        for data_name in rows:
            dict_manga={}
            manga_name = data_name[0]
            manga_id = data_name[1]
            url_desc = 'https://new.reaperscans.fr/series/'+ manga_name
            cur.execute("SELECT max(READ_PROGRESS.READ_DATE),BOOK.NAME,SERIES.NAME FROM READ_PROGRESS INNER JOIN BOOK ON BOOK.ID = READ_PROGRESS.BOOK_ID INNER JOIN SERIES ON SERIES.ID = BOOK.SERIES_ID WHERE COMPLETED=1 AND SERIES.NAME='"+manga_name+"' GROUP BY SERIES.NAME;")
            infos_komga = cur.fetchall()

            page = scraper.get(url_desc).text
            soup = BSHTML(page,features="html.parser")
            images = soup.findAll('div', {'class': 'container'})

            last_chapter_url = images[1].find('div', {'class': 'chapter-link'}).a.get('href')
            last_chapter_number = last_chapter_url.split('/')[5].split('-')[1]
            url_img=images[0].find('img', {'class': 'img-responsive'})['src']
            summary_manga = images[0].find('div', {'class': 'summary__content'}).text
            dict_manga['url']=url_img
            dict_manga['summary']=summary_manga
            dict_manga['name']=manga_name
            dict_manga['last_chapter_web']=last_chapter_number
            dict_manga['last_chapter_web_url']=last_chapter_url
            dict_manga['manga_url']='https://reader.nhaak.com/series/'+manga_id
            if len(infos_komga)>0:   
                dict_manga['last_chapter_read']=infos_komga[0][1].split('-')[1]
                dict_manga['reading_date']=infos_komga[0][0].split(' ')[0]
            # else:
            #     dict_manga['last_chapter']='Chaptire-1'
            #     dict_manga['reading_date']='Not Yet.'

            list_manga.append(dict_manga)
        
        return render_template('mangas.html', list_manga=list_manga)

@app.route('/search-manga', methods=['POST','GET'])
def search_manga_page():
    db_file = '/data/Dockers/TOOLS/Komga/database.sqlite'
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        return e
    cur = conn.cursor()
    cur.execute("SELECT NAME FROM SERIES;")
    rows = cur.fetchall()
    if request.method == 'POST':
            searched_term = request.form['query']
            searched_term = searched_term.replace(' ','+').lower()
            url_desc = 'https://new.reaperscans.fr/webtoon/'
            search_page = scraper.get(url_desc).text
            bsoup = BSHTML(search_page,features="html.parser")
            images = bsoup.findAll('div', {'class': 'container'})
            
            return render_template('search_manga.html', searched_term=searched_term)
    elif request.method == 'GET':
        list_infos_manga=[]
        url_get_list = 'https://new.reaperscans.fr/webtoon/?m_orderby=new-manga'
        search_page = scraper.get(url_get_list).text
        bsoup = BSHTML(search_page,features="html.parser")
        images = bsoup.findAll('div', {'class': 'tab-content-wrap'})

        each_manga = images[0].findAll('div',{'class': 'col-4 col-md-2 badge-pos-2'})

        for each in each_manga:
            if each.a.get('title').replace(' ','-') not in rows[0]:
                data_mangas={}
                data_mangas['url']=each.a.get('href')
                data_mangas['titre']=each.a.get('title')
                data_mangas['image']=each.img.get('src')
                data_mangas['votes']=int(float(each.find('span', {'class': 'score font-meta total_votes'}).text))
                data_mangas['last_chapter']=each.find('a', {'class': 'btn-link'}).text
                list_infos_manga.append(data_mangas)

        return render_template('search_manga.html', list_infos_manga=list_infos_manga)

if __name__ == "__main__": 
    app.run(debug=True)