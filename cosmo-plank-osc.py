# Python script that reads values from COSMO Plank and send them 
# to a specified host (bonjour name) using OSC

#!/usr/bin/python
from cosmoavr.cosmoplank import CosmoPlank as CosmoHat
from time import sleep, time
import OSC

timeout = 2

TOLERANCE = 0.001
box_num = 1

port_expr = 9000+box_num 
port_toggle = 9900+box_num 

send_address_expr = 'lemuria.local', port_expr
send_address_toggle = 'lemuria.local', port_toggle


def safesleep(amt):
    if amt > 0:
        sleep(amt)

def run(c, o_e, o_t):
    switch_state = c.switches()
    switch_last = switch_state
    last_knobs = c.knobs()
    first = True

    count = 0
    now = time()
    toggle = []

    connected = True

    while True:
        try:
            knobs = c.knobs()
            changed = [abs(n-l) > TOLERANCE for n,l in zip(knobs, last_knobs)]  
            last_knobs = knobs

            for i, (knob, change) in enumerate(zip(knobs, changed)):
                if change or first:
                    address = '/Lemur/Box%i/Expr%s' % (box_num,str(i+1))
                    msg = OSC.OSCMessage()
                    msg.setAddress(address)
                    msg.append(knob)
                    print msg #"=" * int(knob*100)
                    try:
                        o_e.send(msg)
                    except OSC.OSCClientError as exception:
                        print exception

            switches = c.switches()
            posedge = [s and not l for s,l in zip(switches, switch_last)]
            changed = [s != l for s,l in zip(switches, switch_last)]
            switch_last = switches

            for i, edge in enumerate(posedge):
                if edge or first:
                    switch_state[i] = not switch_state[i]
                    address = '/Lemur/Box%i/Toggle%i' % (box_num,(i+1))
                    msg = OSC.OSCMessage()
                    msg.setAddress(address)
                    data = int(switch_state[i])
                    # Scale for MIDI values
                    msg.append(data*127)
                    try:
                        o_t.send(msg)
                    except OSC.OSCClientError as exception:
                        print exception
                    print msg
        except connected as exception:
            print "Connection failed!"
            print connected


        now += 0.005
        safesleep(now-time())
        count += 1
        first = False

def main():
    c = CosmoHat()

    now = time()

    o_e = OSC.OSCClient()
    o_t = OSC.OSCClient()

    connected = False

    print "\nConnecting to %s\n" % send_address_expr[0]

    while connected == False: 
        try:
            o_e.connect(send_address_expr)
            o_t.connect(send_address_toggle)
            connected = True
            print "Connected!"
        except OSC.OSCClientError as exception:
            connected = False
            print "Not connected!"
            safesleep(timeout)

    try:
        while True:
            run(c, o_e, o_t)
    finally:
        c.stop()

main()
