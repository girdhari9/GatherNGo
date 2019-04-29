create table if not exists logindetails ( 
  userid text primary key ,
  firstname text not null,
  lastname text not null,
  gender text not null,
  email text not null,
  phonenumber text not null,
  password text not null,
  usertype text not null,
  created_at TIMESTAMP
  DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP null,
  FOREIGN KEY  (userid) REFERENCES persondetails(userid)
);

create table if not exists ridedetails (
  transactionid integer primary key autoincrement,
  userid text not null,
  sourceaddress text not null,
  sourcecity text not null,
  sourcecountry text not null,
  sourcepincode integer not null,
  sourcelat text not null,
  sourcelong text not null,
  destaddress text not null,
  destcity text not null,
  destcountry text not null,
  destpincode integer not null,
  destlat text not null,
  destlong text not null,
  ridebookingdate TIMESTAMP
  DEFAULT CURRENT_TIMESTAMP,
  ridetime TIMESTAMP null,
  created_at TIMESTAMP
  DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP null,
  FOREIGN KEY  (userid) REFERENCES persondetails(userid)
);

create table if not exists walletdetails (
  userid text primary key,
  walletamount text not null,
  transactionid integer not null,
  created_at TIMESTAMP
  DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP null,
  FOREIGN KEY  (userid) REFERENCES persondetails(userid),
  FOREIGN KEY  (transactionid) REFERENCES ridedetails(transactionid)
 );

 
 
