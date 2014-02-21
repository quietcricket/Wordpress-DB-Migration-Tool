# Wordpress DB Migration Tool

## What is it for

* Export Wordpress database into an sql file
* Replace local url (e.g. 'http://localhost/wp') with live url (e.g. 'http://wewearglasses.com')
* Import sql database into your local database
* Replace the live url (or other developers' url) with you local url
* Automatically change 'localhost' into your machine's IP address (for testing on mobile devices)


## Supported OS

* OSX only for now
* You can grab the python code and configure it for Windows or Linux


## How to use

* Place the app file into your wordpress folder
* I prefer to put it in the theme's folder which I normally work on intensively
* Launch the app and configure the path to your MySQL's bin folder
* Configure the local url and live url
* Click "Export DB" will export your database
* The exported database will be in the same folder as the app. The filename will be "[your-wp-db].sql" (The app scans your wp-config.php file and the name follows the settings there)
* If you want to import database, make sure you put the "[your-wp-db].sql" into the same folder as the app

## Todo

* Add an icon
* Configure the plist of the app 