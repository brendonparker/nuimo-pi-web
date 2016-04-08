#Raspberry Pi Web-Signage with Nuimo Controller
This repo demonstrates controlling a "digital-signage" dashboard using a Nuimo controller. For now there are several different approaches, all of which revolve around using a config file (`urls.csv`, you need to create this) of webpages and then cyclcing through the webpages on a timer.

- `app.py` has a single WebView that gets reloaded at some interval. You can use the Nuimo controller to advance by pressing the button or swiping forward or backward.
- `app3.py` was an attempt at having several views, to speed up rendering by pre-loading the next and previous pages. However, the experience on the PI isn't too great; when a webview loads, it haults the PI and results in a not-so-great user experience. I've left it in there as a sample.
- `app4.py` is what I'd recommend playing with. This allows rotation, which allows the user to rotate to a specific page, then press the button to select it. Similar idea to `app3.py` except I didn't actually render the page, just showed the title at the bottom.

## Installation/Setup from fresh Raspbian Image
1. install latest Jessie image (full, not-lite) (https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)
- `sudo apt-get update` (Update latest bits)
2. Install bluez library
- `sudo apt-get install --no-install-recommends bluetooth` (Installs bluez)
- `sudo hciconfig hci0 up` (Enables your Bluetooth dongle)
- _Optional_: `sudo hcitool lescan` (Should discover your Nuimo, press Ctrl+C to stop discovery)
3. Install bluepy library
- `sudo apt-get install build-essential libglib2.0-dev libdbus-1-dev python-setuptools git` (Installs build dependencies and git)
- `sudo pip install -U pip` (Upgrade Pip to latest version)
- `sudo pip install https://github.com/IanHarvey/bluepy/archive/master.zip#bluepy`
4. Install python-webkit
- `sudo apt-get install python-webkit`
4. Pull this repo
- `git clone https://github.com/brendonparker/nuimo-py-web`

### WebKit References
https://github.com/although2013/Ticket_prices/blob/master/README.md
https://andyortlieb.wordpress.com/2010/05/21/webkit-python-gtk-on-debian-lenny/
http://trac.webkit.org/wiki/UsingGitWithWebKit

## Auto-Start (Kiosk mode)
copy the `py.desktop` into `$HOME/.config/autostart`
you may need to edit the path to the app within that file, depending on where you ran your git clone from.

### Update autostart
To disable screensaver and mouse, use the below as reference to go into your `/etc/xdg/lxsession/LXDE/autostart`
I've found it helpful to install `unclutter`: `sudo apt-get install unclutter`

````
    @lxpanel --profile LXDE
    @pcmanfm --desktop --profile LXDE
    #@xscreensaver -no-splash

    #hide mouse
    @unclutter

    #disable screensaver
    @xset x off
    @xset s noblank
    @xset -dpms

````

## Configuration
  - Create a `urls.csv` in the directory of the `app.py` with a list of URLs that you wish to be cycled through as a part of the signage.

## YouTube Demo
[![YouTube Demo](http://img.youtube.com/vi/15om36vGzek/0.jpg)](http://www.youtube.com/watch?v=15om36vGzek)

## TODOS:
  - Install script
  - Some sort of input (perhaps double tap, or swipe down) to re-display IP Address
