from webkit import WebView
import pygtk
pygtk.require('2.0')
import gtk, threading, time, glib
from nuimo import NuimoScanner, Nuimo, NuimoDelegate

glib.threads_init()

class App:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        fixed = gtk.Fixed()
        views = [WebView(), WebView(), WebView()]
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()

        for idx, view in enumerate(views):
            view.set_usize(width, height)
            fixed.put(views[idx], idx*width, 0)
        
        window.add(fixed)
        self.loadUrls()
        window.fullscreen()
        window.show_all()

        views[0].open(self.urls[0])
        views[1].open(self.urls[1])
        views[2].open(self.urls[2])

        self.views = views
        self.fixed = fixed
        self.x = 0
        self.width = width

    def loadUrls(self):
        self.current = 2
        try:
            with open('urls.csv') as f:
                self.urls = f.readlines()
                #remove empties
                self.urls = filter(None, self.urls)
        except:
            print 'failed to read urls.csv'
            self.urls = ['http://google.com?q=page1', 'http://google.com?q=page2', 'http://google.com?q=page3']        

    def rotate(self, val):
        w = self.width
        oldX = self.x
        newX = self.x - val
        x = self.x = newX % (3 * w)

        def loadUrl(idx, url_idx):
            url = self.urls[url_idx]
            self.views[idx].open(url)
            print (url_idx, idx, url)
        def incrementCurrent(idx):
            self.current = (self.current + 1) % len(self.urls)
            loadUrl(idx, self.current)
        def decrementCurrent(idx):
            self.current = self.current - 1
            if self.current < 0:
                self.current = len(self.urls) - 1
            temp = self.current - 2
            if temp < 0:
                temp = len(self.urls) - temp
            loadUrl(idx, self.current)
        
        if (oldX < .5 * w) and (newX >= .5 * w):
            incrementCurrent(2)
        elif (oldX < 1.5 * w) and (newX >= 1.5 * w):
            incrementCurrent(0)
        elif (oldX < 2.5 * w) and (newX >= 2.5 * w):
            incrementCurrent(1)
        elif (oldX > .5 * w) and (newX <= .5 * w):
            decrementCurrent(1)
        elif (oldX > 1.5 * w) and (newX <= 1.5 * w):
            decrementCurrent(2)
        elif (oldX > 2.5 * w) and (newX <= 2.5 * w):
            decrementCurrent(1)
             
        for idx, view in enumerate(self.views):
            if idx == 0 and x > w:
                self.fixed.move(view, ((idx+3)*w)-x, 0)
            else:
                self.fixed.move(view, (idx*w)-x, 0)

    def next(self):
        self.current = (self.current + 1) % len(self.urls)
        self.view.open(self.urls[self.current])

    def previous(self):
        self.current = self.current - 1
        if self.current < 0:
            self.current = len(self.urls) - 1
        self.view.open(self.urls[self.current])


class CustomNuimoDelegate(NuimoDelegate):
    def __init__(self, nuimo, app):
        NuimoDelegate.__init__(self, nuimo)
        self.app = app

    def handleRotation(self, value):
        NuimoDelegate.handleRotation(self, value)
        gtk.idle_add(app.rotate, value)
        
    def handleSwipe(self, value):
        NuimoDelegate.handleSwipe(self, value)
        if value == 0:
            gtk.idle_add(app.next)
        elif value == 1:
            gtk.idle_add(app.previous)
            
    def handleButton(self, value):
        NuimoDelegate.handleButton(self, value)
        if value == 1:
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
    try:
        gtk.main()
    except Exception, e:
        print '%s', e
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

