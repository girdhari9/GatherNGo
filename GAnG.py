#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3, os, datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, current_app, flash
from contextlib import closing
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
import googlemaps, pandas as pd
import geopy.distance

# Creating the application.
app = Flask(__name__)
app.config.from_object("config")

@app.context_processor
def variables_def():
  return dict(
        websiteName=unicode(app.config["WEBSITENAME"], "utf-8"),
        websiteDesc=unicode(app.config["WEBSITEDESC"], "utf-8"),
        address=unicode(app.config["ADDRESS"], "utf-8"),
        contact=unicode(app.config["CONTACTDETAIL"], "utf-8"),
        email=unicode(app.config["EMAILID"], "utf-8"),
        timing=unicode(app.config["TIMING"], "utf-8"),
        websiteUrl=request.url_root[:-1],
        currentUrl=request.path,
        )

def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource(os.path.join(os.getcwd(), "CabSharing-Schema.sql"), mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

def get_pages():
  fetch_pages = g.db.execute('select * from pages order by pageid')
  pages = [dict(pageid=y[0], pageurl=y[1], pagetitle=y[2]) for y in fetch_pages.fetchall()]
  return pages

def get_posts():
  posts = ""
  fetch_posts = g.db.execute('select users.fullname, posts.* from posts left join users on users.userid = posts.postauthor order by postid desc')
  posts = [dict(authorname=x[0], postid=x[1], posttitle=x[2], posturl=x[3], postcontent=x[4], postauthor=x[5], posttheme=x[6], postdate=x[7]) for x in fetch_posts.fetchall()]
  return posts

def getPosts(userid):
  posts = ""
  fetch_posts = g.db.execute('select * from posts where postauthor = ? order by postid desc',(userid,))
  posts = [dict(postid=x[0], posttitle=x[1], posturl=x[2], postcontent=x[3], postauthor=x[4], postdate=x[6]) for x in fetch_posts.fetchall()]
  return posts

def single_post(posturl):
  showingpost = g.db.execute('select * from posts where posturl = ?', (posturl,))
  for x in showingpost.fetchall():
    postid, posttitle, posturl, postcontent, postauthor, posttheme, postdate = x[0], x[1], x[2], x[3], x[4], x[5], x[6]
  post = [postid, posttitle, posturl, postcontent, postauthor, posttheme, postdate]
  return post

def editpost(posturl):
  if session.get('logged_in'):
    getPost = g.db.execute('select * from posts where posturl = ?', (posturl,))
    for n in getPost.fetchall():
      posttitle, posturl, postcontent, posttheme = n[1], n[2], n[3], n[5]
    post = [posttitle, posturl, postcontent, posttheme]
    return post
  else:
    abort(404)

def single_page(pageurl):
  showingpage = g.db.execute('select * from pages where pageurl= ?', (pageurl,))
  for x in showingpage.fetchall():
    pageid, pageurl, pagetitle, pagecontent, pageauthor, pagedate = x[0], x[1], x[2], x[3], x[4], x[5]
  page = [pageid, pageurl, pagetitle, pagecontent, pageauthor, pagedate]
  return page

def getUserDetail(userid):
  getDetail = g.db.execute('select * from logindetails where userid= ?', (userid,))
  userDetail = getDetail.fetchone()
  return userDetail

def getPostsWithAuthor(userid):
  getDetail = g.db.execute('select * from posts where postauthor= ? order by postdate',(userid,))
  adminPost = [dict(posturl=detail[2], posttitle=detail[1], postdate=detail[6]) for detail in getDetail.fetchall()]
  print(adminPost)
  return adminPost

def getAuthors(userid):
  getDetail = g.db.execute('select * from users where not userid = ?',(userid,))
  adminProfile = [dict(userid=detail[0], username=detail[1], password=detail[2], fullname=detail[3], emailid=detail[4], mobile_no=detail[5]) for detail in getDetail.fetchall()]
  print adminProfile 
  return adminProfile

def getPostAuthor(posturl):
  getDetail = g.db.execute('select fullname from users where userid = (select postauthor from posts where posturl= ?)',(posturl,))
  for x in getDetail.fetchall():
    fullname = x[0]
  user = [fullname]
  return user

def getCommnet(posturl):
  getDetail = g.db.execute('select users.userid, users.fullname, comments.comment, comments.cmttime \
                            FROM posts \
                            INNER JOIN \
                            (comments INNER JOIN users ON comments.userid = users.userid) ON posts.postid = comments.postid \
                            WHERE (((posts.posturl)= ?))',(posturl,))
  comment = [dict(userid=detail[0],fullname=detail[1], comment=detail[2], cmttime=detail[3]) for detail in getDetail.fetchall()]
  return comment

def editpage(pageurl):
  if session.get('logged_in'):
    getPage = g.db.execute('select * from pages where pageurl = ?', (pageurl,))
    for n in getPage.fetchall():
      pagetitle, pageurl, pagecontent, = n[1], n[2], n[3]
    page = [pageurl, pagetitle, pagecontent]
    return page
  else:
    abort(404)

def getPostid(posturl):
  getDetail = g.db.execute('select postid from posts where posturl= ?',(posturl,))
  for postid in getDetail.fetchall():
    return postid[0]

def checkUsername(username):
  getUser = g.db.execute('select userid from logindetails where userid= ?',(username,))
  if not getUser.fetchone():
    return True
  return False

def checkUrl(posturl):
  getUrl = g.db.execute('select posturl from posts where posturl= ?',(posturl,))
  if not getUrl.fetchone():
    return True
  return False  

def checkAuthorUrl(posturl):
  getId = g.db.execute('select postauthor from posts where posturl= ?',(posturl,))
  userid = getId.fetchone()
  if session.get('logged_in'):
    if userid[0] == str(session['userid']):
      return True
    return False 
  else:
    abort(404) 

def createCluster(distancelist):
  userList = []
  for key, val in distancelist.items(): 
    print(str(key), val)
    if val <= 1:
      userList.append(key[0])
  return userList
      
def getUsersDetail(userList):
  print(userList)
  print(userList[0])
  userDetails = g.db.execute('SELECT * FROM logindetails', g.db)
  return [dict(userid=detail[0], fullname=detail[1], gender=detail[3]) for detail in userDetails.fetchall()]

def doCluster(sourceLat, sourceLong, destLat, destLong, City, rideTime, pincode):
  # Need to optimize Query
  query = "SELECT * FROM ridedetails WHERE (sourcecity LIKE '%" + City + "%' and sourcepincode = '"+ pincode +"') and ridetime = '" + rideTime + "'"
  df = pd.read_sql(query, g.db)
  distancelist = {}
  for index in range(len(df)):
    if session['userid'] == df.iloc[[index]]['userid'].iloc[0]:
      continue

    LatOrigin = float(df.iloc[[index]]['sourcelat'])
    LongOrigin = float(df.iloc[[index]]['sourcelong'])
    origins = (LatOrigin,LongOrigin)

    userorigin = (sourceLat, sourceLong)
    distancelist[df.iloc[[index]]['userid'].iloc[0]] = geopy.distance.vincenty(origins, userorigin).km
  print(distancelist) 
  userList = createCluster(distancelist)
  return getUsersDetail(userList)


@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.route('/contact')
def show_contact():
  return render_template('contact.html')

@app.route('/')
def show_index():
  return render_template('index.html')

@app.route('/post/<posturl>')
def show_post(posturl):
  return render_template('post.html', post=single_post(posturl), user=getPostAuthor(posturl), comment=getCommnet(posturl),  pages=get_pages())

@app.route('/post/<posturl>/edit')
def postedit(posturl):
  if not checkAuthorUrl(posturl):
    abort(404)
  else:
    if session.get('logged_in'):
      return render_template('edit.html', post = editpost(posturl), contentType = "post", pages=get_pages())
    else:
      abort(404)

@app.route('/post/<posturl>/delete')
def postdelete(posturl):
  if session.get('logged_in'):
    g.db.execute('delete from comments where postid = (select postid from posts where posturl = ?)', (posturl,))
    g.db.execute('delete from posts where posturl = ?', (posturl,))
    g.db.commit()
    return render_template('index.html', posts=get_posts(), pages=get_pages())
  else:
    abort(404)

@app.route('/page/<pageurl>')
def show_page(pageurl):
  return render_template('page.html', page=single_page(pageurl), pages=get_pages())

@app.route('/page/<pageurl>/edit')
def pageedit(pageurl):
  if session.get('logged_in'):
    return render_template('edit.html', post = editpage(pageurl), contentType = "page", pages=get_pages())
  else:
    abort(404)

@app.route('/page/<pageurl>/delete')
def pagedelete(pageurl):
  if session.get('logged_in'):
      g.db.execute('delete from pages where pageurl = ?', (pageurl,))
      g.db.commit()
      return render_template('index.html', posts=get_posts(), pages=get_pages())
  else:
    abort(404)

@app.route('/archive')
def archive():
  if session.get('logged_in'):
    userid = session['userid']
  else:
    return render_template('archive.html', posts=get_posts(), pages=get_pages())

  return render_template('archive.html', posts=getPosts(userid), profile=getUserDetail(userid), pages=get_pages())

@app.route('/publish', methods=['GET', 'POST'])
def publish():
  if session.get('logged_in'):
    if request.method == 'POST':
      if not checkUrl(request.form['url']):
        flash('Give different Content Link!')
        return redirect(request.url)
      if request.form['contenttype'] == "post":
        g.db.execute('insert into posts (posttitle, posturl, postcontent, postauthor, posttheme) values (?, ?, ?, ?, ?)',
                     (request.form['title'], request.form['url'], request.form['content'], session['userid'], request.form['themeval']))
        g.db.commit()
        return redirect(request.url_root)
      else:
        g.db.execute('insert into pages (pagetitle, pageurl, pagecontent, pageauthor) values (?, ?, ?, ?)',
                     (request.form['title'], request.form['url'], request.form['content'], session['userid']))
        g.db.commit()
        return redirect(request.url_root)
    elif request.method == 'GET':
      return render_template('new.html', pages=get_pages())
  else:
    return abort(404)

def make_external(url):
  return urljoin(request.url_root, url)


@app.route('/posts.atom')
def recent_feed():
  feed = AtomFeed('Recent Articles',
                  feed_url=request.url, url=request.url_root)
  articles = get_posts()[:5]
  for y in range(len(articles)):
      feed.add(articles[y]['posttitle'], articles[y]['postcontent'],
               content_type='html',
               url=make_external(articles[y]['posturl']),
               updated=datetime.datetime.strptime(articles[y]['postdate'], '%Y-%m-%d %H:%M:%S'))
  return feed.get_response()

@app.route('/publishedit', methods=['POST'])
def doEdit():
  if session.get('logged_in'):
    if request.method == 'POST':
      if request.form["contenttype"] == "post":
        g.db.execute('UPDATE posts SET posttitle = ?, postcontent = ?, posttheme = ? WHERE posturl = ?', (request.form['title'], request.form['content'], request.form['themeval'], request.form['url']))
        g.db.commit()
        return redirect(request.url_root)
      else:
        g.db.execute('UPDATE pages SET pagetitle = ?, pagecontent = ? WHERE pageurl = ?', (request.form['title'], request.form['content'], request.form['url']))
        g.db.commit()
        return redirect(request.url_root)
    else:
        abort(404)
  else:
    abort(404)

@app.route('/People-Near-You', methods=['GET', 'POST'])
def rideDetails():
  if session.get('logged_in'):
    if request.method == 'POST':
      # if request.form['contenttype'] == "post":
      sourceAdd = request.form['sourceLocation']
      sourceCity = request.form['locality']
      sourceCountry = request.form['country']
      sourcePincode= request.form['postal_code']
      sourceLat, sourceLong = request.form['lat'], request.form['lng'] 
      destAdd = request.form['destinationLocation']
      destCity = request.form['destlocality']
      destCountry = request.form['destcountry']
      destPincode = request.form['destpostal_code']
      destLat, destLong = request.form['destlat'], request.form['destlng']
      # if sourceCity != destCity:
      #   flash('Source and Destination address should be in same CITY!')
      #   return redirect(request.url)
      g.db.execute('insert into rideDetails (userid, sourceaddress, sourcecity, sourcecountry, sourcepincode, sourcelat, sourcelong, destaddress, destcity, destcountry, destpincode, destlat, destlong, ridetime) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (session['userid'], sourceAdd, sourceCity, sourceCountry, sourcePincode, sourceLat, sourceLong, destAdd, destCity, destCountry, destPincode, destLat, destLong, request.form['rideTime']))
      g.db.commit()
      RideDetails = [sourceAdd, destAdd, request.form['rideTime']]
      return render_template("people-cluster.html", clustering = doCluster(sourceLat, sourceLong, destLat, destLong, sourceCity, request.form['rideTime'], sourcePincode))
      # else:
      #   flash('Something went wrong!')
      #   return redirect(request.url)
    elif request.method == 'GET':
      flash('Something went wrong!')
      return redirect(request.url)
  else:
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if session.get('logged_in'):
    return redirect(request.url_root)
  # username = request.form['username'].subn(r'<(script).*?</\1>(?s)', '', 0, data)[0]
  # print username
  if request.method == 'POST':
    getUser = g.db.execute('select * from logindetails where userid = ? or email = ? or phonenumber = ?', (request.form['userdetail'], request.form['userdetail'], request.form['userdetail']))
    userData = getUser.fetchone()
    if not userData:
      flash('Invalid Username!')
      return redirect(request.url)

    if userData[6] != request.form['password']:
      flash('Invalid Password!')
      return redirect(request.url) 
    else:
      session['logged_in'] = True
      session['username'] = request.form['userdetail']
      session['userid'] = userData[0]
      return redirect(request.url_root)
  return render_template('login.html')

@app.route('/profile')
def getProfile():
  if session.get('userid'):
    userid = session['userid']
  else:
    abort(404)
  if session.get('logged_in'):
    return render_template('profile.html', profile=getUserDetail(userid))
  else:
    abort(404)

@app.route('/authorlist')
def getAdminList():
  if session.get('userid'):
    userid = session['userid']
  else:
    abort(404)
  if session.get('logged_in'):
    return render_template('users.html', profile=getAuthors(userid), pages=get_pages())
  else:
    abort(404)

@app.route('/postlist/<userid>')
def getPostList(userid):
  if session.get('logged_in'):
    return render_template('userpost.html', posts=getPostsWithAuthor(userid), pages=get_pages())
  else:
    abort(404)

@app.route('/check-username', methods=['POST'])
def checkUser():
    if checkUsername(request.form['x']):
      return '1'
    return '0'

@app.route('/check-url', methods=['POST'])
def checkPostUrl():
    if not checkUrl(request.form['x']):
      return 'Give different Content Link!'

@app.route('/register', methods=['GET', 'POST'])
def doRegister():
  if request.method == 'POST':
    if not checkUsername(request.form['username']):
      flash('Username already exist!')
      return redirect(request.url)

  if session.get('logged_in'):
    return redirect(request.url_root)
  if request.method == 'POST':
    if request.form['password'] == request.form['confirmPassword']:
      g.db.execute('insert into logindetails (userid, firstname, lastname, gender, email, phonenumber, password, usertype) values (?, ?, ?, ?, ?, ?, ?, ?)',
                   (request.form['username'], request.form['firstname'], request.form['lastname'], request.form['gender'], request.form['emailid'], request.form['mobile_no'], request.form['password'], request.form['usertype']))
      g.db.commit()
      flash('You have registered successfully!')
      return redirect(request.url)
    else:
      error = 'Invalid password'
      session['error'] = error
      flash('Password do not match!')
      return redirect(request.url)
  return render_template('register.html')

@app.route('/profile/edit', methods=['GET', 'POST'])
def editPro():
  if not session.get('logged_in'):
    abort(404)
  return render_template('editprofile.html', profile=getUserDetail(session['userid']), pages=get_pages())

@app.route('/profile/edit/userdetail', methods=['POST'])
def ProfileEdit():
  if not session.get('logged_in'):
    abort(404)
  userid = session['userid']
  if request.method == 'POST':
    g.db.execute('UPDATE users SET fullname = ?, emailid = ?, mobile_no = ? WHERE userid = ?', (request.form['fullname'], request.form['emailid'], request.form['mobile_no'], userid))
    g.db.commit()
    return redirect(request.url_root)
  else:
      abort(404)

@app.route('/submit.comment/<posturl>', methods=['POST'])
def doComment(posturl):
  postid = getPostid(posturl)
  if session.get('logged_in'):
    userid = session['userid']
  else:
    userid = 0
  if request.method == 'POST':
    g.db.execute('insert into comments (postid, userid, comment) values (?, ?, ?)',(postid, userid, request.form['comment']))
    g.db.commit()
    if session.get('logged_in'):
      getDetail = g.db.execute('select fullname from users where userid= ?', (userid,))
      for x in getDetail.fetchall():
        username = x[0]
      return username
    return str(userid)
  else:
    abort(404)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  return redirect(request.url_root)

if __name__ == "__main__":
  init_db()
  app.run(host='0.0.0.0')
