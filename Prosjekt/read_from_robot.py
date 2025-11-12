import socket
import struct
import numpy as np

SKOLEIP = '192.168.12.55'
SIMIP = '192.168.19.129'

DO_bit = [0] * 8
DI_bit = [0, 1, 2] * 4
#print(DI_bit)
#print(DI_bit.reverse())


def convert_cartesian(cart):
    cart = struct.unpack('!d', cart)[0]
    cart = format(cart*1000, '.4f')
    cart = float(cart)
    return cart

def convert_rad(rad):
    rad = struct.unpack('!d', rad)[0]
    rad = format(rad, '.4f')
    rad = float(rad)
    return rad

def convert_IO(IO):
    IO = struct.unpack('!d', IO)[0]
    IO = int(IO)
    IO = bin(IO)[2:].zfill(8)
    return IO


def wait_for_move_end():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Socket konfigurasjon

    s.connect((SIMIP, 30003))
    
    while(True):
        #Leser data
        #All posisjons-data er sett fra basen
        Discard = s.recv(444)

        X_actual = s.recv(8)  #X_actual value
        Y_actual = s.recv(8)  #Y_actual value
        Z_actual = s.recv(8)  #Z_actual Value
        Rx_actual = s.recv(8)  #Rx_actual Value
        Ry_actual = s.recv(8)  #Ry_actual Value
        Rz_actual = s.recv(8)  #Rz_actual Value
        
        X_speed = s.recv(8) #X_speed Value
        Y_speed = s.recv(8) #Y_speed Value
        Z_speed = s.recv(8) #Z_speed Value
        Rx_speed = s.recv(8) #Rx_speed Value
        Ry_speed = s.recv(8) #Rz_speed Value
        Rz_speed = s.recv(8) #Rz_speed Value

        Discard = s.recv(48)

        X_target = s.recv(8) #X_target value
        Y_target = s.recv(8) #Y_target value
        Z_target = s.recv(8) #Z_target value
        Rx_target = s.recv(8) #Rx_target Value
        Ry_target = s.recv(8) #Ry_target Value
        Rz_target = s.recv(8) #Rz_target Value

        Discard = s.recv(48)
        DI = s.recv(8) #Digital input values
        Discard = s.recv(352)
        DO = s.recv(8) #Digital output values
        Discard = s.recv(64)

        #Konverterer data
        X_actual = convert_cartesian(X_actual)
        Y_actual = convert_cartesian(Y_actual)
        Z_actual = convert_cartesian(Z_actual)

        Rx_actual = convert_rad(Rx_actual)
        Ry_actual = convert_rad(Ry_actual)
        Rz_actual = convert_rad(Rz_actual)

        X_speed = convert_cartesian(X_speed)
        Y_speed = convert_cartesian(Y_speed)
        Z_speed = convert_cartesian(Z_speed)

        Rx_speed = convert_rad(Rx_speed)
        Ry_speed = convert_rad(Ry_speed)
        Rz_speed = convert_rad(Rz_speed)

        X_target = convert_cartesian(X_target)
        Y_target = convert_cartesian(Y_target)
        Z_target = convert_cartesian(Z_target)

        Rx_target = convert_rad(Rx_target)
        Ry_target = convert_rad(Ry_target)
        Rz_target = convert_rad(Rz_target)

        #DO = convert_IO(DO)
        #DI = convert_IO(DI)
        '''
        for i in range(8):
            print('DO_%s' %i + ' = ' + DO[7-i])
            DO_bit[i] = DO[7-i]
        for i in range(8):
            print('DI_%s' %i + ' = ' + DI[7-i])
            DI_bit[i] = DI[7-i]
        '''
        #pose_actual = ([X_actual*0.01, Y_actual*0.01, Z_actual*0.01, Rx_actual, Ry_actual, Rz_actual])
        #if np.array_equal(pose,pose_actual):
        if X_speed < 0.005 and Y_speed < 0.005 and Z_speed < 0.005:
            print(f'loop has broken' )
            break
    s.close()


#X_actual-X_target == 0 and Y_actual-Y_target == 0 and Z_actual-Z_target == 0 and 

def get_pose():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Socket konfigurasjon

    s.connect((SIMIP, 30003))

    Discard = s.recv(444)

    X_actual = s.recv(8)  #X_actual value
    Y_actual = s.recv(8)  #Y_actual value
    Z_actual = s.recv(8)  #Z_actual Value
    Rx_actual = s.recv(8)  #Rx_actual Value
    Ry_actual = s.recv(8)  #Ry_actual Value
    Rz_actual = s.recv(8)  #Rz_actual Value
    
    X_speed = s.recv(8) #X_speed Value
    Y_speed = s.recv(8) #Y_speed Value
    Z_speed = s.recv(8) #Z_speed Value
    Rx_speed = s.recv(8) #Rx_speed Value
    Ry_speed = s.recv(8) #Rz_speed Value
    Rz_speed = s.recv(8) #Rz_speed Value

    Discard = s.recv(48)

    X_target = s.recv(8) #X_target value
    Y_target = s.recv(8) #Y_target value
    Z_target = s.recv(8) #Z_target value
    Rx_target = s.recv(8) #Rx_target Value
    Ry_target = s.recv(8) #Ry_target Value
    Rz_target = s.recv(8) #Rz_target Value

    Discard = s.recv(480)

    #Konverterer data
    X_actual = convert_cartesian(X_actual)
    Y_actual = convert_cartesian(Y_actual)
    Z_actual = convert_cartesian(Z_actual)

    Rx_actual = convert_rad(Rx_actual)
    Ry_actual = convert_rad(Ry_actual)
    Rz_actual = convert_rad(Rz_actual)

    X_speed = convert_cartesian(X_speed)
    Y_speed = convert_cartesian(Y_speed)
    Z_speed = convert_cartesian(Z_speed)

    Rx_speed = convert_rad(Rx_speed)
    Ry_speed = convert_rad(Ry_speed)
    Rz_speed = convert_rad(Rz_speed)

    X_target = convert_cartesian(X_target)
    Y_target = convert_cartesian(Y_target)
    Z_target = convert_cartesian(Z_target)

    Rx_target = convert_rad(Rx_target)
    Ry_target = convert_rad(Ry_target)
    Rz_target = convert_rad(Rz_target)

    pose = ([X_actual, Y_actual, Z_actual, Rx_actual, Ry_actual, Rz_actual])
    s.close()
    return pose

pose = get_pose()
print(pose)

