"""Small, dependency-free Chrome DevTools client for local QA only."""
import base64
import json
import os
import socket
import struct
import time
import urllib.request
from urllib.parse import urlsplit


class Browser:
    def __init__(self, port=9333):
        self.port = port
        request = urllib.request.Request(f'http://127.0.0.1:{port}/json/new?about:blank', method='PUT')
        with urllib.request.urlopen(request) as response:
            target = json.load(response)
        self.target = target['id']
        url = urlsplit(target['webSocketDebuggerUrl'])
        self.socket = socket.create_connection((url.hostname, url.port), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.socket.sendall((f'GET {url.path} HTTP/1.1\r\nHost: {url.netloc}\r\n'
                             f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
                             f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n'
                             f'Origin: http://localhost:{port}\r\n\r\n').encode())
        response = b''
        while not response.endswith(b'\r\n\r\n'):
            response += self.socket.recv(1)
        assert response.startswith(b'HTTP/1.1 101 '), response
        self.sequence = 0
        self.events = []
        for domain in ('Page', 'Runtime', 'Network', 'Log'):
            self.call(domain + '.enable')

    def _read(self, length):
        result = b''
        while len(result) < length:
            chunk = self.socket.recv(length - len(result))
            if not chunk:
                raise ConnectionError('Chrome closed the connection')
            result += chunk
        return result

    def _send(self, payload, opcode=1):
        mask = os.urandom(4)
        length = len(payload)
        header = bytes([0x80 | opcode])
        if length < 126:
            header += bytes([0x80 | length])
        elif length < 65536:
            header += bytes([0x80 | 126]) + struct.pack('!H', length)
        else:
            header += bytes([0x80 | 127]) + struct.pack('!Q', length)
        data = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
        self.socket.sendall(header + mask + data)

    def _receive(self):
        parts = []
        while True:
            first, second = self._read(2)
            length = second & 127
            if length == 126:
                length = struct.unpack('!H', self._read(2))[0]
            elif length == 127:
                length = struct.unpack('!Q', self._read(8))[0]
            mask = self._read(4) if second & 128 else None
            payload = self._read(length)
            if mask:
                payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
            if first & 15 == 9:
                self._send(payload, 10)
                continue
            if first & 15 == 8:
                raise ConnectionError('Chrome closed the WebSocket')
            parts.append(payload)
            if first & 128:
                return json.loads(b''.join(parts))

    def call(self, method, params=None):
        self.sequence += 1
        sequence = self.sequence
        self._send(json.dumps({'id': sequence, 'method': method, 'params': params or {}}).encode())
        while True:
            message = self._receive()
            if message.get('id') == sequence:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message.get('result', {})
            self.events.append(message)

    def evaluate(self, expression):
        result = self.call('Runtime.evaluate', {'expression': expression, 'awaitPromise': True, 'returnByValue': True})
        if 'exceptionDetails' in result:
            raise RuntimeError(result['exceptionDetails'])
        return result['result'].get('value')

    def viewport(self, width, height=900, dpr=1):
        self.call('Emulation.setDeviceMetricsOverride', {
            'width': width, 'height': height, 'deviceScaleFactor': dpr, 'mobile': False})

    def navigate(self, url):
        self.events = []
        self.call('Page.navigate', {'url': url})
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if self.evaluate('document.readyState') == 'complete':
                break
            time.sleep(0.1)
        self.evaluate('Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 5000))]).then(() => true)')

    def key(self, key, code=None, modifiers=0):
        vk = {'Tab': 9, 'Enter': 13, 'Escape': 27, ' ': 32}.get(key, 0)
        data = {'key': key, 'code': code or key, 'windowsVirtualKeyCode': vk, 'modifiers': modifiers}
        if key in ('Enter', ' '):
            data['text'] = '\r' if key == 'Enter' else ' '
            data['unmodifiedText'] = data['text']
        self.call('Input.dispatchKeyEvent', {'type': 'keyDown', **data})
        self.call('Input.dispatchKeyEvent', {'type': 'keyUp', **data})

    def screenshot(self, path, full=False):
        params = {'format': 'png', 'captureBeyondViewport': full}
        if full:
            size = self.call('Page.getLayoutMetrics')['cssContentSize']
            params['clip'] = {**size, 'scale': 1}
        result = self.call('Page.captureScreenshot', params)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(result['data']))

    def close(self):
        self.socket.close()
        with urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/close/{self.target}'):
            pass
