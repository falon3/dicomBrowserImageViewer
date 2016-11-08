/*To change a user's privilege rights to Researcher run this line in mySQL in the database*/

UPDATE TABLE users SET acctype = 'Researcher' WHERE name='<username to be changed>'
