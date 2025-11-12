import socket
import time
import struct
import read_from_robot 

SKOLEIP = '192.168.12.55'
SIMIP = '192.168.19.129'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SIMIP, 30002))

def sendCommand(cmd):
    '''
    Sends command in clear-text to robot.

    args:
        cmd: The full command with arguments (string)
   '''
    #cmd = 'def program():\n ' + cmd + '\nend\n'
    cmd = cmd + '\n'
    s.sendall(cmd.encode())


#test-command
#while True:
    #sendCommand('set_digital_out(0, False)')
    #time.sleep(1)
    #sendCommand('set_digital_out(0, True)')
    #time.sleep(1)

#print(pose)
'''
pose = read_from_robot.get_pose()
print(pose)
sendCommand('movel(p[0.200,-0.270,-0.250,-3.14,-0,-0], 0.1, 0.1)')
pose = read_from_robot.get_pose()
print(pose)
#time.sleep(1)
'''