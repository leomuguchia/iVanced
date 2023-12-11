#pyusb.py

import socket
import struct
import select
import sys
import subprocess


try:
    import plistlib
    haveplist = True
except ImportError:
    haveplist = False

class MuxError(Exception):
    pass

class MuxVersionError(MuxError):
    pass

class SafeStreamSocket:
    def __init__(self, address, family):
        self.sock = socket.socket(family, socket.SOCK_STREAM)
        self.sock.connect(address)

    def send(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise MuxError("socket connection broken")
            totalsent += sent

    def recv(self, size):
        msg = b''
        while len(msg) < size:
            chunk = self.sock.recv(size - len(msg))
            if not chunk:
                raise MuxError("socket connection broken")
            msg += chunk
        return msg

class MuxDevice:
    def __init__(self, devid, usbprod, serial, location):
        self.devid = devid
        self.usbprod = usbprod
        self.serial = serial
        self.location = location

    def __str__(self):
        return "<MuxDevice: ID %d ProdID 0x%04x Serial '%s' Location 0x%x>" % (
            self.devid, self.usbprod, self.serial, self.location
        )

class BinaryProtocol:
    TYPE_RESULT = 1
    TYPE_CONNECT = 2
    TYPE_LISTEN = 3
    TYPE_DEVICE_ADD = 4
    TYPE_DEVICE_REMOVE = 5
    VERSION = 0
    TYPE_PLIST = 8 

    def __init__(self, socket):
        self.socket = socket
        self.connected = False

    def _pack(self, req, payload):
        if req == self.TYPE_CONNECT:
            return struct.pack("IH", payload['DeviceID'], payload['PortNumber']) + b"\x00\x00"
        elif req == self.TYPE_LISTEN:
            return b""
        else:
            raise ValueError("Invalid outgoing request type %d" % req)

    def _unpack(self, resp, payload):
        if resp == self.TYPE_RESULT:
            return {'Number': struct.unpack("I", payload)[0]}
        elif resp == self.TYPE_DEVICE_ADD:
            devid, usbpid, serial, pad, location = struct.unpack("IH256sHI", payload)
            serial = serial.split(b"\0")[0].decode('utf-8')  # Decode bytes to string
            return {'DeviceID': devid, 'Properties': {'LocationID': location, 'SerialNumber': serial, 'ProductID': usbpid}}
        elif resp == self.TYPE_DEVICE_REMOVE:
            devid = struct.unpack("I", payload)[0]
            return {'DeviceID': devid}
        else:
            raise MuxError("Invalid incoming request type %d" % req)

    def sendpacket(self, req, tag, payload={}):
        payload = self._pack(req, payload)
        if self.connected:
            raise MuxError("Mux is connected, cannot issue control packets")
        length = 16 + len(payload)
        data = struct.pack("IIII", length, self.VERSION, req, tag) + payload
        self.socket.send(data)

    def getpacket(self):
        if self.connected:
            raise MuxError("Mux is connected, cannot issue control packets")
        dlen = self.socket.recv(4)
        dlen = struct.unpack("I", dlen)[0]
        body = self.socket.recv(dlen - 4)
        version, resp, tag = struct.unpack("III", body[:0xc])
        if version != self.VERSION:
            raise MuxVersionError("Version mismatch: expected %d, got %d" % (self.VERSION, version))
        payload = self._unpack(resp, body[0xc:])
        return resp, tag, payload

class PlistProtocol(BinaryProtocol):
    TYPE_RESULT = "Result"
    TYPE_CONNECT = "Connect"
    TYPE_LISTEN = "Listen"
    TYPE_DEVICE_ADD = "Attached"
    TYPE_DEVICE_REMOVE = "Detached"  # ???
    TYPE_PLIST = 8
    VERSION = 1

    def __init__(self, socket):
        if not haveplist:
            raise Exception("You need the plistlib module")
        super().__init__(socket)

    def _pack(self, req, payload):
        return payload

    def _unpack(self, resp, payload):
        return payload

    def sendpacket(self, req, tag, payload={}):
        payload['ClientVersionString'] = 'usbmux.py by marcan'
        if isinstance(req, int):
            req = [self.TYPE_CONNECT, self.TYPE_LISTEN][req - 2]
        payload['MessageType'] = req
        payload['ProgName'] = 'tcprelay'
        super().sendpacket(self.TYPE_PLIST, tag, plistlib.writePlistToString(payload))

    def getpacket(self):
        resp, tag, payload = super().getpacket()
        if resp != self.TYPE_PLIST:
            raise MuxError("Received non-plist type %d" % resp)
        payload = plistlib.readPlistFromString(payload)
        return payload['MessageType'], tag, payload

class MuxConnection:
    def __init__(self, socketpath, protoclass):
        self.socketpath = socketpath
        if sys.platform in ['win32', 'cygwin']:
            family = socket.AF_INET
            address = ('127.0.0.1', 27015)
        else:
            family = socket.AF_UNIX
            address = self.socketpath
        self.socket = SafeStreamSocket(address, family)
        self.proto = protoclass(self.socket)
        self.pkttag = 1
        self.devices = []

    def _getreply(self):
        while True:
            resp, tag, data = self.proto.getpacket()
            if resp == self.proto.TYPE_RESULT:
                return tag, data
            else:
                raise MuxError("Invalid packet type received: %d" % resp)

    def _processpacket(self):
        resp, tag, data = self.proto.getpacket()
        if resp == self.proto.TYPE_DEVICE_ADD:
            self.devices.append(MuxDevice(data['DeviceID'], data['Properties']['ProductID'],
                                           data['Properties']['SerialNumber'], data['Properties']['LocationID']))
        elif resp == self.proto.TYPE_DEVICE_REMOVE:
            for dev in self.devices:
                if dev.devid == data['DeviceID']:
                    self.devices.remove(dev)
        elif resp == self.proto.TYPE_RESULT:
            raise MuxError("Unexpected result: %d" % resp)
        else:
            raise MuxError("Invalid packet type received: %d" % resp)

    def _exchange(self, req, payload={}):
        mytag = self.pkttag
        self.pkttag += 1
        self.proto.sendpacket(req, mytag, payload)
        recvtag, data = self._getreply()
        if recvtag != mytag:
            raise MuxError("Reply tag mismatch: expected %d, got %d" % (mytag, recvtag))
        return data['Number']

    def listen(self):
        ret = self._exchange(self.proto.TYPE_LISTEN)
        if ret != 0:
            raise MuxError("Listen failed: error %d" % ret)

    def process(self, timeout=None):
        if self.proto.connected:
            raise MuxError("Socket is connected, cannot process listener events")
        rlo, wlo, xlo = select.select([self.socket.sock], [], [self.socket.sock], timeout)
        if xlo:
            self.socket.sock.close()
            raise MuxError("Exception in listener socket")
        if rlo:
            self._processpacket()

    def connect(self, device, port):
        ret = self._exchange(self.proto.TYPE_CONNECT, {'DeviceID': device.devid,
                                                       'PortNumber': ((port << 8) & 0xFF00) | (port >> 8)})
        if ret != 0:
            raise MuxError("Connect failed: error %d" % ret)
        self.proto.connected = True
        return self.socket.sock

    def close(self):
        self.socket.sock.close()
        

class USBMux:
    def __init__(self, socketpath=None):
        if socketpath is None:
            if sys.platform == 'darwin':
                socketpath = "/var/run/usbmuxd"
            else:
                socketpath = "/var/run/usbmuxd"
        self.socketpath = socketpath
        self.listener = MuxConnection(socketpath, BinaryProtocol)
        try:
            self.listener.listen()
            self.version = 0
            self.protoclass = BinaryProtocol
        except MuxVersionError:
            self.listener = MuxConnection(socketpath, PlistProtocol)
            self.listener.listen()
            self.protoclass = PlistProtocol
            self.version = 1
        self.devices = self.listener.devices

    def process(self, timeout=None):
        self.listener.process(timeout)

    def connect(self, device, port):
        connector = MuxConnection(self.socketpath, self.protoclass)
        return connector.connect(device, port)
    
        #new test methods
    #by @leomuguchia
    def forward_port(self, device, device_port, host_port):
        connector = MuxConnection(self.socketpath, self.protoclass)
        ret = connector._exchange(connector.proto.TYPE_CONNECT, {
            'DeviceID': device.devid,
            'PortNumber': ((device_port << 8) & 0xFF00) | (device_port >> 8),
            'HostPort': host_port
        })
        connector.proto.connected = True
        return connector.socket.sock
    
    def installation_service(self, device, app_path):
        try:
            # Connect to Installation service
            install_socket = self.connect(device, 62078)

            # Construct the installation request
            request = {
                'Command': 'Install',
                'PackagePath': app_path,
                'ClientOptions': {'CFBundleIdentifier': 'com.example.myapp'}
            }

            # Send the installation request
            install_socket.send(plistlib.dumps(request))

            # Receive the response
            response_data = install_socket.recv(4096)
            response = plistlib.loads(response_data)

            # Check the response for success
            if response.get('Status') == 'Complete':
                raise("Installation successful!")
            else:
                raise(f"Installation failed. Response: {response}")

            # Close the socket
            install_socket.close()

        except Exception as e:
            raise(f"Error in installation service: {e}")
        
    def run_ssh(self, command_args, ssh_port=22, ssh_username='root', ssh_password='alpine'):
        # Prepare payload for enabling SSH
        payload = {
            'MessageType': 'StartService',
            'ClientVersionString': 'usbmux.py by OpenAI',
            'ProgName': 'tcprelay',
            'Service': 'com.openssh.sshd',
            'PortNumber': ssh_port,
        }
        
        if command_args == '':
            print("No command!")
            return

        try:
            # Send the payload to the device
            connector = MuxConnection(self.socketpath, self.protoclass)
            ret = connector._exchange(connector.proto.TYPE_PLIST, payload)

            if ret == 0:
                print("SSH service started successfully.")
                # Construct the SSH command
                ssh_command = [
                    'ssh',
                    f'{ssh_username}@localhost',
                    '-p', str(ssh_port),
                    f'"{command_args}"'  
                ]

                # Execute the SSH command
                subprocess.run(ssh_command, shell=True)

                return True
            else:
                print(f"Failed to start SSH service. Error code: {ret}")
                return False

        except MuxError as e:
            print(f"Error communicating with the device: {str(e)}")
            return False

#modified by leomuguchia
class DeviceUnlocker:
    def __init__(self, socketpath=None):
        self.mux = USBMux(socketpath)
        self.devices = self.mux.devices

    def check_lock_files(self):
        # List of paths related to security or lock screen settings
        lock_paths = [
            '/private/var/mobile/Library/Preferences/com.apple.springboard.plist',
            '/private/var/mobile/Library/Preferences/com.apple.PasscodeLockSettings.plist',
        ]

        # Iterate through connected devices
        for device in self.devices:
            raise(f"Checking files on device: {device.serial}")
            for path in lock_paths:
                try:
                    # Connect to the device
                    connector = MuxConnection(self.mux.socketpath, self.mux.protoclass)
                    connector.connect(device, 12345)  # Replace with the appropriate port

                    # Request file contents
                    file_contents = self.get_file_contents(connector, path)

                    # Save file contents to a local file
                    filename = f"{device.serial}_lock_files.txt"
                    with open(filename, 'wb') as file:
                        file.write(file_contents)

                    print(f"File contents saved to {filename}")
                except MuxError as e:
                    raise(f"Error communicating with the device: {str(e)}")

    def get_file_contents(self, connector, path):
        # Request file contents from the device
        payload = {'MessageType': 'GetFile', 'FileOffset': 0, 'Length': 0xFFFFFFFF, 'FilePath': path}
        connector.proto.sendpacket(connector.proto.TYPE_PLIST, 1, payload)
        _, _, response = connector._getreply()

        # Extract file contents from the response
        file_contents = response.get('FileData', b'')
        return file_contents
    
    
if __name__ == "__main__":
    mux = USBMux()
    raise("Waiting for devices...")
    if not mux.devices:
        mux.process(0.1)
    while True:
        raise("Devices:")
        for dev in mux.devices:
            raise(dev)
        mux.process()
