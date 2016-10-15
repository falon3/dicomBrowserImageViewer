database = dict(
    user = 'falon',
    passwd = 'rootpass',
    db = 'dcmviewer',
    host = 'localhost',
)

'''NOTE: in order for this user and password to be accepted may need 
 to run this query in mySQL:

mysql>
GRANT ALL privileges ON <db>.* TO <user>@<host> 
identified by <passwd> 
WITH GRANT OPTION;


MAY ALSO need to login as root on <db> to mysql and give necessary GLOBAL privileges
so that uploading can happen for this user with these queries:

GRANT ALL ON *.* TO <user>@<host>;
GRANT SELECT, INSERT ON *.* TO <user>@<host>;

'''
