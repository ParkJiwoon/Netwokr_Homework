#
# NonBlockingTCPServer.py
# 20131902 Park Ji Woon
#

import select
import socket
import time
import signal

def handler(signum, frame):
    print('\nBye bye~')
    serverSocket.close()
    exit(0)

# Number of client are global variable
clientNum = 0

# Ctrl+C exception handling
signal.signal(signal.SIGINT, handler)

serverName = 'nsl2.cau.ac.kr'
serverPort = 21902
    
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverName, serverPort))
serverSocket.listen()

# clients : client Address List, cIndex : client Number List
inputs = [serverSocket]  
clients = []
cIndex = []

print("\nThe server is ready to receive on port", serverPort)
clientNum = 0
clientIndex = 0
    
while True:
    readable, writable, exceptional = select.select(inputs, [], [])
    
    for s in readable:              
        # new client connect
        if s is serverSocket:
            (connectionSocket, clientAddress) = serverSocket.accept()
            clientNum = clientNum + 1
            clientIndex = clientIndex + 1
            
            cIndex.append(clientIndex)
            clients.append(connectionSocket.getpeername())
            inputs.append(connectionSocket)
            print("\nClient", clientIndex, "connected. Number of connected clients =",clientNum)
            
        # receve data
        else:
            data = s.recv(2048)
            clientAddr = s.getpeername()                
            
            #get client Address which sended data
            for i, addr in enumerate(clients):
                if addr == clientAddr:
                    idx = cIndex[i]
            
            # if server received data
            if data:
                recvList = eval(data.decode())
                inputOption = recvList[0]
                
                
                if inputOption in ['1', '2', '3', '4']:
                    print('\nConnection requested from', clientAddr)    
                    print('Command', inputOption)
        
                # Reponse Upper Message
                if inputOption == '1':
                    # Convert string to tuple
                    message = recvList[1]
                    modifiedMessage = message.upper()
                    s.send(modifiedMessage.encode())
                     
                # Reponse Lower Message
                elif inputOption == '2':
                    message = recvList[1]
                    modifiedMessage = message.lower()
                    s.send(modifiedMessage.encode())
                       
                # Reponse Client Address and Port
                # Convert tuple to string
                # So clientAddress can be encoded
                elif inputOption == '3':
                    s.send(str(clientAddr).encode())
                            
                # Response current Server Time
                elif inputOption == '4':
                    serverTime = time.strftime("%Y-%m-%d %H:%M:%S")
                    s.send(serverTime.encode())
                    
                # Client select option 5
                else:
                    clientNum = clientNum - 1
                    print("\nClient", idx, "disconnected. Number of connected clients =",clientNum);
                    s.close()
                    cIndex.remove(idx)
                    clients.remove(clientAddr)
                    inputs.remove(s)
                
            #if server didn't received data (client disconnected)
            else:
                clientNum = clientNum - 1
                print("\nClient", idx, "disconnected. Number of connected clients =",clientNum);
                s.close()
                cIndex.remove(idx)
                clients.remove(clientAddr)
                inputs.remove(s)
                            
        
serverSocket.close()