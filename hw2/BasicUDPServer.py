#
# BasicUDPServer.py
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

serverPort = 31902
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))


while True:
    print("\nThe server is ready to receive on port", serverPort)
    
    while True:
        inputOption, clientAddress = serverSocket.recvfrom(2048)
            
        if inputOption.decode() in ['1', '2', '3', '4']:
            print('\nConnection requested from', clientAddress)    
            print('Command', inputOption.decode())
        
        # Reponse Upper Message
        if inputOption.decode() == '1':
            message, clientAddress = serverSocket.recvfrom(2048)
            modifiedMessage = message.decode().upper()
            serverSocket.sendto(modifiedMessage.encode(), clientAddress)
            
        # Reponse Lower Message
        elif inputOption.decode() == '2':
            message, clientAddress = serverSocket.recvfrom(2048)
            modifiedMessage = message.decode().lower()
            serverSocket.sendto(modifiedMessage.encode(), clientAddress)
        
        # Reponse Client Address and Port
        # Convert tuple to string
        # So clientAddress can be encoded
        elif inputOption.decode() == '3':
            serverSocket.sendto(str(clientAddress).encode(), clientAddress)
            
        # Response current Server Time
        elif inputOption.decode() == '4':
            serverTime = time.strftime("%Y-%m-%d %H:%M:%S")
            serverSocket.sendto(serverTime.encode(), clientAddress)
        
        # Client select option 5
        else:
            print("\nThe client has been terminated")
            break 
    
        
serverSocket.close()