from webkit import WebView
import pygtk
pygtk.require('2.0')
import sys, gtk, threading, time, glib
from nuimo import NuimoScanner, Nuimo, NuimoDelegate

glib.threads_init()

class App:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        sw = gtk.ScrolledWindow()
        self.view = WebView()
        sw.add(self.view)
        window.add(sw)
        self.loadUrls()
        window.fullscreen()
        window.show_all()
        self.view.open(self.urls[self.current])

        self.hadnuimoaction = False

        thread = threading.Thread(target=self.auto_loop)
        thread.daemon = True
        thread.start()

    def loadUrls(self):
        self.current = 0
        urlsPath = 'urls.csv'
        if len(sys.argv) > 1:
            urlsPath = sys.argv[1]
        
        try:
            with open(urlsPath) as f:
                self.urls = f.readlines()
                #remove empties
                self.urls = filter(None, self.urls)
        except:
            print 'failed to read ' + urlsPath
            self.urls = ['http://google.com']

    def next(self):
        self.current = (self.current + 1) % len(self.urls)
        self.view.open(self.urls[self.current])

    def previous(self):
        self.current = self.current - 1
        if self.current < 0:
            self.current = len(self.urls) - 1
        self.view.open(self.urls[self.current])
    
    def auto_loop(self):
        sleep = 18
        if len(sys.argv) > 2:
            sleep = float(sys.argv[2])

        while True:
            time.sleep(sleep)
            if self.hadnuimoaction == False:
                gtk.idle_add(self.next)
            else:
                self.hadnuimoaction = False

class CustomNuimoDelegate(NuimoDelegate):
    def __init__(self, nuimo, app):
        NuimoDelegate.__init__(self, nuimo)
        self.app = app
        
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
        if data == 1:
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
    app = App()
    
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
    
