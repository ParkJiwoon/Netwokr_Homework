#
# BasicTCPClient.py
# 20131902 Park Ji Woon
#

import socket
import time
import signal

def handler(signum, frame):
    print('\nBye bye~')
    clientSocket.close()
    exit(0)

# Ctrl+C exception handling
signal.signal(signal.SIGINT, handler)

serverName = 'nsl2.cau.ac.kr'
serverPort = 21902 

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

print("The client is running on port", clientSocket.getsockname()[1])

while True:
    print('<Menu>')
    print('1) convert text to UPPER-case')
    print('2) convert text to LOWER-case')
    print('3) get my IP address and port number')
    print('4) get server time')
    print('5) exit')
    
    # input command number
    inputOption = input('Input option: ')    
    
    if inputOption == '1':        
        clientSocket.send(inputOption.encode())        
        message = input('Input sentence: ')   
        
        start = time.time()
        clientSocket.send(message.encode())
        modifiedMessage = clientSocket.recv(2048)
        
        end = time.time()
        elapsed = end - start
        
        # Server Off exception handling
        if not modifiedMessage:
            print("The server is off")
            break        
        
        print('Reply from server:', modifiedMessage.decode())
        # ms = 1000 * seconds
        print('\nResponse time:',round(elapsed*1000, 1), 'ms\n')
        
        
    elif inputOption == '2':        
        clientSocket.send(inputOption.encode())        
        message = input('Input sentence: ')    
        
        start = time.time()
        clientSocket.send(message.encode())
        modifiedMessage = clientSocket.recv(2048)
        
        end = time.time()
        elapsed = end - start
        
        if not modifiedMessage:
            print("The server is off")
            break        
        
        print('Reply from server:', modifiedMessage.decode())
        print('\nResponse time:',round(elapsed*1000, 1), 'ms\n')
    
    
    elif inputOption == '3':   
        start = time.time()
        clientSocket.send(inputOption.encode()) 
        clientAddr = clientSocket.recv(2048)
                
        end = time.time()
        elapsed = end - start
        
        if not clientAddr:
            print("The server is off")
            break        
        
        # Convert string to tuple
        Addr = eval(clientAddr.decode())
        clientIP = Addr[0]
        clientPort = Addr[1]
        print('Reply from server: IP =', clientIP, ', Port =', clientPort)
        print('\nResponse time:',round(elapsed*1000, 1), 'ms\n')
    
    
    elif inputOption == '4':
        start = time.time()
        clientSocket.send(inputOption.encode())        
        serverTime = clientSocket.recv(2048)
        
        end = time.time()
        elapsed = end - start
        
        if not serverTime:
            print("The server is off")
            break        
        
        print('Reply from server: time =',serverTime.decode())
        print('\nResponse time:',round(elapsed*1000, 1), 'ms\n')
    
    
    elif inputOption == '5':
        clientSocket.send(inputOption.encode())
        break
    
    # Client must select option 1~5
    else:
        print('Please enter the correct value\n')   
    

clientSocket.close()
