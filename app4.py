from webkit import WebView
import pygtk
pygtk.require('2.0')
import sys, gtk, threading, time, glib
import xml.sax.saxutils
from nuimo import NuimoScanner, Nuimo, NuimoDelegate
from ipaddress import IpAddress

ip = IpAddress()
glib.threads_init()

class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        # Fixed Container
        self.fixed = gtk.Fixed()
        self.add(self.fixed)

        # Get Screen Info
        self.width = width = gtk.gdk.screen_width()
        self.height = height = gtk.gdk.screen_height()

        # Label
        self.label = gtk.Label()
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        self.label.set_usize(width, 50)
        self.label.set_label(ip.ipaddress())
        self.fixed.put(self.label, 0, height-50)

        # WebView        
        self.webview = WebView()
        self.webview.set_usize(width, height - 50)
        self.fixed.put(self.webview, 0, 0)

        self.loadUrls()
        self.fullscreen()
        self.open()
        self.hadnuimoaction = False

        self.showIpAddress()

        thread = threading.Thread(target=self.auto_loop)
        thread.daemon = True
        thread.start()

    def showIpAddress(self):
        text = '<span weight="bold" size="xx-large">%s</span>' % ip.ipaddress()
        self.label.set_markup(text)
        self.webview.set_usize(self.width, self.height-50)

    def loadUrls(self):
        self.current = 0
        urlsPath = 'urls.csv'

        def split(x):
            return map(str.rstrip, x.split(','))
        
        if len(sys.argv) > 1:
            urlsPath = sys.argv[1]
        try:
            with open(urlsPath) as f:
                self.urls = map(split, f.readlines())
        except:
            print 'failed to read ' + urlsPath
            self.urls = ['http://google.com', 'Google']

    def open(self):
        self.rotating = False
        self.rotateval = 0
        self.webview.set_usize(self.width, self.height)
        self.webview.open(self.urls[self.current][0])

    def login(self):
        if self.webview.props.uri == 'https://www.pivotaltracker.com/signin':
            # TODO: Put your username and password here:
            user = 'user@domain.com'
            pwd = 'password'
            script = "$('#credentials_username').val('%s'); $('#credentials_password').val('%s'); $('#signin_form').submit();" % (user, pwd)
            self.webview.execute_script(script)

    def rotate(self, val):
        self.rotating = True
        self.rotateval += val
        count = len(self.urls)
        idx = (self.current + (self.rotateval / 100)) % count
        text = '%s (%d/%d)' % (self.urls[idx][1], idx+1, count)
        text = xml.sax.saxutils.escape(text)
        text = '<span weight="bold" size="xx-large">%s</span>'%(text)
        #print text
        self.label.set_markup(text)
        self.webview.set_usize(self.width, self.height-50)
        
    def next(self):
        count = len(self.urls)
        if self.rotating == False:
            self.current = (self.current + 1) % count
        else:
            self.current = (self.rotateval / 100) % count
        self.open()

    def previous(self):
        self.current = self.current - 1
        if self.current < 0:
            self.current = len(self.urls) - 1
        self.open()
    
    def auto_loop(self):
        sleep = 18
        if len(sys.argv) > 2:
            sleep = float(sys.argv[2])

        while True:
            time.sleep(10)
            gtk.idle_add(self.login)    
            time.sleep(sleep-10)
            
            if self.hadnuimoaction == False:
                gtk.idle_add(self.next)
            else:
                self.hadnuimoaction = False

class CustomNuimoDelegate(NuimoDelegate):
    def __init__(self, nuimo, app):
        NuimoDelegate.__init__(self, nuimo)
        self.app = app

    def handleRotation(self, data):
        NuimoDelegate.handleRotation(self, data)
        self.app.hadnuimoaction = True
        gtk.idle_add(self.app.rotate, data)
        
    def handleSwipe(self, data):
        NuimoDelegate.handleSwipe(self, data)
        self.app.hadnuimoaction = True
        if data == 1:
            gtk.idle_add(app.next)
        else:
            gtk.idle_add(app.previous)
            
    def handleButton(self, data):
        NuimoDelegate.handleButton(self, data)
        self.app.hadnuimoaction = True
        if data == 0:
            gtk.idle_add(app.next)

def showImagesOnNuimo(nuimo):
    nuimo.displayLedMatrix(
        "         " +
        " ***     " +
        " *  * *  " +
        " *  *    " +
        " ***  *  " +
        " *    *  " +
        " *    *  " +
        " *    *  " +
        "         ", 2.0)
    time.sleep(2)
    nuimo.displayLedMatrix(
        " **   ** " +
        " * * * * " +
        "  *****  " +
        "  *   *  " +
        " * * * * " +
        " *  *  * " +
        " * * * * " +
        "  *   *  " +
        "   ***   ", 20.0)

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    app = MainWindow()
    app.connect("destroy", lambda q: gtk.main_quit())
    app.show_all()
    
    def nuimo_process():
        
        def foundDevice(addr):
            print 'found device: ' + addr
            nuimo = Nuimo(addr)
            nuimo.set_delegate(CustomNuimoDelegate(nuimo, app))
            nuimo.connect()
            showImagesOnNuimo(nuimo)
            
            while True:
                nuimo.waitForNotifications()

        while True:
            try:
                NuimoScanner().start(foundDevice)
            except Exception, e:
                print 'failed to connect to nuimo: %s' % e
                time.sleep(5)


    thread = threading.Thread(target=nuimo_process)
    thread.daemon = True
    thread.start()
    
    main()
    
