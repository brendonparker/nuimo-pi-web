import os, re

class IpAddress():
    def ipaddress(self, interface = 'wlan0'):
        f = os.popen('ifconfig ' + interface)
        p = re.compile('inet addr:(.*?) ')
        
        line = ' '.join(f.readlines())
        m = p.search(line)
        if m == None:
            return 'Unknown'
        else:
            return m.group(1)
