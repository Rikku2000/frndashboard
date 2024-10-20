FRN Client Console (AlterFRN) - Dashboard by 13MAD86 / Martin

!!! WARING !!!
Please use the script at your own risk, do not harm me if any corruption to your system, thanks.

Install copy the files to the home directory on the device e.g:
- /home/pi/

You need to install Python 3 and psutil, do it like:
- sudo apt-get install python3-dev python3-pip
- sudo pip3 install psutil

please note that you need to edit 2 files on your system:
- frndashboard.service @ ExecStart

You need to determint the dashboard to run it at boot of the device.
--- ExecStart=/usr/bin/sudo /usr/bin/python3 /home/pi/dashboard.py ---

- dashboard.py
The following lines need also to be edited to work on your system:

Here you need to define where your config file are locatated (at line 23):
- config.read(r'/home/pi/frnconsole.cfg')

Here you need to define where the web script files are located (at line 27):
- WEBPATH = "/home/pi/dashboard"

Same as in config.read, you need to define the config file location (at line 219):
- with open(r'/home/pi/frnconsole.cfg', 'w') as configfile:
