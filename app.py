from flask import Flask, render_template, url_for, request, redirect, send_file, session
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from flask_uploads import UploadSet, configure_uploads, DATA
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter
from flask_mail import Mail
import pandas as pd
import re
import bs4 as bs
import lxml
import urllib.request
from urllib.parse import quote
from urllib.request import Request, urlopen
import urllib

#sentiment_analysis_modules
import twitter_streaming as ts
import threading
import json
import requests
#import sentiment_module as sa

proxy_support = urllib.request.ProxyHandler({"http":"http://61.233.25.166:80"})
opener = urllib.request.build_opener(proxy_support)
urllib.request.install_opener(opener)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netflixentUser.db'
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_APP_NAME'] = 'NET FLIXENT'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_LOGIN_ENDPOINT'] = ''

db = SQLAlchemy(app)

files =  UploadSet('files', DATA)
app.config['UPLOADED_FILES_DEST'] = 'static/files'
configure_uploads(app, files)


class netflixentUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable = False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    confirmed_at = db.Column(db.DateTime())

db_adapter = SQLAlchemyAdapter(db, netflixentUser)
user_manager = UserManager(db_adapter, app)

@app.route('/')
def index():
         return render_template('index.html')

@app.route('/trailernotfound')
def trailernotfound():
    return render_template('trailernotfound.html')

@app.route('/recomendations')
def recomendations():
    return render_template('recomendations.html')

@app.route('/movienotfound')
def movienotfound():
    return render_template('movienotfound.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/showtimes')
def showtimes():
    return render_template('showtimes.html')

@app.route('/favorites')
def favorites():
    return render_template('favorites.html')

@app.route('/howitworks')
def howitworks():
    return render_template('howitworks.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/trending_news')
def trending_news():
    return render_template('trending_news.html')

@app.route('/conditions')
def conditions():
    return render_template('conditions.html')

@app.route('/favs')
def favs():
    return render_template('favs.html')

@app.route('/whatissentiment')
def whatissentiment():
    return render_template('whatissentiment.html')

@app.route('/notfound2')
def notfound2():
    return render_template('notfound2.html')

@app.route('/in_theatres',methods=['GET', 'POST'] )
def in_theatres():
    (in_cinemas,heading) = getincinemas()
    return render_template('in_theatres.html',in_cinemas=in_cinemas,heading=heading)

@app.route('/popular_movies',methods=['GET', 'POST'] )
def popular_movies():
    popular_m = getmostpopular()
    return render_template('popular_movies.html',popular_m=popular_m)

@app.route('/upcoming_movies',methods=['GET', 'POST'] )
def upcoming_movies():
    (upcoming_m,heading2) = getupcoming()
    return render_template('upcoming_movies.html',upcoming_m=upcoming_m,heading2=heading2)

@app.route('/recent_dvd',methods=['GET', 'POST'] )
def recent_dvd():
    (recent_dvd_m) = getdvd()
    return render_template('recent_dvd.html',recent_dvd_m=recent_dvd_m)

@app.route('/streaming',methods=['GET', 'POST'] )
def streaming():
    movie_input = session.get('my_var')
    session['movie_input'] = movie_input
    title = session.get('title')
    poster_ref = session.get('poster_ref')
    poster = session.get('poster')
    trailer = session.get('trailer')
    amazon = session.get('amazon')
    itunes = session.get('itunes')
    vudu = session.get('vudu')
    return render_template('streaming.html',name=movie_input,title=title,poster_ref=poster_ref,poster=poster,trailer=trailer,amazon=amazon,itunes=itunes,vudu=vudu)

@app.route('/velocity',methods=['GET', 'POST'] )
def velocity():
    movie_input = session.get('my_var')
    session['movie_input'] = movie_input
    title = session.get('title')
    poster_ref = session.get('poster_ref')
    poster = session.get('poster')
    trailer = session.get('trailer')
    imdb_rating = session.get('imdb_rating')
    imdb_total_users = session.get('imdb_total_users')
    all_tomatometer = session.get('all_tomatometer')
    avg_rateall = session.get('avg_rateall')
    top_tomameter = session.get('top_tomameter')
    avg_ratetop = session.get('avg_ratetop')
    audiencescore = session.get('audiencescore')
    useravg= session.get('useravg')
    score = session.get('score')
    rating_value = session.get('rating_value')
    best_rating_value = session.get('best_rating_value')
    metacriticscore = session.get('metacriticscore')
    usermetascore = session.get('usermetascore')
    fandango_score = session.get('fandango_score')
    try:
        imdb = float(imdb_rating)*9.8
        alls = float(all_tomatometer.split("%")[0])
        top = float(top_tomameter.split("%")[0])
        avg_all = float(avg_rateall.split("/")[0])*10
        avg_top = float(avg_ratetop.split("/")[0])*10
        aud = float(audiencescore.split("%")[0])
        avg_user = float(useravg.split("/")[0])*20
        mrq = float(score)
        imdb = round(imdb,2)
        roger_score = float((float(rating_value)/float(best_rating_value))*100)
        metac = float(metacriticscore)
        userm = float(float(usermetascore)*10)
        fand = float(fandango_score)*19.5
        rt_eq = round(float((alls + top + avg_all + avg_top + avg_user)/5),1)
        meta_eq = round(float((metac + userm)/2),1)
        sums = imdb + alls + top + avg_all + avg_top + aud + avg_user + mrq + roger_score + metac + userm + fand
        vel = float(sums / 12)
        vel = round(vel,1)

    except ValueError:
        vel = "N/A"
    return render_template('velocity.html',name=movie_input,title=title,poster_ref=poster_ref,poster=poster,trailer=trailer,vel=vel,imdb=imdb,rt_eq=rt_eq,mrq=mrq,roger_score=roger_score,fand=fand,meta_eq=meta_eq )

@app.route('/trailerpage')
def trailerpage():
    trailer = session.get('trailer')
    print("tttttt",trailer)
    return render_template('trailerpage.html',trailer=trailer)

@app.route('/sentiment',methods=['GET', 'POST'] )
def sentiment():
    movie_input = session.get('my_var')
    session['movie_input'] = movie_input
    title = session.get('title')
    poster_ref = session.get('poster_ref')
    poster = session.get('poster')
    trailer = session.get('trailer')
    twitter_tag = session.get('twitter_tag')

    s = open('trash.txt','w')
    s.write(twitter_tag.replace("#",""))
    s.close()

    thr = threading.Thread(target=ts.streaminging,args=(twitter_tag,))
    thr.start()
    return render_template('sentiment.html',name=movie_input,title=title,twitter_tag=twitter_tag,poster=poster,trailer=trailer,poster_ref=poster_ref)

@app.route('/chart', methods=['GET','POST'])
def chart():
    return render_template('chart.html')

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():

    favs = open("static/favs.txt",'a')
    favs.write(jsdata)
    favs.close()
    return jsdata

@app.route('/rating',methods=['GET', 'POST'] )
def rating():
    movie_input = session.get('my_var')
    session['movie_input'] = movie_input
    title = session.get('title')
    poster_ref = session.get('poster_ref')
    poster = session.get('poster')
    trailer = session.get('trailer')
    imdb_rating = session.get('imdb_rating')
    imdb_total_users = session.get('imdb_total_users')
    all_tomatometer = session.get('all_tomatometer')
    avg_rateall = session.get('avg_rateall')
    top_tomameter = session.get('top_tomameter')
    avg_ratetop = session.get('avg_ratetop')
    audiencescore = session.get('audiencescore')
    useravg= session.get('useravg')
    score = session.get('score')
    rating_value = session.get('rating_value')
    best_rating_value = session.get('best_rating_value')
    metacriticscore = session.get('metacriticscore')
    usermetascore = session.get('usermetascore')
    fandango_score = session.get('fandango_score')
    fandango_fans = session.get('fandango_fans')
    return render_template('rating.html',name=movie_input,title=title,poster_ref=poster_ref,poster=poster,trailer=trailer,imdb_rating=imdb_rating,imdb_total_users=imdb_total_users,all_tomatometer=all_tomatometer,top_tomameter=top_tomameter,audiencescore=audiencescore,score=score,metacriticscore=metacriticscore,usermetascore=usermetascore,avg_ratetop=avg_ratetop,avg_rateall=avg_rateall,useravg=useravg,rating_value=rating_value,best_rating_value=best_rating_value,fandango_score=fandango_score,fandango_fans=fandango_fans)

@app.route('/articles_news',methods=['GET', 'POST'] )
def articles_news():
    movie_input = session.get('my_var')
    session['movie_input'] = movie_input
    title = session.get('title')
    poster_title = session.get('poster_title')
    release_yr = session.get('release_yr')
    poster_ref = session.get('poster_ref')
    poster = session.get('poster')
    trailer = session.get('trailer')
    (all_zipped,count_all) = getarticles(poster_title,release_yr)
    return render_template('articles_news.html',all_zipped=all_zipped,count_all=count_all,name=movie_input,title=title,poster_ref=poster_ref,poster=poster,trailer=trailer)

@app.route('/results', methods=['GET', 'POST'] )
@login_required
def results():
    try:

        if(request.method == "POST"):
            movie_input = request.form['movie_name']
        else:
            movie_input = session.get('movie_input')

        session['my_var'] = movie_input
        (title,imdb_rating,imdb_total_users,duration,release_yr,poster,poster_ref,trailer,director,writer,stars,story,genres,countr,lang,releasedate,budge,opening_weekend,gross_value,poster_title,twitter_tag) = getimdb(movie_input)
        (critics_consensus,all_tomatometer,avg_rateall,rev_countall,freshall,rottenall,top_tomameter,avg_ratetop,rev_counttop,freshtop,rottentop,audiencescore,useravg,userrate,studio,amazon,itunes,vudu) = gettomatoes(poster_title,release_yr)
        (published_date,author_name,roger_review,rating_value,best_rating_value,movie_rated) = getRogerEbert(poster_title,release_yr,releasedate)
        (mrqe_rated,full_cast,movie_synopsis,user_rating_src,critic_rating_src,score) = getmrqe(poster_title,title,release_yr)
        (metacriticscore,usermetascore,pos_meta,mix_meta,neg_meta,pos_user,mix_user,neg_user,tot_meta,tot_user) = getMetacritic(poster_title,release_yr)
        (fandango_score,fandango_fans) = getFandango(poster_title,release_yr)

        session['title'] = title
        session['poster_ref'] = poster_ref
        session['poster'] = poster
        session['trailer'] = trailer
        session['imdb_rating'] = imdb_rating
        session['imdb_total_users'] = imdb_total_users
        session['all_tomatometer'] = all_tomatometer
        session['avg_rateall'] = avg_rateall
        session['top_tomameter'] = top_tomameter
        session['avg_ratetop'] = avg_ratetop
        session['audiencescore'] = audiencescore
        session['useravg'] = useravg
        session['score'] = score
        session['rating_value'] = rating_value
        session['best_rating_value'] = best_rating_value
        session['metacriticscore'] = metacriticscore
        session['usermetascore'] = usermetascore
        session['poster_title'] = poster_title
        session['release_yr'] = release_yr
        session['twitter_tag'] = twitter_tag
        session['fandango_score'] = fandango_score
        session['fandango_fans'] = fandango_fans
        session['amazon'] = amazon
        session['itunes'] = itunes
        session['vudu'] = vudu
        print(user_rating_src)
        return render_template('results.html',
                            name=movie_input,
                            storie = story,
                            title=title,
                            imdb_rating=imdb_rating,
                            imdb_total_users=imdb_total_users,
                            duration=duration,
                            release_yr=release_yr,
                            poster=poster,
                            poster_ref=poster_ref,
                            writer=writer,
                            director=director,
                            stars=stars,
                            countr=countr,
                            lang=lang,
                            releasedate=releasedate,
                            budge=budge,
                            opening_weekend=opening_weekend ,
                            gross_value=gross_value,
                            trailer=trailer,
                            genres=genres,
                            poster_title=poster_title,
                            critics_consensus=critics_consensus,
                            all_tomatometer=all_tomatometer,
                            avg_rateall=avg_rateall,
                            rev_countall=rev_countall,
                            freshall=freshall,
                            rottenall=rottenall,
                            top_tomameter=top_tomameter,
                            avg_ratetop=avg_ratetop,
                            rev_counttop=rev_counttop,
                            freshtop=freshtop,
                            rottentop=rottentop,
                            audiencescore=audiencescore,
                            useravg=useravg,
                            userrate=userrate,
                            studio=studio,
                            published_date=published_date,
                            author_name=author_name,
                            roger_review = roger_review,
                            rating_value=rating_value,
                            best_rating_value=best_rating_value,
                            movie_rated=movie_rated,
                            mrqe_rated=mrqe_rated,
                            full_cast=full_cast,
                            movie_synopsis=movie_synopsis,
                            user_rating_src = user_rating_src,
                            critic_rating_src=critic_rating_src,
                            score=score,
                            metacriticscore = metacriticscore,
                            usermetascore=usermetascore,
                            pos_meta=pos_meta,
                            mix_meta=mix_meta,
                            neg_meta=neg_meta,
                            pos_user=pos_user,
                            mix_user=mix_user,
                            neg_user=neg_user,
                            tot_meta=tot_meta,
                            tot_user=tot_user,
                            fandango_fans=fandango_fans,
                            fandango_score=fandango_score
                            )
    except IndexError:
        return render_template('notfound.html')

proxies = {
    "http": 'http://51.15.86.88:3128',
    "https": 'http://51.15.86.88:3128'
}
def getimdb(movie_input):
    imdb_rate = "NA"
    opening_week = 'NOT AVAILABLE'
    budgets = 'NOT AVAILABLE'
    gross = 'NOT AVAILABLE'
    language = 'NOT AVAILABLE'
    releasedate = 'NOT AVAILABLE'
    dur = 'NOT AVAILABLE'
    release = 'NOT AVAILABLE'
    dirctor = 'NOT AVAILABLE'
    wrter = 'NOT AVAILABLE'
    country = 'NOT AVAILABLE'
    trailer_url = "trailernotfound"
    poster_ref = "#"
    poster_href = "#"
    poster_url = "#"
    storyline = "NOT AVAILABLE"
    imdb_users = "NA"
    poster_ttle = "NA"

    name1 = movie_input.replace(" ","+")
    print(name1)

    sauce = requests.get("http://www.imdb.com/find?ref_=nv_sr_fn&q="+name1+"&s=all",proxies=proxies).text

    soup = bs.BeautifulSoup(sauce, 'lxml')
    #creating bs for findall
    s1 = soup.find_all("td", {"class" : "result_text"})
    data = []
    titles_all = []
    for titles in s1:
        if ("(TV" not in titles.text) and ("(Video" not in titles.text):
            titles_all.append(titles.text)
            data.append(titles.a.get('href'))

    #print(titles_all)
    main_url = data[0]
    sauce2 = requests.get("http://www.imdb.com"+main_url,proxies=proxies).text
    soup2= bs.BeautifulSoup(sauce2,'lxml')
    s = soup2.find_all('div', class_="title_wrapper")

    for ttle in s:
        movie_title = ttle.h1.text
        result = ''.join([i for i in movie_title if not i.isdigit()])
        new_result = result.replace("\xa0()","")
        new_result2 = new_result.replace("-","")
        new_result3 = new_result2.replace(" ","")
        new_result4 = new_result3.replace("()","")
        new_result5 = new_result4.replace(":","")
        new_result6 = new_result5.replace("'","")
        twitter_tag = "#"+new_result6

    s2= soup2.find_all('div', class_='ratings_wrapper')

    for rate in s2:
        imdb_rate = rate.div.strong.span.text
        imdb_users = rate.a.span.text

    s3= soup2.find_all('div', class_='title_wrapper')

    for j in s3:
        try:
            dur = j.time.text
            release = j.a.string
        except AttributeError:
            break

    s4 = soup2.find_all('div', class_="poster")

    for ps in s4:
        poster_url = ps.img.get('src')


    s0 = soup2.find_all('div', class_="poster")

    for k in s0:
        try:
            p = k.a
            l = p.get('href')
            poster_href = "http://www.imdb.com"+l

        except AttributeError:
            break

    s5 = soup2.find_all('div', class_="slate")

    for k in s5:
        t = k.a
        l2 = t.get('href')
        trailer_url = "http://www.imdb.com"+l2


    s7 = soup2.find_all('div', class_="inline canwrap")

    for story in s7:
        storyline = story.p.text

    s8 = soup2.find_all('div', itemprop="genre")
    for urls in s8:
        gnre = urls.text
        gnr=gnre.replace("|","")
        genre= gnr.replace("Genres:","")
    s20 = soup2.find_all('div', class_="credit_summary_item")
    for z in s20:
        test = z.h4.text
        if(test == "Director:") or (test == "Directors:"):
            dirr = z.text
            drctor = dirr.replace("Director:","")
            dirctor = drctor.replace("Directors:","")

        elif(test == "Writer:") or (test == 'Writers:'):
            write = z.text
            wrtr = write.replace("Writer:","")
            wrter = wrtr.replace("Writers:","")

        elif(test == "Stars:") or (test == "Star:"):
            cast = z.text
            ss = cast.replace("See full cast & crew »","")
            star = ss.replace("|"," ")
            st = star.replace("Stars:","")
            strs = st.replace("Star:","")

    s9 = soup2.find_all('div', class_="txt-block")
    for details in s9:
        try:
            head = details.h4.text
            if (head == "Country:"):
                d1 = details.text
                dnew1 = d1.replace("|","")
                cuntry = dnew1.replace("See more »","")
                country = cuntry.replace("Country:","")
            if (head == "Language:"):
                d2 = details.text
                dnew2 = d2.replace("|","")
                langage = dnew2.replace("See more »","")
                language = langage.replace("Language:","")
            if (head == "Release Date:"):
                d3 = details.text
                dnew3 = d3.replace("|","")
                relese_date = dnew3.replace("See more »","")
                release_date = relese_date.replace("Release Date: ","")
            if (head == "Budget:"):
                d4 = details.text
                dnew4 = d4.replace("|","")
                budget = dnew4.replace("See more »","")
                budgets = budget.replace("Budget: ","")
            if (head == "Opening Weekend:"):
                d5 = details.text
                dnew5 = d5.replace("|","")
                opning_week = dnew5.replace("See more »","")
                opening_week = opning_week.replace("Opening Weekend: ","")
            if (head == "Gross:"):
                d6 = details.text
                dnew6 = d6.replace("|","")
                gros = dnew6.replace("See more »","")
                gross = gros.replace("Gross: ","")

        except AttributeError:
            break

    trial = soup2.find_all('div', class_='poster')
    for i in trial:
        main_title = i.img.get('title')
        poster_ttle = main_title.replace(" Poster","")

    return (movie_title,imdb_rate,imdb_users,dur,release,poster_url,poster_href,trailer_url,dirctor,wrter,strs, storyline,genre,country,language,release_date,budgets,opening_week,gross,poster_ttle,twitter_tag)

def gettomatoes(poster_title,release_yr):
    try:
        if ("Bahubali" in poster_title):
            poster_title = "Baahubali 2: The Conclusion (2017)"
        elif("The Avengers" in poster_title):
            poster_title = "Marvels the Avengers"
        t = poster_title.replace(" ()","")
        t = t.replace(" -","")
        t = t.replace(" :","")
        t = t.replace(" ","_")
        t = t.replace(".","")
        t = t.replace("-","")
        t = t.replace(",","")
        t = t.replace("'","")
        t = t.replace(" ","")
        t = t.replace(":","")
        t = t.replace("-","")
        t = t.replace("!","")
        t = t.replace('(',"")
        t = t.replace(')',"")
        t = t.replace("&","and")
        print("njejn",t)
        consensus = "NOT AVAILABLE"
        all_meter = "NOT AVAILABLE"
        avg_rate_all= "NOT AVAILABLE"
        rev_count_all= "NOT AVAILABLE"
        fresh_all= "NOT AVAILABLE"
        rotten_all= "NOT AVAILABLE"
        top_meter= "NOT AVAILABLE"
        avg_rate_top= "NOT AVAILABLE"
        rev_count_top= "NOT AVAILABLE"
        fresh_top= "NOT AVAILABLE"
        rotten_top= "NOT AVAILABLE"
        audience_score= "NOT AVAILABLE"
        user_avg= "NOT AVAILABLE"
        user_rate= "NOT AVAILABLE"
        studio = "NA"
        movietitle = t.lower()

        sauce = urllib.request.urlopen("https://www.rottentomatoes.com/m/"+movietitle+"_"+release_yr,timeout=10000).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')

        soup2 = soup.find_all('div',id="all-critics-numbers")
        for con in soup2:
            consensus = con.p.text
            consensus = consensus.replace("Critics Consensus:","")

        tomatometer_all = soup2[0].find_all('span',class_="meter-value superPageFontColor")
        for al in tomatometer_all:
            all_meter = al.text

        all_critics = soup2[0].find_all('div', class_="superPageFontColor")
        for a in all_critics:
            try:
                i = a.span.text
                if (i == "Average Rating: "):
                    avg_rate = a.text
                    avg_rate_all = avg_rate.replace("Average Rating:","")
                    avg_rate_all = avg_rate_all.replace("/10","")
                    avg_rate_all = avg_rate_all.replace(" ","")
                elif(i == "Reviews Counted: "):
                    rev_count = a.text
                    rev_count_all = rev_count.replace("Reviews Counted:","")

                elif(i == "Fresh: "):
                    fresh = a.text
                    fresh_all = fresh.replace("Fresh:","")

                elif(i == "Rotten: "):
                    rotten = a.text
                    rotten_all = rotten.replace("Rotten:","")

            except AttributeError:
                break

        soup3 = soup.find_all('div',id="top-critics-numbers")
        tomatometer_top = soup3[0].find_all('span',class_="meter-value superPageFontColor")
        for top in tomatometer_top:
            top_meter = top.text


        top_critics = soup3[0].find_all('div', class_="superPageFontColor")
        for b in top_critics:
            try:
                i = b.span.text
                if (i == "Average Rating: "):
                    avg_rate = b.text
                    avg_rate_top = avg_rate.replace("Average Rating:","")
                    avg_rate_top = avg_rate_all.replace("/10","")
                    avg_rate_top = avg_rate_all.replace(" ","")

                elif(i == "Reviews Counted: "):
                    rev_count = b.text
                    rev_count_top = rev_count.replace("Reviews Counted:","")

                elif(i == "Fresh: "):
                    fresh = b.text
                    fresh_top = fresh.replace("Fresh:","")

                elif(i == "Rotten: "):
                    rotten = b.text
                    rotten_top = rotten.replace("Rotten:","")

            except AttributeError:
                break

        audience = soup.find_all('div', class_="audience-score meter")
        for c in audience:
            audience_score = c.text
            audience_score = audience_score.replace("liked it","")
            audience_score = audience_score.replace(" ","")

        user_reviews = soup.find_all('div', class_="audience-info hidden-xs superPageFontColor")
        for d in user_reviews:
            ans = d.text
            ans= ans.replace("Average Rating:","")
            ans = ans.replace("User Ratings:","")
            user_avg=ans[0:20]
            user_avg = user_avg.replace(" ","")
            user_rate = ans[21 : ]
            user_avg = user_avg.replace(" ","")
            user_avg = user_avg.replace("/5","")
            user_avg = user_avg.replace(" ","")
            std = soup.find_all('a')
        for e in std:
            test= e.get('target')
            if (test == "movie-studio"):
                studio = e.text
        link1 = soup.find_all('a',onclick="trackAffiliateEvent('amazon')")
        if(len(link1) != 0):
            for ls in link1:
                amazon = ls.get('href')
        else:
            amazon = ''
        link2 = soup.find_all('a',onclick="trackAffiliateEvent('itunes')")
        if(len(link2) != 0):
            for ls in link2:
                itunes = ls.get('href')
        else:
            itunes = ''
        link3 = soup.find_all('a',onclick="trackAffiliateEvent('vudu')")
        if(len(link3) != 0):
            for ls in link3:
                vudu = ls.get('href')
        else:
            vudu = ''

        return (consensus,all_meter,avg_rate_all,rev_count_all,fresh_all,rotten_all,top_meter,avg_rate_top,rev_count_top,fresh_top,rotten_top,audience_score,user_avg,user_rate,studio,amazon,itunes,vudu)
    except urllib.error.HTTPError:
        try:
            if ("Bahubali" in poster_title):
                poster_title = "Baahubali 2: The Conclusion (2017)"
            t = poster_title.replace(" ()","")
            t = t.replace(" -","")
            t = t.replace(" :","")
            t = t.replace(" ","_")
            t = t.replace(".","")
            t = t.replace(",","")
            t = t.replace("-","")
            t = t.replace("'","")
            t = t.replace(" ","")
            t = t.replace(":","")
            t = t.replace("-","")
            t = t.replace("!","")
            t = t.replace('(',"")
            t = t.replace(')',"")
            t = t.replace("&","and")
            print("njejn",t)
            consensus = "NOT AVAILABLE"
            all_meter = "NOT AVAILABLE"
            avg_rate_all= "NOT AVAILABLE"
            rev_count_all= "NOT AVAILABLE"
            fresh_all= "NOT AVAILABLE"
            rotten_all= "NOT AVAILABLE"
            top_meter= "NOT AVAILABLE"
            avg_rate_top= "NOT AVAILABLE"
            rev_count_top= "NOT AVAILABLE"
            fresh_top= "NOT AVAILABLE"
            rotten_top= "NOT AVAILABLE"
            audience_score= "NOT AVAILABLE"
            user_avg= "NOT AVAILABLE"
            user_rate= "NOT AVAILABLE"
            studio = "NA"
            movietitle = t.lower()

            print("https://www.rottentomatoes.com/m/"+movietitle)
            sauce = urllib.request.urlopen("https://www.rottentomatoes.com/m/"+movietitle,timeout=10000).read()
            soup = bs.BeautifulSoup(sauce, 'lxml')

            soup2 = soup.find_all('div',id="all-critics-numbers")
            for con in soup2:
                consensus = con.p.text
                consensus = consensus.replace("Critics Consensus:","")

            tomatometer_all = soup2[0].find_all('span',class_="meter-value superPageFontColor")
            for al in tomatometer_all:
                all_meter = al.text

            all_critics = soup2[0].find_all('div', class_="superPageFontColor")
            for a in all_critics:
                try:
                    i = a.span.text
                    if (i == "Average Rating: "):
                        avg_rate = a.text
                        avg_rate_all = avg_rate.replace("Average Rating:","")
                        avg_rate_all = avg_rate_all.replace("/10","")
                        avg_rate_all = avg_rate_all.replace(" ","")
                    elif(i == "Reviews Counted: "):
                        rev_count = a.text
                        rev_count_all = rev_count.replace("Reviews Counted:","")

                    elif(i == "Fresh: "):
                        fresh = a.text
                        fresh_all = fresh.replace("Fresh:","")

                    elif(i == "Rotten: "):
                        rotten = a.text
                        rotten_all = rotten.replace("Rotten:","")

                except AttributeError:
                    break

            soup3 = soup.find_all('div',id="top-critics-numbers")
            tomatometer_top = soup3[0].find_all('span',class_="meter-value superPageFontColor")
            for top in tomatometer_top:
                top_meter = top.text


            top_critics = soup3[0].find_all('div', class_="superPageFontColor")
            for b in top_critics:
                try:
                    i = b.span.text
                    if (i == "Average Rating: "):
                        avg_rate = b.text
                        avg_rate_top = avg_rate.replace("Average Rating:","")
                        avg_rate_top = avg_rate_all.replace("/10","")
                        avg_rate_top = avg_rate_all.replace(" ","")

                    elif(i == "Reviews Counted: "):
                        rev_count = b.text
                        rev_count_top = rev_count.replace("Reviews Counted:","")

                    elif(i == "Fresh: "):
                        fresh = b.text
                        fresh_top = fresh.replace("Fresh:","")

                    elif(i == "Rotten: "):
                        rotten = b.text
                        rotten_top = rotten.replace("Rotten:","")

                except AttributeError:
                    break

            audience = soup.find_all('div', class_="audience-score meter")
            for c in audience:
                audience_score = c.text
                audience_score = audience_score.replace("liked it","")
                audience_score = audience_score.replace("want to see","")
                audience_score = audience_score.replace(" ","")
                audience_score = audience_score.replace("wanttosee","")
            user_reviews = soup.find_all('div', class_="audience-info hidden-xs superPageFontColor")
            for d in user_reviews:
                ans = d.text
                ans= ans.replace("Average Rating:","")
                ans = ans.replace("User Ratings:","")
                user_avg=ans[0:20]
                user_avg = user_avg.replace(" ","")
                user_rate = ans[21 : ]
                user_avg = user_avg.replace(" ","")
                user_avg = user_avg.replace("/5","")
                user_avg = user_avg.replace(" ","")
                std = soup.find_all('a')
            for e in std:
                test= e.get('target')
                if (test == "movie-studio"):
                    studio = e.text
            link1 = soup.find_all('a',onclick="trackAffiliateEvent('amazon')")
            if(len(link1) != 0):
                for ls in link1:
                    amazon = ls.get('href')
            else:
                amazon = ''
            link2 = soup.find_all('a',onclick="trackAffiliateEvent('itunes')")
            if(len(link2) != 0):
                for ls in link2:
                    itunes = ls.get('href')
            else:
                itunes = ''
            link3 = soup.find_all('a',onclick="trackAffiliateEvent('vudu')")
            if(len(link3) != 0):
                for ls in link3:
                    vudu = ls.get('href')
            else:
                vudu = ''

            return (consensus,all_meter,avg_rate_all,rev_count_all,fresh_all,rotten_all,top_meter,avg_rate_top,rev_count_top,fresh_top,rotten_top,audience_score,user_avg,user_rate,studio,amazon,itunes,vudu)
        except urllib.error.HTTPError:
            try:
                if ("Bahubali" in poster_title):
                    poster_title = "Baahubali 2: The Conclusion (2017)"
                t = poster_title.replace(" ()","")
                t = t.replace("The ","")
                t = t.replace(" -","")
                t = t.replace(" :","")
                t = t.replace(" ","_")
                t = t.replace(".","")
                t = t.replace(",","")
                t = t.replace("-","")
                t = t.replace("'","")
                t = t.replace(" ","")
                t = t.replace("-","")
                t = t.replace(":","")
                t = t.replace("!","")
                t = t.replace('(',"")
                t = t.replace(')',"")
                t = t.replace("&","and")
                print("njejn",t)
                consensus = "NOT AVAILABLE"
                all_meter = "NOT AVAILABLE"
                avg_rate_all= "NOT AVAILABLE"
                rev_count_all= "NOT AVAILABLE"
                fresh_all= "NOT AVAILABLE"
                rotten_all= "NOT AVAILABLE"
                top_meter= "NOT AVAILABLE"
                avg_rate_top= "NOT AVAILABLE"
                rev_count_top= "NOT AVAILABLE"
                fresh_top= "NOT AVAILABLE"
                rotten_top= "NOT AVAILABLE"
                audience_score= "NOT AVAILABLE"
                user_avg= "NOT AVAILABLE"
                user_rate= "NOT AVAILABLE"
                studio = "NA"
                movietitle = t.lower()
                print("https://www.rottentomatoes.com/m/"+movietitle)
                sauce = urllib.request.urlopen("https://www.rottentomatoes.com/m/"+movietitle,timeout=10000).read()
                soup = bs.BeautifulSoup(sauce, 'lxml')

                soup2 = soup.find_all('div',id="all-critics-numbers")
                for con in soup2:
                    consensus = con.p.text
                    consensus = consensus.replace("Critics Consensus:","")

                tomatometer_all = soup2[0].find_all('span',class_="meter-value superPageFontColor")
                for al in tomatometer_all:
                    all_meter = al.text

                all_critics = soup2[0].find_all('div', class_="superPageFontColor")
                for a in all_critics:
                    try:
                        i = a.span.text
                        if (i == "Average Rating: "):
                            avg_rate = a.text
                            avg_rate_all = avg_rate.replace("Average Rating:","")
                            avg_rate_all = avg_rate_all.replace("/10","")
                            avg_rate_all = avg_rate_all.replace(" ","")
                        elif(i == "Reviews Counted: "):
                            rev_count = a.text
                            rev_count_all = rev_count.replace("Reviews Counted:","")

                        elif(i == "Fresh: "):
                            fresh = a.text
                            fresh_all = fresh.replace("Fresh:","")

                        elif(i == "Rotten: "):
                            rotten = a.text
                            rotten_all = rotten.replace("Rotten:","")

                    except AttributeError:
                        break

                soup3 = soup.find_all('div',id="top-critics-numbers")
                tomatometer_top = soup3[0].find_all('span',class_="meter-value superPageFontColor")
                for top in tomatometer_top:
                    top_meter = top.text


                top_critics = soup3[0].find_all('div', class_="superPageFontColor")
                for b in top_critics:
                    try:
                        i = b.span.text
                        if (i == "Average Rating: "):
                            avg_rate = b.text
                            avg_rate_top = avg_rate.replace("Average Rating:","")
                            avg_rate_top = avg_rate_all.replace("/10","")
                            avg_rate_top = avg_rate_all.replace(" ","")

                        elif(i == "Reviews Counted: "):
                            rev_count = b.text
                            rev_count_top = rev_count.replace("Reviews Counted:","")

                        elif(i == "Fresh: "):
                            fresh = b.text
                            fresh_top = fresh.replace("Fresh:","")

                        elif(i == "Rotten: "):
                            rotten = b.text
                            rotten_top = rotten.replace("Rotten:","")

                    except AttributeError:
                        break

                audience = soup.find_all('div', class_="audience-score meter")
                for c in audience:
                    audience_score = c.text
                    audience_score = audience_score.replace("liked it","")
                    audience_score = audience_score.replace("want to see","")
                    audience_score = audience_score.replace(" ","")
                    audience_score = audience_score.replace("wanttosee","")
                user_reviews = soup.find_all('div', class_="audience-info hidden-xs superPageFontColor")
                for d in user_reviews:
                    ans = d.text
                    ans= ans.replace("Average Rating:","")
                    ans = ans.replace("User Ratings:","")
                    user_avg=ans[0:20]
                    user_avg = user_avg.replace(" ","")
                    user_rate = ans[21 : ]
                    user_avg = user_avg.replace(" ","")
                    user_avg = user_avg.replace("/5","")
                    user_avg = user_avg.replace(" ","")
                    std = soup.find_all('a')
                for e in std:
                    test= e.get('target')
                    if (test == "movie-studio"):
                        studio = e.text
                link1 = soup.find_all('a',onclick="trackAffiliateEvent('amazon')")
                if(len(link1) != 0):
                    for ls in link1:
                        amazon = ls.get('href')
                else:
                    amazon = ''
                link2 = soup.find_all('a',onclick="trackAffiliateEvent('itunes')")
                if(len(link2) != 0):
                    for ls in link2:
                        itunes = ls.get('href')
                else:
                    itunes = ''
                link3 = soup.find_all('a',onclick="trackAffiliateEvent('vudu')")
                if(len(link3) != 0):
                    for ls in link3:
                        vudu = ls.get('href')
                else:
                    vudu = ''

                return (consensus,all_meter,avg_rate_all,rev_count_all,fresh_all,rotten_all,top_meter,avg_rate_top,rev_count_top,fresh_top,rotten_top,audience_score,user_avg,user_rate,studio,amazon,itunes,vudu)
            except urllib.error.HTTPError:
                consensus = "NOT AVAILABLE"
                all_meter = "NOT AVAILABLE"
                avg_rate_all= "NOT AVAILABLE"
                rev_count_all= "NOT AVAILABLE"
                fresh_all= "NOT AVAILABLE"
                rotten_all= "NOT AVAILABLE"
                top_meter= "NOT AVAILABLE"
                avg_rate_top= "NOT AVAILABLE"
                rev_count_top= "NOT AVAILABLE"
                fresh_top= "NOT AVAILABLE"
                rotten_top= "NOT AVAILABLE"
                audience_score= "NOT AVAILABLE"
                user_avg= "NOT AVAILABLE"
                user_rate= "NOT AVAILABLE"
                studio = "NA"
                amazon = "NA"
                itunes = "NA"
                vudu = "NA"
                return (consensus,all_meter,avg_rate_all,rev_count_all,fresh_all,rotten_all,top_meter,avg_rate_top,rev_count_top,fresh_top,rotten_top,audience_score,user_avg,user_rate,studio,amazon,itunes,vudu)

def getRogerEbert(poster_title,release_yr,release_date):
    try:
        if ("Bahubali" in poster_title):
            poster_title = "Baahubali 2: The Conclusion (2017)"
        elif('Iron Man Three' in poster_title):
            poster_title = 'iron man 3'
        published = "NOT AVAILABLE"
        author= "NOT AVAILABLE"
        roger_rev= "NOT AVAILABLE"
        rating= "NOT AVAILABLE"
        best_rate= "NOT AVAILABLE"
        rated= "NOT AVAILABLE"
        s1 = poster_title.replace(":","")
        s2 = s1.replace("(","")
        s3 = s2.replace(")","")
        s3 = s3.replace("?","")
        s3 = s3.replace(".","")
        s3 = s3.replace("&","and")
        s3 = s3.replace("!","")
        s3 = s3.replace(",","")
        s4 = s3.replace("'","")
        s5 = s4.replace(" ","-")
        s6 = s5.replace("--","-")
        name =s6.lower()
        name= name+"-"
        print(name)
        urls = ("http://www.rogerebert.com/reviews/"+name+str(release_yr)).encode('ascii','ignore').decode('ascii')
        print(urls)
        sauce = requests.get(urls,proxies=proxies).text
        soup = bs.BeautifulSoup(sauce, 'lxml')

        t0 = soup.find_all('time')
        for tim in t0:
            published = tim.text

        t = soup.find_all("meta")
        for auth in t:
            if (auth.get('name') == "author"):
                author = auth.get('content')


        t1 = soup.find_all("div",itemprop="reviewBody")
        for roger in t1:
            roger_rev = roger.p.text
            roger_rev = roger_rev.encode('utf-8')
            roger_rev = roger_rev.decode("utf-8-sig")

        t2 = soup.find_all("meta")
        for rate in t2:
            if (rate.get('itemprop') == "ratingValue"):
                rating = rate.get('content')
                print(rating)
            elif (rate.get('itemprop') == "worstRating"):
                worst_rate = rate.get('content')
                print(worst_rate)
            elif (rate.get('itemprop') == "bestRating"):
                best_rate = rate.get('content')
                print(best_rate)

        t3 = soup.find_all('p',class_="mpaa-rating")
        for r in t3:
            rated = r.text

        return (published,author,roger_rev,rating,best_rate,rated)
    except urllib.error.HTTPError:
        try:
            release_date = release_date.split(" ")
            release_yr_new = release_date[2]
            if ("Bahubali" in poster_title):
                poster_title = "Baahubali 2: The Conclusion (2017)"
            elif('Iron Man Three' in poster_title):
                poster_title = 'iron man 3'
            published = "NOT AVAILABLE"
            author= "NOT AVAILABLE"
            roger_rev= "NOT AVAILABLE"
            rating= "NOT AVAILABLE"
            best_rate= "NOT AVAILABLE"
            rated= "NOT AVAILABLE"
            s1 = poster_title.replace(":","")
            s2 = s1.replace("(","")
            s3 = s2.replace(")","")
            s3 = s3.replace(".","")
            s3 = s3.replace("&","and")
            s3 = s3.replace("!","")
            s3 = s3.replace("?","")
            s3 = s3.replace(",","")
            s4 = s3.replace("'","")
            s5 = s4.replace(" ","-")
            s6 = s5.replace("--","-")
            name =s6.lower()
            name= name+"-"
            print(name)
            urls = ("http://www.rogerebert.com/reviews/"+name+str(release_yr_new)).encode('ascii','ignore').decode('ascii')
            sauce = requests.get(urls,proxies=proxies).text
            soup = bs.BeautifulSoup(sauce, 'lxml')

            t0 = soup.find_all('time')
            for tim in t0:
                published = tim.text


            t = soup.find_all("meta")
            for auth in t:
                if (auth.get('name') == "author"):
                    author = auth.get('content')


            t1 = soup.find_all("div",itemprop="reviewBody")
            for roger in t1:
                roger_rev = roger.p.text
                roger_rev = roger_rev.encode('utf-8')


            t2 = soup.find_all("meta")
            for rate in t2:
                if (rate.get('itemprop') == "ratingValue"):
                    rating = rate.get('content')
                    print(rating)
                elif (rate.get('itemprop') == "worstRating"):
                    worst_rate = rate.get('content')
                    print(worst_rate)
                elif (rate.get('itemprop') == "bestRating"):
                    best_rate = rate.get('content')
                    print(best_rate)

            t3 = soup.find_all('p',class_="mpaa-rating")
            for r in t3:
                rated = r.text

            return (published,author,roger_rev,rating,best_rate,rated)
        except urllib.error.HTTPError:
            published = "NOT FOUND"
            author= "NOT FOUND"
            roger_rev= "NOT FOUND"
            rating= "NOT FOUND"
            best_rate= "NOT FOUND"
            rated    = "NOT FOUND"
            return (published,author,roger_rev,rating,best_rate,rated)
def getmrqe(poster_title,title,release_yr):
    try:
        if("Iron Man Three" in poster_title):
            poster_title = "Iron Man 3"
        print("ssss", poster_title)
        print(" (" + str(release_yr) + ")")
        link = ""
        mrqe_rate = "NA"
        cast = "NA"
        synopsis = "NA"
        user_rating_src = ""
        critic_rating_src = ""
        score = ""
        #http://www.mrqe.com/search?utf8=✓&q=
        tt = poster_title.replace(":","")
        tt = tt.replace("(","")
        tt = tt.replace(")","")
        tt = tt.replace("-","")
        tt = tt.replace(".","")
        tt = tt.replace("&","and")
        tt = tt.replace(" ","+")
        tt = tt.lower()
        tt = tt+"+"
        print(tt)

        url = ("http://www.mrqe.com/search?q="+tt+"&commit=").encode('ascii','ignore').decode('ascii')
        print (url)
        sauce = requests.get(url,proxies=proxies).text
        soup = bs.BeautifulSoup(sauce, 'lxml')

        find = soup.find_all('a')
        mrqe_title = poster_title + " (" + str(release_yr) + ")"
        if ("Hugo" in mrqe_title):
            mrqe_title = "Hugo (2011/II)"
        elif ("Arrival" in mrqe_title):
            mrqe_title = "Arrival (2016/II)"
        elif ("Bahubali" in mrqe_title):
            mrqe_title = "Baahubali 2: The Conclusion (2017)"
        print(mrqe_title)
        for b in find:
            if (b.text == mrqe_title):
                link = b.get('href')
                print(link)

        mainurl = ("http://www.mrqe.com"+link)
        print (mainurl)
        sauce2 = requests.get(mainurl,proxies=proxies).text
        soup2 = bs.BeautifulSoup(sauce2, 'lxml')

        meta = soup2.find_all('p')
        ##print(meta)

        for i in meta:
            a = i.text
            if "Rating:" in a:
                mrqe_rate = i.text
                mrqe_rate = mrqe_rate.replace('Rating: ','')
                print(mrqe_rate)

        meta_c = soup2.find_all('div',class_='metadata')
        for k in meta_c:
            cast = k.p.text
            cast = cast.replace("Cast:","")
            print (cast.encode('utf-8'))

        syn = soup2.find_all('p',class_='synopsis')
        for j in syn:
            synopsis = j.text
            synopsis = synopsis.replace("Synopsis:","")

        usr = soup2.find_all('img',alt = "User Rating")
        for user in usr:
            user_rating_src = user.get('src')
            print(user_rating_src)

        crt = soup2.find_all('img',alt = "Critic Rating")
        for critic in crt:
            critic_rating_src = critic.get('src')
        try:
            s_url = critic_rating_src.replace("?","/")
            result = re.match(r'^((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$', s_url)
            string = result.groups()[5]
            score = re.findall(r'[^\\/]+|[\\/]', string)[2]
            score = score.replace("score=","")
        except AttributeError:
            score ="NA"
        except IndexError:
            score ="NA"
        return (mrqe_rate,cast,synopsis,user_rating_src,critic_rating_src,score)
    except urllib.error.HTTPError:
        mrqe_rate = "NOT AVAILABLE"
        cast = "NOT AVAILABLE"
        synopsis= "NOT AVAILABLE"
        user_rating_src = ""
        critic_rating_src = ""
        score = ""
        return (mrqe_rate,cast,synopsis,user_rating_src,critic_rating_src,score)
    except AttributeError:
        mrqe_rate = "NOT AVAILABLE"
        cast = "NOT AVAILABLE"
        synopsis= "NOT AVAILABLE"
        user_rating_src = ""
        critic_rating_src = ""
        score = ""
        return (mrqe_rate,cast,synopsis,user_rating_src,critic_rating_src,score)
def getMetacritic(poster_title,release_yr):
    try:
        if ("Bahubali" in poster_title):
            poster_title = "Baahubali 2: The Conclusion (2017)"
        if ("Bahubali" in poster_title):
            poster_title = ""
        if ("Iron Man Three" in poster_title):
            poster_title = "iron man 3"
        meta_critic_score = "NOT AVAILABLE"
        user_meta_score = "NOT AVAILABLE"
        pos_meta= "NOT AVAILABLE"
        mix_meta= "NOT AVAILABLE"
        neg_meta= "NOT AVAILABLE"
        pos_user= "NOT AVAILABLE"
        mix_user= "NOT AVAILABLE"
        neg_user = "NOT AVAILABLE"
        tot_meta = "NA"
        tot_user = "NA"
        tt = poster_title.replace(":","")
        tt = tt.replace("(","")
        tt = tt.replace(")","")
        tt = tt.replace(",","")
        tt = tt.replace("&","")
        tt = tt.replace("  "," ")
        tt = tt.replace(".","")
        tt = tt.replace("'","")
        tt = tt.replace(" - ","-")
        tt = tt.replace(" ","-")
        tt = tt.lower()
        print(tt)

        site = "http://www.metacritic.com/movie/"+tt+"-"+release_yr

        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(site,headers=hdr,proxies=proxies).text
        soup = bs.BeautifulSoup(req, 'lxml')
        print (site)
        m1 = soup.find_all('span',class_="metascore_w header_size movie positive")
        for i1 in m1:
            meta_critic_score = i1.text

        m4 = soup.find_all('span',class_="metascore_w header_size movie positive perfect")
        for i1 in m4:
            meta_critic_score = i1.text

        m2 = soup.find_all('span',class_="metascore_w header_size movie mixed")
        for i2 in m2:
            meta_critic_score = i2.text

        m3 = soup.find_all('span',class_="metascore_w header_size movie negative")
        for i3 in m3:
            meta_critic_score = i3.text

        n = soup.find_all('td',class_="score")
        soup2 = n[0].find_all('span')
        for j in soup2:
            user_meta_score = j.text
            print(user_meta_score)

        z = soup.find_all('div',class_="chart positive")
        for ps in z:
            pos_user = ps.text
            pos_user = pos_user.replace("Positive:","")
        y = soup.find_all('div',class_="chart mixed")
        for mx in y:
            mix_user = mx.text
            mix_user = mix_user.replace("Mixed:","")
            print (mix_user)
        w = soup.find_all('div',class_="chart negative")
        for ng in w:
            neg_user = ng.text
            neg_user = neg_user.replace("Negative:","")
            print (neg_user)
        a = z[0].find_all('div')
        b = y[0].find_all('div')
        c = w[0].find_all('div')

        x = soup.find_all('div',class_="text oswald")
        x1 = x[0].find_all('div')
        x2 = x1[1]
        pos_meta = list(x2)[0]


        y = soup.find_all('div',class_="text oswald")
        y1 = y[1].find_all('div')
        y2 = y1[1]
        mix_meta = list(y2)[0]

        z = soup.find_all('div',class_="text oswald")
        z1 = z[2].find_all('div')
        z2 = z1[1]
        neg_meta = list(z2)[0]
        tot_meta = (int(pos_meta.replace(",","")) + int(mix_meta.replace(",","")) + int(neg_meta.replace(",","")))
        tot_user = (int(pos_user.replace(",","")) + int(mix_user.replace(",","")) + int(neg_user.replace(",","")))
        return (meta_critic_score,user_meta_score, pos_meta, mix_meta, neg_meta, pos_user, mix_user, neg_user,tot_meta,tot_user)

    except IndexError:
        try:
            if ("Bahubali" in poster_title):
                poster_title = "Baahubali 2: The Conclusion (2017)"
            if ("Bahubali" in poster_title):
                poster_title = ""
            if ("Iron Man Three" in poster_title):
                poster_title = "iron man 3"
            meta_critic_score = "NOT AVAILABLE"
            user_meta_score = "NOT AVAILABLE"
            pos_meta= "NOT AVAILABLE"
            mix_meta= "NOT AVAILABLE"
            neg_meta= "NOT AVAILABLE"
            pos_user= "NOT AVAILABLE"
            mix_user= "NOT AVAILABLE"
            neg_user = "NOT AVAILABLE"
            tot_meta = "NA"
            tot_user = "NA"
            tt = poster_title.replace(":","")
            tt = tt.replace("(","")
            tt = tt.replace(")","")
            tt = tt.replace(",","")
            tt = tt.replace("&","")
            tt = tt.replace("  "," ")
            tt = tt.replace(".","")
            tt = tt.replace("'","")
            tt = tt.replace(" - ","-")
            tt = tt.replace(" ","-")
            tt = tt.lower()
            print(tt)

            site = "http://www.metacritic.com/movie/"+tt
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = requests.get(site,headers=hdr,proxies=proxies).text
            soup = bs.BeautifulSoup(req, 'lxml')
            print (site)
            m1 = soup.find_all('span',class_="metascore_w header_size movie positive")
            for i1 in m1:
                meta_critic_score = i1.text

            m4 = soup.find_all('span',class_="metascore_w header_size movie positive perfect")
            for i1 in m4:
                meta_critic_score = i1.text

            m2 = soup.find_all('span',class_="metascore_w header_size movie mixed")
            for i2 in m2:
                meta_critic_score = i2.text

            m3 = soup.find_all('span',class_="metascore_w header_size movie negative")
            for i3 in m3:
                meta_critic_score = i3.text

            n = soup.find_all('td',class_="score")
            soup2 = n[0].find_all('span')
            for j in soup2:
                user_meta_score = j.text
                print(user_meta_score)

            z = soup.find_all('div',class_="chart positive")
            for ps in z:
                pos_user = ps.text
                pos_user = pos_user.replace("Positive:","")
            y = soup.find_all('div',class_="chart mixed")
            for mx in y:
                mix_user = mx.text
                mix_user = mix_user.replace("Mixed:","")
                print (mix_user)
            w = soup.find_all('div',class_="chart negative")
            for ng in w:
                neg_user = ng.text
                neg_user = neg_user.replace("Negative:","")
                print (neg_user)
            a = z[0].find_all('div')
            b = y[0].find_all('div')
            c = w[0].find_all('div')

            x = soup.find_all('div',class_="text oswald")
            x1 = x[0].find_all('div')
            x2 = x1[1]
            pos_meta = list(x2)[0]


            y = soup.find_all('div',class_="text oswald")
            y1 = y[1].find_all('div')
            y2 = y1[1]
            mix_meta = list(y2)[0]

            z = soup.find_all('div',class_="text oswald")
            z1 = z[2].find_all('div')
            z2 = z1[1]
            neg_meta = list(z2)[0]
            tot_meta = (int(pos_meta.replace(",","")) + int(mix_meta.replace(",","")) + int(neg_meta.replace(",","")))
            tot_user = (int(pos_user.replace(",","")) + int(mix_user.replace(",","")) + int(neg_user.replace(",","")))
            print(meta_critic_score)
            return (meta_critic_score,user_meta_score, pos_meta, mix_meta, neg_meta, pos_user, mix_user, neg_user,tot_meta,tot_user)
        except urllib.error.HTTPError:
            meta_critic_score = "NOT AVAILABLE"
            user_meta_score = "NOT AVAILABLE"
            pos_meta= "NOT AVAILABLE"
            mix_meta= "NOT AVAILABLE"
            neg_meta= "NOT AVAILABLE"
            pos_user = "NOT AVAILABLE"
            mix_user = "NOT AVAILABLE"
            neg_user = "NOT AVAILABLE"
            tot_user = "NA"
            tot_meta = "NA"
            return (meta_critic_score,user_meta_score, pos_meta, mix_meta, neg_meta, pos_user, mix_user, neg_user,tot_meta,tot_user)
    except:
        #print(meta_critic_score)
        meta_critic_score = "NOT AVAILABLE"
        user_meta_score = "NOT AVAILABLE"
        pos_meta= "NOT AVAILABLE"
        mix_meta= "NOT AVAILABLE"
        neg_meta= "NOT AVAILABLE"
        pos_user = "NOT AVAILABLE"
        mix_user = "NOT AVAILABLE"
        neg_user = "NOT AVAILABLE"
        tot_user = "NA"
        tot_meta = "NA"
        return (meta_critic_score,user_meta_score, pos_meta, mix_meta, neg_meta, pos_user, mix_user, neg_user,tot_meta,tot_user)

import socket

def getFandango(poster_title, release_yr):
    try:
        if("Iron Man Three" in poster_title):
            poster_title = "Iron Man 3"
        elif("The Avengers" in poster_title):
            poster_title = "Marvel's the Avengers"
        global urls
        fandango_score = "NA"
        fandango_fans = "NA"
        ttt = poster_title.replace(" ()","")
        titl = ttt.replace(":","")
        end = titl.replace(" ","-")
        titl = titl.replace(" ","+")
        titl2 = titl.replace("&","and")
        titl2 = titl2.lower()
        print("fand "+titl2)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        req = requests.get("https://www.fandango.com/search/?q="+titl2, headers=headers,proxies=proxies,timeout=20).text

        soup = bs.BeautifulSoup(req, 'lxml')

        #print(soup)
        rate = soup.find_all('div',class_='movie-info-stats')

        mtitle = poster_title+" ("+release_yr+")"
        print(mtitle)
        for i in rate:
            if(i.h3.text.lower() == poster_title.lower()):
                urls = i.a.get('href')
            elif(i.h3.text.lower() == mtitle.lower()):
                urls = i.a.get('href')
            else:
                if(release_yr == "2017"):
                    release_yr = "2018"
                elif(release_yr == "2018"):
                    release_yr = "2017"
                mtitle2 = poster_title+" ("+release_yr+")"
                if(i.h3.text.lower() == poster_title.lower()):
                    urls = i.a.get('href')
                elif(i.h3.text.lower() == mtitle2.lower()):
                    urls = i.a.get('href')

        response = requests.get(urls, headers=headers,proxies=proxies)
        data = response.text
        soup2 = bs.BeautifulSoup(data, 'lxml')

        fd = soup2.find_all('li',class_='fd-star-rating__container')
        for f in fd:
            fandango_score = f.div.get('data-star-rating')

        fan = soup2.find_all('li',class_='movie-details__fan-ratings')
        for k in fan:
            fandango_fans =  k.text
        return (fandango_score,fandango_fans)
    except urllib.error.HTTPError:
        if("Iron Man Three" in poster_title):
            poster_title = "Iron Man 3"
        elif("The Avengers" in poster_title):
            poster_title = "Marvel's the Avengers"
        global urls
        fandango_score = "NA"
        fandango_fans = "NA"
        ttt = poster_title.replace(" ()","")
        titl = ttt.replace(":","")
        end = titl.replace(" ","-")
        titl = titl.replace(" ","+")
        titl2 = titl2.lower()
        print("fand "+titl2)
        req = Request("https://www.fandango.com/search/?q="+titl2, headers={'User-Agent': 'Mozilla/5.0'})
        sauce = urlopen(req,timeout=10000).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')

        #print(soup)
        rate = soup.find_all('div',class_='movie-info-stats')

        mtitle = poster_title+" ("+release_yr+")"
        print(mtitle)
        for i in rate:
            if(i.h3.text.lower() == poster_title.lower()):
                urls = i.a.get('href')
            elif(i.h3.text.lower() == mtitle.lower()):
                urls = i.a.get('href')
            else:
                if(release_yr == "2017"):
                    release_yr = "2018"
                elif(release_yr == "2018"):
                    release_yr = "2017"
                mtitle2 = poster_title+" ("+release_yr+")"
                if(i.h3.text.lower() == poster_title.lower()):
                    urls = i.a.get('href')
                elif(i.h3.text.lower() == mtitle2.lower()):
                    urls = i.a.get('href')

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(urls, headers=headers)
        data = response.text
        soup2 = bs.BeautifulSoup(data, 'lxml')

        fd = soup2.find_all('li',class_='fd-star-rating__container')
        for f in fd:
            fandango_score = f.div.get('data-star-rating')

        fan = soup2.find_all('li',class_='movie-details__fan-ratings')
        for k in fan:
            fandango_fans =  k.text
        return (fandango_score,fandango_fans)

    except NameError:
        fandango_score = "NOT FOUND"
        fandango_fans = "NOT FOUND"
        return (fandango_score,fandango_fans)

def velocity(imdb_rate,all_critics_tomatometer,audience_score,roger_rating,metascore,user_meta_score,fandango_score,mrqe_metric):
    imdb = float(imdb_rate)*10
    all_critics = float(all_critics_tomatometer.replace("%",""))
    aud = float(audience_score.replace("%",""))
    roger_ebert = float(roger_rating)*25
    meta = float(metascore)
    user_metta = float(user_meta_score)*10
    fandango = float(fandango_score)*20
    mrqe = float(mrqe_metric)
    sum = imdb + all_critics + aud + roger_ebert + meta + user_metta + fandango + mrqe
    vel = round(sum / 8, 1)
    return vel

def getincinemas():
    sauce = requests.get("http://www.mrqe.com/lists/incinemas",proxies=proxies).text
    soup = bs.BeautifulSoup(sauce, 'lxml')
    l = soup.find_all('a',class_= "tooltip_container")
    data = []
    for i in l:
        try:
            in_cinemas = i.text
            data.append(in_cinemas)
        except AttributeError:
            break

    m = soup.find_all('th',colspan = "2")
    for j in m:
        main = j.text
    return(data,main)

def getupcoming():
    sauce2 = requests.get("http://www.mrqe.com/lists/upcoming",proxies=proxies).text
    soup2 = bs.BeautifulSoup(sauce2, 'lxml')
    l = soup2.find_all('a',class_= "tooltip_container")
    data2 =[]
    for i in l:
        try:
            in_cinemas = i.text
            data2.append(in_cinemas)
        except AttributeError:
            break
    m = soup2.find_all('th',colspan = "2")
    for j in m:
        main2 = j.text
    return(data2,main2)

def getdvd():
    sauce2 = requests.get("http://www.mrqe.com/lists/recentdvd",proxies=proxies).text
    soup2 = bs.BeautifulSoup(sauce2, 'lxml')
    l = soup2.find_all('a',class_= "tooltip_container")
    data3 =[]
    for i in l:
        try:
            in_cinemas = i.text
            data3.append(in_cinemas)
        except AttributeError:
            break
    return(data3)

def getmostpopular():
    url = "http://www.mrqe.com/lists/most_popular"
    req = requests.get(url,proxies=proxies).text
    soup = bs.BeautifulSoup(req, 'lxml')
    l = soup.find_all('a',class_= "tooltip_container")
    popular_m = []
    for i in l:
        try:
            in_cinemas = i.text
            popular_m.append(in_cinemas)
        except AttributeError:
            break
    return popular_m

def velocity_calculation(imdb_eq,rt_eq,eq_fand,eq_meta,roger_rating,mrqe_metric):
    w_1 = 0.207
    w_2 = 0.163
    w_3 = 0.203
    w_4 = 0.172
    w_5 = 0.113
    w_6 = 0.129
    sum = w1*imdb_eq + w2*rt_eq + w3*eq_fand + w4*eq_meta + w5*mrqe_metric + w6*roger_rating
    vel = round(sum / 6, 1)
    return vel

def getequivalent(rating,votes,Q):
    e = 2.71828
    P = 0.5
    equiv = P*rating + 10*(1-P)*(1 - (e**(-votes/Q)))
    return equiv

def getarticles(poster_title,release_yr):

    print("ssss", poster_title)
    print(" (" + str(release_yr) + ")")
    link = ""
    mrqe_rate = "NA"
    cast = "NA"
    synopsis = "NA"
    user_rating_src = ""
    critic_rating_src = ""
    score = ""
    #http://www.mrqe.com/search?utf8=✓&q=
    tt = poster_title.replace(":","")
    tt = tt.replace("(","")
    tt = tt.replace(")","")
    tt = tt.replace("-","")
    tt = tt.replace(".","")
    tt = tt.replace(" ","+")
    tt = tt.lower()
    tt = tt+"+"
    print(tt)

    url = ("http://www.mrqe.com/search?q="+tt+str(release_yr)+"&commit=").encode('ascii','ignore').decode('ascii')
    print (url)
    sauce = requests.get(url,proxies=proxies).text
    soup = bs.BeautifulSoup(sauce, 'lxml')

    find = soup.find_all('a')
    mrqe_title = poster_title + " (" + str(release_yr) + ")"
    if ("Hugo" in mrqe_title):
        mrqe_title = "Hugo (2011/II)"
    print(mrqe_title)
    for b in find:
        if (b.text == mrqe_title):
            link = b.get('href')
            print(link)

    mainurl = ("http://www.mrqe.com"+link)
    print (mainurl)
    sauce2 = requests.get(mainurl,proxies=proxies).text
    soup2 = bs.BeautifulSoup(sauce2, 'lxml')
    all_links = []
    ref = soup2.find_all('a',class_="tooltip_container")
    for li in ref:
        all_links.append("http://www.mrqe.com"+li.get('href'))
    count_all = len(all_links)
    print(len(all_links))
    print(all_links)

    all_articles= []
    art = soup2.find_all('li', class_="article")
    for ar in art:
        all_articles.append(ar.text)
    print(len(all_articles))

    all_zipped = list(zip(all_articles,all_links))
    return (all_zipped,count_all)

if __name__ == '__main__':
    app.run(debug=True)
