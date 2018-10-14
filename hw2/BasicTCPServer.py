#
# BasicTCPServer.py
# 20131902 Park Ji Woon
#

import socket
import time
import signal

def handler(signum, frame):
    print('\nBye bye~')
    serverSocket.close()
    exit(0)
    
# Ctrl+C exception handling
signal.signal(signal.SIGINT, handler)

serverName = 'nsl2.cau.ac.kr'
serverPort = 21902

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverName, serverPort))
serverSocket.listen(1)

while True:
    print("\nThe server is ready to receive on port", serverPort)
    (connectionSocket, clientAddress) = serverSocket.accept()
        
    while True:
        inputOption = connectionSocket.recv(2048)
        
        if inputOption.decode() in ['1', '2', '3', '4']:
            print('\nConnection requested from', clientAddress)    
            print('Command', inputOption.decode())
        
        # Reponse Upper Message
        if inputOption.decode() == '1':
            message = connectionSocket.recv(2048)
            modifiedMessage = message.decode().upper()
            connectionSocket.send(modifiedMessage.encode())
             
        # Reponse Lower Message
        elif inputOption.decode() == '2':
            message = connectionSocket.recv(2048)
            modifiedMessage = message.decode().lower()
            connectionSocket.send(modifiedMessage.encode())
               
        # Reponse Client Address and Port
        # Convert tuple to string
        # So clientAddress can be encoded
        elif inputOption.decode() == '3':
            connectionSocket.send(str(clientAddress).encode())
                    
        # Response current Server Time
        elif inputOption.decode() == '4':
            serverTime = time.strftime("%Y-%m-%d %H:%M:%S")
            connectionSocket.send(serverTime.encode())
            
        # Client select option 5
        else:
            print("\nThe client has been terminated")
            connectionSocket.close()
            break                             

serverSocket.close()