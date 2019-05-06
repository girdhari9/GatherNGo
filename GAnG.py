#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3, os, datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, current_app, flash
from contextlib import closing
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
import googlemaps, pandas as pd
import geopy.distance
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

# Creating the application.
app = Flask(__name__)
app.config.from_object("config")

app.config['GOOGLEMAPS_KEY'] = "AIzaSyD9JkQXx1V6_Z9XUUcIXsUlYHpeCst3AcI"

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

def getUserDetail(userid):
  getDetail = g.db.execute('select * from logindetails where userid= ?', (userid,))
  userDetail = getDetail.fetchone()
  return userDetail

def checkUsername(username):
  getUser = g.db.execute('select userid from logindetails where userid= ?',(username,))
  if not getUser.fetchone():
    return True
  return False

def createCluster(distancelist):
  userList = []
  for key, val in distancelist.items(): 
    if val <= 1:
      userList.append(key[0])
  return userList
      
def getUsersDetail(userList):
  userdata = []
  userDetails = g.db.execute('SELECT * FROM logindetails')
  for val in userList:
    for dbval in userDetails.fetchall():
      if val == dbval[0]:
        userdata.append(dbval)
  return userdata

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

@app.route('/check-username', methods=['POST'])
def checkUser():
    if checkUsername(request.form['x']):
      return '1'
    return '0'

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

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  return redirect(request.url_root)

if __name__ == "__main__":
  init_db()
  GoogleMaps(app)
  app.run(host='0.0.0.0')
