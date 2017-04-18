# tumblr2telegram
Get instant notification of observed tumblr blog update to telegram bot.

#### Install some essential packages and use PM2 to make this application daemonized, monitored and kept alive forever.

# Install & Setup
Install packages as following instructions
``` shell
pip install pytumblr telegram-send
```
Get Tumblr access credentials from the Tumblr API console at https://api.tumblr.com/console.  
Then configure **telegram-send** by entering the bot credentials created by Telegram Bot.

Install PyExifTool
``` shell
git clone git://github.com/smarnach/pyexiftool.git
python setup.py install [--user|--prefix=<installation-prefix]
```
Install PM2
``` shell
npm install pm2 -g 
```

# Usage
Add some blog names at blog list, then start fetching and pushing service using following command:
``` shell
pm2 start main.py
```
And use these commands for auto start when host machine is rebooted
``` shell
pm2 startup
pm2 save
```
