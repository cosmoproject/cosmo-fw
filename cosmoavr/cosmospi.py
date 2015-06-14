from __future__ import print_function
import spidev
import threading
import Queue

START = 2
END = 3
ESCAPE = 16

class CosmoSpi(threading.Thread):
    def __init__(self):
        self.spi = spidev.SpiDev(0,0)
        self.spi.max_speed_hz = int(500e3)
        threading.Thread.__init__(self)
        self.daemon = True
        self._txq = Queue.Queue(maxsize=2)
        self._rxq = Queue.Queue(maxsize=10)
        self._txmsg = []
        self._stop = False
        self._pending = {}

    def _escape(self, data):
        ret = []
        for d in data:
            if d in (START, END, ESCAPE):
                ret.append(ESCAPE)
            ret.append(d)
        return ret

    def call(self, command, data=[]):
        packet = [command] + data
        packet = [START] + self._escape(packet) + [END]
        reply_q = Queue.Queue(maxsize=1)
        self._txq.put((reply_q, packet))
        return reply_q.get(timeout=1)
        

    def write(self, packet):
        self._txq.put((None, [START] + self._escape(packet) + [END]))

    def read(self, timeout=1):
        try:
            return self._rxq.get(timeout=timeout)
        except Queue.Empty:
            return None

    def _readbytes(self, n):
        to_send = self._txmsg[:n]
        self._txmsg = self._txmsg[n:]
        if len(to_send) < n:
            to_send.extend([0] * (n-len(to_send)))
        ret = self.spi.xfer(to_send, int(150e3), 10, 8)
        #print("Exchanging", to_send, ret)
        return ret
        
    def stop(self):
        self._stop = True
        try:
            self._txq.put_nowait((None, []))
        except Queue.Full:
            pass
        self.join()

    def run(self):
        data = []
        last = -1
        while not self._stop:
            if not data:
                if not self._txmsg:
                    try:
                        handler, self._txmsg = self._txq.get(timeout=0.1)
                        if handler is not None:
                            self._txmsg += [0]*4 # For start of reply
                            command = self._txmsg[1]
                            assert command not in self._pending
                            self._pending[command] = handler
                    except Queue.Empty:
                        pass
                if not self._txmsg:
                    self._txmsg = [0]
                data = self._readbytes(len(self._txmsg))
            start_found = False
            while data:
                d = data.pop(0)
                if d == START and last != ESCAPE:
                    start_found = True
                    last = d
                    break
                elif d != 0:
                    print("Garbage:",d);
                last = d
            if not start_found:
                continue
            stop_found = False
            packet = []
            while not stop_found and not self._stop:
                if not data:
                    data = self._readbytes(max(10, len(self._txmsg)))
                escaped = False
                while data:
                    d = data.pop(0)
                    if escaped:
                        escaped = False
                        packet.append(d)
                    elif d == ESCAPE:
                        escaped = True
                    elif d == START:
                        # reset packet
                        packet = []
                    elif d == END:
                        stop_found = True
                        break
                    else:
                        packet.append(d)
            command = packet[0]
            if command in self._pending:
                self._pending[command].put(packet[1:])
                del self._pending[command]
            else:
                self._rxq.put(packet)
