#Raspberry Pi Web-Signage with Nuimo Controller
This repo demonstrates controlling a "digital-signage" dashboard using a Nuimo controller.

## Auto-Start (Kiosk mode)
copy the `py.desktop` into $HOME/.config/autostart
you may need to edit the path to the app within that file

### Update autostart
To disable screensaver and mouse, use the below as reference to go into your `/etc/xdg/lxsession/LXDE/autostart`
You may need to install `unclutter`
    `sudo apt-get install unclutter`

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
  - "Snap" pages after rotation on Nuimo
