import os, logging, argparse, glob, cloudscraper
import sqlite3
from sqlite3 import Error
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup as BSHTML
from urllib.request import Request, urlopen

list_manga=[]
db_file = '/data/Dockers/TOOLS/Komga/database.sqlite'
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
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
     
        
print(list_manga)