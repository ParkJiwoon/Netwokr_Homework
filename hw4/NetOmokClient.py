#
# NetOmokClient.py
# 20131902 Park Ji Woon
#

import socket
import select
import sys
import signal

def print_board(b, ROW, COL):

    print("\n   ", end="")
    for j in range(0, COL):
        print("%2d" % j, end="")

    print()
    print("  ", end="")
    for j in range(0, 2*COL+3):
        print("-", end="")
    
    print()
    for i in range(0, ROW):
        print("%d |" % i, end="")
        for j in range(0, COL):
            c = b[i][j]
            if c == 0:
                print(" +", end="")
            elif c == 1:
                print(" 0", end="")
            elif c == 2:
                print(" @", end="")
            else:
                print("ERROR", end="")
        print(" |")

    print("  ", end="")
    for j in range(0, 2*COL+3):
        print("-", end="")
    
    print()

def closeSocket():
    ''' close all sockets '''
    for i, csocket in enumerate(inputs):
        csocket.close()
        
    clientSocket.close()
    sys.exit()

def handler(signum, frame):
    print('\nBye bye~')
    clientSocket.close()
    sys.exit()  
    
def makeSendList(check, data):
    sendData = []
    sendData.append(check)
    sendData.append(data)
    
    return str(sendData).encode()


serverName = '58.232.196.145'
serverPort = 31902 

# Ctrl+C exception handling
signal.signal(signal.SIGINT, handler)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
try:
    clientSocket.connect((serverName, serverPort))        
# When server is off, client try to connect
except Exception as e:
    print('Can not connect to the server', serverName)
    sys.exit()
        
# Connect successful and check nickname
if len(sys.argv) == 2:
    sendMsg = makeSendList(1, sys.argv[1])
    clientSocket.send(sendMsg)
else:
    print('Input correct argv: python <client> <nickname>')
    clientSocket.close()
    sys.exit()

playerState = 0

while True:
    try:     
        # inputs : socket list
        inputs = [sys.stdin, clientSocket]  
        readable, writable, exceptional = select.select(inputs, [], [], 5)
        
        for s in readable:
            if s is clientSocket:
                data = s.recv(2048)
                
                if not data:
                    print('Can not connect to server ', serverName)
                    closeSocket()
                else:                 
                    recvData = eval(data.decode())   
                    
                    if recvData[0] is 1:
                        ''' data is wrong message '''
                        print(recvData[1])
                        closeSocket()
                        
                    elif recvData[0] is 2:
                        ''' data is playgame message '''
                        print(recvData[1])
                        playerState = 1
                        
                    elif recvData[0] is 3:
                        ''' data is board '''
                        (board, ROW, COL, message) = recvData[1]
                        print_board(board, ROW, COL)
                        print(message)
                        
                    elif recvData[0] is 4:
                        ''' data is response time out message '''
                        print(recvData[1])
                        playerState = 0
                        
                    else:
                        ''' data is normal message '''
                        print(recvData[1])
                    
                
            else:           
                ''' you can send message when you chat '''       
                inputMessage = input()  
                
                if playerState is 0:                       
                    sendMsg = makeSendList(0, inputMessage)                
                    clientSocket.send(sendMsg)
                    
                elif playerState is 1:
                    if inputMessage == 'y' or inputMessage == 'n':
                        sendMsg = makeSendList(2, inputMessage) 
                        clientSocket.send(sendMsg)
                        playerState = 0
                    
            
    # Ctrl + C exception
    except KeyboardInterrupt:
        print('\nBye bye~')
        closeSocket()

closeSocket()
