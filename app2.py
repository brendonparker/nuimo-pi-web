from webkit import WebView
import pygtk
pygtk.require('2.0')
import gtk, threading, time
from nuimo import NuimoScanner, Nuimo, NuimoDelegate

class App:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        fixed = gtk.Fixed()
        views = [WebView(), WebView(), WebView()]
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height()

        for idx, view in enumerate(views):
            view.set_usize(width, height)
            fixed.put(views[idx], -width+(idx*width), 0)
        
        window.add(fixed)
        #self.loadUrls()
        window.fullscreen()
        window.show_all()

        views[0].open('http://google.com?q=page1')
        views[1].open('http://google.com?q=page2')
        views[2].open('http://google.com?q=page3')

        self.views = views
        self.fixed = fixed
        self.x = 0
        self.width = width

    def rotate(self, val):
        w = self.width
        x = self.x = (self.x - val) % (3 * w)
        for idx, view in enumerate(self.views):
            if idx == 0 and x > w:
                self.fixed.move(view, ((idx+3)*w)-x, 0)
            else:
                self.fixed.move(view, (idx*w)-x, 0)

    def loadUrls(self):
        self.current = 0
        try:
            with open('urls.csv') as f:
                self.urls = f.readlines()
                #remove empties
                self.urls = filter(None, self.urls)
        except:
            print 'failed to read urls.csv'
            self.urls = ['http://google.com']

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
