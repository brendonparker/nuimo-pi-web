from bluepy.btle import UUID, Scanner, DefaultDelegate, Peripheral, BTLEException
import itertools
import struct
import sys
import time

if sys.version_info >= (3, 0):
    from functools import reduce

class ScanDelegate(DefaultDelegate):
    def __init__(self, scanner, notify):
        DefaultDelegate.__init__(self)
        self.notify = notify
        self.scanner = scanner

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            if dev.getValueText(9) == "Nuimo":
                self.scanner.stop()
                self.notify(dev.addr)

class NuimoScanner():
    def start(self, notify):
        scanner = Scanner()
        scanner.withDelegate(ScanDelegate(scanner, notify))
        scanner.scan(10.0)


class NuimoDelegate(DefaultDelegate):
    def __init__(self, nuimo):
        DefaultDelegate.__init__(self)
        self.nuimo = nuimo

    def handleBattery(self, data):
        print('BATTERY', data)

    def handleFly(self, data1, data2):
        print('FLY', data1, data2)

    def handleSwipe(self, data):
        print ('SWIPE', data)

    def handleRotation(self, data):
        print('ROTATE', data)
        
    def handleButton(self, data):
        print('BUTTON', data)

    def handleNotification(self, cHandle, data):
        if int(cHandle) == self.nuimo.characteristicValueHandles['BATTERY']:
            self.handleBattery(ord(data[0]))
        elif int(cHandle) == self.nuimo.characteristicValueHandles['FLY']:
            self.handleFly(ord(data[0]), ord(data[1]))
        elif int(cHandle) == self.nuimo.characteristicValueHandles['SWIPE']:
            self.handleSwipe(ord(data[0]))
        elif int(cHandle) == self.nuimo.characteristicValueHandles['ROTATION']:
            value = ord(data[0]) + (ord(data[1]) << 8)
            if value >= 1 << 15:
                value = value - (1 << 16)
            self.handleRotation(value)
        elif int(cHandle) == self.nuimo.characteristicValueHandles['BUTTON']:
            self.handleButton(ord(data[0]))
            
        
class NuimoConsoleLoggerDelegate(DefaultDelegate):
    def __init__(self, nuimo):
        DefaultDelegate.__init__(self)
        self.nuimo = nuimo

    def handleNotification(self, cHandle, data):
        if int(cHandle) == self.nuimo.characteristicValueHandles['BATTERY']:
            print('BATTERY', ord(data[0]))
        elif int(cHandle) == self.nuimo.characteristicValueHandles['FLY']:
            print('FLY', ord(data[0]), ord(data[1]))
        elif int(cHandle) == self.nuimo.characteristicValueHandles['SWIPE']:
            print('SWIPE', ord(data[0]))
        elif int(cHandle) == self.nuimo.characteristicValueHandles['ROTATION']:
            value = ord(data[0]) + (ord(data[1]) << 8)
            if value >= 1 << 15:
                value = value - (1 << 16)
            print('ROTATION', value)
        elif int(cHandle) == self.nuimo.characteristicValueHandles['BUTTON']:
            print('BUTTON', ord(data[0]))
            
class Nuimo:
    SERVICE_UUIDS = [
        UUID('0000180f-0000-1000-8000-00805f9b34fb'), # Battery
        UUID('f29b1525-cb19-40f3-be5c-7241ecb82fd2'), # Sensors
        UUID('f29b1523-cb19-40f3-be5c-7241ecb82fd1')  # LED Matrix
    ]

    CHARACTERISTIC_UUIDS = {
        UUID('00002a19-0000-1000-8000-00805f9b34fb') : 'BATTERY',
        UUID('f29b1529-cb19-40f3-be5c-7241ecb82fd2') : 'BUTTON',
        UUID('f29b1528-cb19-40f3-be5c-7241ecb82fd2') : 'ROTATION',
        UUID('f29b1527-cb19-40f3-be5c-7241ecb82fd2') : 'SWIPE',
        UUID('f29b1526-cb19-40f3-be5c-7241ecb82fd2') : 'FLY',
        UUID('f29b1524-cb19-40f3-be5c-7241ecb82fd1') : 'LED_MATRIX'
    }

    NOTIFICATION_CHARACTERISTIC_UUIDS = [
        #'BATTERY', # Uncomment only if you are not using the iOS emulator (iOS does't support battery updates without authentication)
        'BUTTON',
        'ROTATION',
        'SWIPE',
        'FLY']

    # Notification data
    NOTIFICATION_ON  = struct.pack("BB", 0x01, 0x00)
    NOTIFICATION_OFF = struct.pack("BB", 0x00, 0x00)

    def __init__(self, macAddress):
        self.macAddress = macAddress

    def set_delegate(self, delegate):
        self.delegate = delegate

    def connect(self):
        self.peripheral = Peripheral(self.macAddress, addrType='random')
        # Retrieve all characteristics from desires services and map them from their UUID
        characteristics = list(itertools.chain(*[self.peripheral.getServiceByUUID(uuid).getCharacteristics() for uuid in Nuimo.SERVICE_UUIDS]))
        characteristics = dict((c.uuid, c) for c in characteristics)
        # Store each characteristic's value handle for each characteristic name
        self.characteristicValueHandles = dict((name, characteristics[uuid].getHandle()) for uuid, name in Nuimo.CHARACTERISTIC_UUIDS.items())
        # Subscribe for notifications
        for name in Nuimo.NOTIFICATION_CHARACTERISTIC_UUIDS:
            self.peripheral.writeCharacteristic(self.characteristicValueHandles[name] + 1, Nuimo.NOTIFICATION_ON, True)
        self.peripheral.setDelegate(self.delegate)

    def waitForNotifications(self):
        self.peripheral.waitForNotifications(1.0)

    def displayLedMatrix(self, matrix, timeout, brightness = 1.0):
        matrix = '{:<81}'.format(matrix[:81])
        bytes = list(map(lambda leds: reduce(lambda acc, led: acc + (1 << led if leds[led] not in [' ', '0'] else 0), range(0, len(leds)), 0), [matrix[i:i+8] for i in range(0, len(matrix), 8)]))
        self.peripheral.writeCharacteristic(self.characteristicValueHandles['LED_MATRIX'], struct.pack('BBBBBBBBBBBBB', bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7], bytes[8], bytes[9], bytes[10], max(0, min(255, int(255.0 * brightness))), max(0, min(255, int(timeout * 10.0)))), True)
