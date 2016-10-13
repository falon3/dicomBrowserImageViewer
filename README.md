# dicomBrowserImageViewer
This is a web-based tool that allows dicom format(ultrasound/MRI) 3D images to be converted and viewed/scrolled in the browser. 

This project is specifically intended to be used for assessing dicom images of hips for dysplasia.

# to clone and setup locally:
inside of project directory run the following commands
```
$ virtualenv flask
$ flask/bin/pip install flask
```
    
# to setup with apache
edit the apache config file (ie. /etc/apache2/apache2.conf) to add with something like the following

```
<VirtualHost *:8000>

    WSGIDaemonProcess app user=www-data group=www-data threads=5 python-path=/var/www/html/dicom/:/var/www/html/dicom/flask/lib/python2.7/site-packages/
    WSGIScriptAlias / /var/www/html/dicom/wsgi.py

    <Directory /var/www/html/dicom>
        WSGIProcessGroup app
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```
add this line to the ports.conf file in the same directory
```
Listen 8000
```
Then create a symbolic link for apache to this project directory from the command line:
```
$ sudo ln -s /var/www/html/dicom <location of this project>
```
and then restart apache, ie.

```
$ sudo /etc/init.d/apache2 restart
```
 
# note: 
Test images currently located locally in the images folder. Database to come later

#Contributers:
Falon Scheers, David Turner, Andrew Whittle
