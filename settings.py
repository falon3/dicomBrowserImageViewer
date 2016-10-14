database = dict(
    user = 'falon',
    password = 'rootpass',
    db_name = 'dcmviewer',
    host = 'localhost',
)

'''NOTE: in order for this user and password to be accepted may need 
 to run this query in mySQL:

mysql>
grant all privileges on <db_name>.* to <user>@<host> 
identified by <password> 
with grant option;

'''
