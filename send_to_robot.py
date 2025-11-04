import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.12.55', 30002))

def sendCommand(cmd):
    #cmd = 'def program():\n ' + cmd + '\nend\n'
    cmd = cmd + '\n'
    s.sendall(cmd.encode())

i=0
while (i<5):
    sendCommand('set_digital_out(0, False)')
    time.sleep(1)
    sendCommand('set_digital_out(0, True)')
    time.sleep(1)

    i = i+1