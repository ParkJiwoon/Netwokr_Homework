#
# BasicUDPClient.py
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
serverPort = 31902

# Random Port Number
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(('', 0))

print("The client is running on port", clientSocket.getsockname()[1])

while True:
    print('<Menu>')
    print('1) convert text to UPPER-case')
    print('2) convert text to LOWER-case')
    print('3) get my IP address and port number')
    print('4) get server time')
    print('5) exit')
    
    # input command number
    # The UDP client becomes blocked when it calls the recvfrom function
    # It could not get return value via recvfrom function.
    # So, I did not handle 'Server Off' exceptions
    inputOption = input('Input option: ')        
    
    if inputOption == '1':
        clientSocket.sendto(inputOption.encode(), (serverName, serverPort))
        message = input('Input sentence: ')      
        
        start = time.time() 
        clientSocket.sendto(message.encode(), (serverName, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        
        end = time.time()
        elapsed = end - start
        
        print('Reply from server:', modifiedMessage.decode())
        print('\nResponse time:',round(elapsed*1000, 1), 'ms\n')
        
        
    elif inputOption == '2':
        clientSocket.sendto(inputOption.encode(), (serverName, serverPort))
        message = input('Input sentence: ')  
        
        start = time.time() 
        clientSocket.sendto(message.encode(), (serverName, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        
        end = time.time()
        elapsed = end - start
        
        print('Reply from server:', modifiedMessage.decode())
        print('\nResponse time:',round(elapsed*1000, 1), 'ms\n')
    
    
    elif inputOption == '3':
        start = time.time() 
        clientSocket.sendto(inputOption.encode(), (serverName, serverPort))
        clientAddr, serverAddress = clientSocket.recvfrom(2048)
        
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
        clientSocket.sendto(inputOption.encode(), (serverName, serverPort))
        serverTime, serverAddress = clientSocket.recvfrom(2048)
        
        end = time.time()
        elapsed = end - start
        
        print('Reply from server: time =',serverTime.decode())
        print('\nResponse time:',round(elapsed*1000, 1), 'ms\n')
    
    
    elif inputOption == '5':
        clientSocket.sendto(inputOption.encode(), (serverName, serverPort))
        break    
    
    # Client must select option 1~5
    else:
        print('Please enter the correct value\n')


clientSocket.close()
