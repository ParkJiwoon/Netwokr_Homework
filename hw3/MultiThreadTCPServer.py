#
# MultiThreadTCPServer.py
# 20131902 Park Ji Woon
#

import socket
import time
import signal
import threading

def handler(signum, frame):
    print('\nBye bye~')
    serverSocket.close()
    exit(0)

# Number of client are global variable
clientNum = 0

def clientHandler(connectionSocket, clientAddress, Index):
    while True:
        data = connectionSocket.recv(2048)
        
        # if server received data
        if data:            
            recvList = eval(data.decode())
            inputOption = recvList[0]
            
            if inputOption in ['1', '2', '3', '4']:
                print('\nConnection requested from', clientAddress)    
                print('Command', inputOption)
            
            # Reponse Upper Message
            if inputOption == '1':
                # Convert string to tuple
                message = recvList[1]
                modifiedMessage = message.upper()
                connectionSocket.send(modifiedMessage.encode())
                 
            # Reponse Lower Message
            elif inputOption == '2':
                message = recvList[1]
                modifiedMessage = message.lower()
                connectionSocket.send(modifiedMessage.encode())
                   
            # Reponse Client Address and Port
            # Convert tuple to string
            # So clientAddress can be encoded
            elif inputOption == '3':
                connectionSocket.send(str(clientAddress).encode())
                        
            # Response current Server Time
            elif inputOption == '4':
                serverTime = time.strftime("%Y-%m-%d %H:%M:%S")
                connectionSocket.send(serverTime.encode())
                
            # Client select option 5
            else:
                break
        
        #if server didn't received data (client disconnected)
        else:
            break
        
    global clientNum
    clientNum = clientNum - 1
    print("\nClient", Index, "disconnected. Number of connected clients =",clientNum);
    connectionSocket.close() 
    
# Ctrl+C exception handling
signal.signal(signal.SIGINT, handler)

if __name__=="__main__":
    serverName = 'nsl2.cau.ac.kr'
    serverPort = 21902
    
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((serverName, serverPort))
    serverSocket.listen(5)
    
    print("\nThe server is ready to receive on port", serverPort)
    # client number
    clientIndex = 0
    
    while True:
        (connectionSocket, clientAddress) = serverSocket.accept()
       
        clientNum = clientNum + 1
        clientIndex = clientIndex + 1
        print("\nClient", clientIndex, "connected. Number of connected clients =",clientNum);
        threading._start_new_thread(clientHandler, (connectionSocket, clientAddress, clientIndex))
                             
    
    serverSocket.close()