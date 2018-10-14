#
# NetOmokServer.py
# 20131902 Park Ji Woon
#

import select
import socket
import signal
import time
import threading

ROW = 10
COL = 10
clientIndex = 0
resTimer = None
timer = None

def check_win(b, x, y):
    last_stone = b[x][y]
    start_x, start_y, end_x, end_y = x, y, x, y

    # check x
    while (start_x - 1 >= 0 and
            b[start_x - 1][y]  == last_stone):
        start_x -= 1
    while (end_x + 1 < ROW and
            b[(end_x + 1)][y] == last_stone):
        end_x += 1
    if end_x - start_x + 1 >= 5:
        return last_stone

    # check y
    start_x, start_y, end_x, end_y = x, y, x, y
    while (start_y - 1 >= 0 and
            b[x][start_y - 1] == last_stone):
        start_y -= 1
    while (end_y + 1 < COL and
            b[x][end_y + 1] == last_stone):
        end_y += 1
    if end_y - start_y + 1 >= 5:
        return last_stone
    
    # check diag 1
    start_x, start_y, end_x, end_y = x, y, x, y
    while (start_x - 1 >= 0 and start_y - 1 >= 0 and
            b[start_x - 1][start_y - 1] == last_stone):
        start_x -= 1
        start_y -= 1
    while (end_x + 1 < ROW and end_y + 1 < COL and
            b[end_x + 1][end_y + 1] == last_stone):
        end_x += 1
        end_y += 1
    if end_y - start_y + 1 >= 5:
        return last_stone
    
    # check diag 2
    start_x, start_y, end_x, end_y = x, y, x, y
    while (start_x - 1 >= 0 and end_y + 1 < COL and
            b[start_x - 1][end_y + 1] == last_stone):
        start_x -= 1
        end_y += 1
    while (end_x + 1 < ROW and start_y - 1 >= 0 and
            b[end_x + 1][start_y - 1] == last_stone):
        end_x += 1
        start_y -= 1
    if end_y - start_y + 1 >= 5:
        return last_stone
    
    return 0

def initGame():
    gameState = 0
    gamePlayer = []
    gameTurn = -1
    gameWin = 0
    gameCount = 0
    board = [[0 for row in range(ROW)] for col in range(COL)]
    
    return (gameState, gamePlayer, gameTurn, gameWin, gameCount, board)


def closeSocket():
    ''' close all sockets and exit '''
    for i, csocket in enumerate(inputs):
        csocket.close()
        
    serverSocket.close()
    exit(0)

def handler(signum, frame):
    print('\nBye bye~')
    closeSocket()    
    
def makeSendMsg(check, data):
    ''' make list for sending to clients '''
    sendData = [check, data]
    
    return str(sendData).encode()

def removeSocket(sock, sender):
    ''' remove sock from connected socket list '''
    clientInfos.remove(sender)
    sock.close()
    inputs.remove(sock)
    
    if sender[2] != '':        
        sendToAll(0, str(sender[2]) + " disconnected. There are " + str(getNumberOfClient()) + " users now")
        

def findSocketIndex(nickname):
    target = -1
    for i, clientInfo in enumerate(clientInfos):
        if clientInfo[2] == nickname:
            target = i
            
    return target
    
def sendToAll(check, data):
    ''' send message to all except sender '''
    message = makeSendMsg(check, data)
    for i, csocket in enumerate(inputs):
        try:            
            if i != 0 and csocket != s and clientInfos[i][2] != '':
                csocket.send(message) 
        except Exception as e:
            csocket.close()
            inputs.remove(csocket)
            
def sendToAllExceptTwo(check, data, nickname):
    ''' send message to all except sender and target '''
    message = makeSendMsg(check, data)    
    target = findSocketIndex(nickname)
    
    for i, csocket in enumerate(inputs):
        try:            
            if i != 0 and csocket != s and clientInfos[i][2] != '' and i != target:
                csocket.send(message) 
        except Exception as e:
            csocket.close()
            inputs.remove(csocket)            
            
def sendToOne(check, data, nickname):
    ''' send message to only one '''
    message = makeSendMsg(check, data)    
    target = findSocketIndex(nickname)
    
    if target == -1:
        sendToSender(0, "There is no user: " + str(nickname))
    else:        
        for i, csocket in enumerate(inputs):
            try:            
                if i == target:
                    csocket.send(message) 
            except Exception as e:
                csocket.close()
                inputs.remove(csocket)
                    
    
def sendToSender(check, data):
    ''' send message to sender '''
    message = makeSendMsg(check, data)
    try:
        s.send(message)
    except Exception as e:
        s.close()
        inputs.remove(s)        
        
def registerNickname(nickname):
    ''' check duplication and register nickname '''
    duplication = False
                        
    if nickname.find('\\') is not -1 or nickname.find(' ') is not -1:
        sendToSender(1, "Do not use \\ or space in nickname")
                            
    # check duplicate nickname
    for i, clientInfo in enumerate(clientInfos):
        if clientInfo[2] is nickname:
            print('Duplicate nickname')
            duplication = True
            break
                                
    if duplication is not True:                            
        ''' add nickname and assign index '''
        for i, clientInfo in enumerate(clientInfos):
            if senderClient is clientInfo: 
                clientInfos[i][1] = clientIndex
                clientInfos[i][2] = nickname
                    
        sendToSender(0, "\nwelcome " + str(senderClient[2]) + " to net-omok chat room at " + str(senderClient[0]) + ". You are " + str(senderClient[1]) + "th user\n")
        sendToAll(0, str(senderClient[2]) + " connected. There are " + str(getNumberOfClient()) + " users now")
                    
    else:
        sendToSender(1, "duplicate nickname. cannot connect")
        
def getNumberOfClient():
    num = 0
    
    for i, clientInfo in enumerate(clientInfos):
        if clientInfo[2] != '':
            num = num + 1
            
    return num-1

def setTimer():
    global gameTurn, timerCheck, gamePlayer, gameCount, gameState, gameWin, board
    
    if len(gamePlayer) == 2:        
        if gameTurn == 0:          
            winner, loser = gamePlayer[1], gamePlayer[0]
        else:
            winner, loser = gamePlayer[0], gamePlayer[1]
            
        message = str(loser) + " timeout! " + str(winner) + " win!"                                        
        sendToSender(0, message)    
        sendToAll(0, message)
        
        timerCheck = 0
        (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
        
        
def responseTimer():
    global gameTurn, timerCheck2, gamePlayer, gameCount, gameState, gameWin, board, responseClient
    
    if findSocketIndex(responseClient) != -1 and findSocketIndex(requestClient) != -1:
        sendToOne(4, "input timeout", str(responseClient))
        sendToOne(0, str(responseClient) + " input timeout", str(requestClient))
        
    timerCheck2 = 0
    (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
        

serverName = '58.232.196.145'
serverPort = 31902

# Ctrl+C exception handling
signal.signal(signal.SIGINT, handler)    

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverName, serverPort))
serverSocket.listen(8)

# inputs : socket list
inputs = [serverSocket]  

# [[(Ip, Port), index, nickname], [(Ip, Port), index, nickname]]
clientInfos = [[0 for col in range(0)] for row in range(0)]
clientInfos.append([0,0,0,0])

print("\nThe server is ready to receive on port", serverPort)
    
timerCheck = 0
timerCheck2 = 0
responseClient = ""
requestClient = ""
(gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()    


while inputs:
    try:
        readable, writable, exceptional = select.select(inputs, [], [], 5)
        
        for s in readable:       
            # new client connect
            if s is serverSocket:
                (connectionSocket, clientAddress) = serverSocket.accept()
                                
                # [(Ip, Port), index, nickname]
                clientInfo = [connectionSocket.getpeername(), 0, '']    
                clientInfos.append(clientInfo)
                inputs.append(connectionSocket)      
                        
            # receive data
            else:
                data = s.recv(2048)
#                resTimer = threading.Timer(10, responseTimer)
                
                recvClientAddr = s.getpeername()   
                
                ''' get client information who sended data'''
                for i, clientInfo in enumerate(clientInfos):
                    if clientInfo[0] == recvClientAddr:
                        senderClient = clientInfo
                                        
                
                # if server received data
                if data:                    
                    recvData = eval(data.decode())
                    
                    if recvData[0] == 1:
                        ''' if the data is nickname '''
                        nickname = recvData[1]     
                        clientIndex = clientIndex + 1
                        registerNickname(nickname)
                            
                    elif recvData[0] == 2:
                        ''' if the data is response of play '''
                        responsePlay = recvData[1]
                        
                        ''' cancel resTimer '''
                        if timerCheck2 == 1:
                            resTimer.cancel()
                            timerCheck2 = 0
                        
                        if len(gamePlayer) == 0:
                            sendToSender(0, "The opponent is disconnected") 
                        else:     
                            if responsePlay == 'y':
                                gamePlayer.append(senderClient[2])
                                gameTurn = 0
                                                            
                                gameStart = "game Started. " + str(gamePlayer[0]) + " plays first"
                                
                                sendList = (board, ROW, COL, gameStart)
                                sendToSender(3, sendList)
                                sendToAll(3, sendList)
                                
                                ''' timer start '''
                                if gameState == 1:                    
                                    timer = threading.Timer(10, setTimer)
                                    timer.start()
                                    timerCheck= 1
                                
                            else:
                                sendToOne(0, str(senderClient[2]) + " refused the game", gamePlayer[0])  
                                (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                        
                                    
                    else:      
                        ''' if the data is just message '''
                        message = recvData[1]                        
                
                        # Command '\quit'
                        if message == '\quit':                  
                            sendToSender(1, "bye~")     
                            
                            if senderClient[2] == responseClient or senderClient[2] == requestClient:
                                if timerCheck2 == 1:
                                    resTimer.cancel()
                                    timerCheck2 = 0
                                
                                (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                            
                            if senderClient[2] in gamePlayer and gameState == 1:
                                if timerCheck == 1:
                                    timer.cancel()
                                    timerCheck = 0
                            
                                sendToAll(0, str(senderClient[2]) + " has left the chat room. Game is over")
                                (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                            removeSocket(s, senderClient)
                            
                        # Command '\list'
                        elif message == '\list':
                            listMsg = "\n"
                            for i, clientInfo in enumerate(clientInfos):
                                if i != 0:
                                    listMsg = listMsg + str(i) + ". < " + str(clientInfo[2]) + ", " + str(clientInfo[0]) + " >\n"
                            
                            sendToSender(0, listMsg)
                            
                        # Command '\w <nickname> <msg>'
                        elif message.startswith('\w ') is True:
                            partitionMessage = message[3:].partition(' ')
                            (targetNickname, space, msg) = partitionMessage
                            whisper = str(senderClient[2]) + "(w)> " + msg 
                            
                            sendToOne(0, whisper, targetNickname)
                            
                        # Command '\play <nickname>'
                        elif message.startswith('\play ') is True:
                            if gameState == 0:
                                partitionMessage = message.partition(' ')
                                (command, space, targetNickname) = partitionMessage
                                whisper = str(senderClient[2]) + " wants to play with you. agree? [y/n]: "
                                
                                if targetNickname == senderClient[2]:
                                    sendToSender(0, "It is you " + str(targetNickname))
                                elif findSocketIndex(targetNickname) != -1:
                                    gameState = 1
                                    gamePlayer.append(senderClient[2])
                                    requestClient = senderClient[2]
                                    sendToOne(2, whisper, targetNickname)
                                    
                                    ''' resTimer start ''' 
                                    if timerCheck2 == 0:
                                        resTimer = threading.Timer(10, responseTimer)
                                        resTimer.start()
                                        timerCheck2 = 1
                                        responseClient = targetNickname
                                else:
                                    sendToSender(0, "There is no user: " + str(targetNickname))
                                
                                
                            else:
                                sendToSender(0, "cannot make play request")
                            
                        # Command '\ss <x> <y>'
                        elif message.startswith('\ss ') is True:
                            if senderClient[2] in gamePlayer:
                                partitionMessage = message[4:].split(' ')
                                
                                if len(partitionMessage) != 2:
                                    sendToSender(0, "Please input correct form")
                                else:     
                                    try:
                                        # It is turn of sender
                                        if gameTurn == gamePlayer.index(senderClient[2]):
                                            ''' cancel timer '''
                                            if timerCheck == 1:
                                                timer.cancel()
                                                timerCheck = 0
                                                
                                            ''' restart timer '''
                                            if gameState == 1:                    
                                                timer = threading.Timer(10, setTimer)
                                                timer.start()
                                                timerCheck= 1                                            
                                            
                                            x, y = int(partitionMessage[0]), int(partitionMessage[1])
                                            
                                            if x < 0 or y < 0 or x >= ROW or y >= COL:
                                                time.sleep(2)
                                                sendToSender(0, "invalid move - out of bound!")
                                            elif board[x][y] != 0:
                                                time.sleep(2)
                                                sendToSender(0, "invalid move - already used!")
                                            else:
                                                if gameTurn == 0:
                                                    board[x][y] = 1
                                                else:
                                                    board[x][y] = 2
                                                                         
                                                # if game is ended
                                                gameWin = check_win(board, x, y)
                                                if gameWin != 0:                                                    
                                                    if gamePlayer.index(senderClient[2]) == 0:          
                                                        winner, loser = gamePlayer[0], gamePlayer[1]
                                                    else:
                                                        winner, loser = gamePlayer[1], gamePlayer[0]    
                                                        
                                                    sendList1 = (board, ROW, COL, "you win")
                                                    sendToSender(3, sendList1)
                                                    
                                                    sendList2 = (board, ROW, COL, "you lose")
                                                    sendToOne(3, sendList2, str(loser))
                                                    
                                                    sendList3 = (board, ROW, COL, str(winner) + " won")
                                                    sendToAllExceptTwo(3, sendList3, str(loser))
                                                    
                                                    (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                                                    
                                                # if game is not ended                                                    
                                                else:
                                                    sendList = (board, ROW, COL, "")
                                                    sendToSender(3, sendList)
                                                    sendToAll(3, sendList)
                                                    
                                                
                                                # if board is fulled
                                                gameCount += 1
                                                if gameCount == ROW*COL:
                                                    sendToSender(0, "There is no space on the board. It's a draw")
                                                    sendToAll(0, "There is no space on the board. It's a draw")
                                                    (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                                                                                                        
                                                gameTurn = (gameTurn + 1) % 2  
                                                
                                        else:
                                            sendToSender(0, "not your turn")
                                        
                                    except ValueError:
                                        sendToSender(0, "Please input number")
                                
                            else:
                                sendToSender(0, "It's not your command")                            
                            
                        # Command '\gg'
                        elif message == '\gg':                             
                            if senderClient[2] in gamePlayer:
                                if timerCheck == 1:
                                    timer.cancel()
                                    timerCheck = 0
                                    
                                if gamePlayer.index(senderClient[2]) == 0:          
                                    winner, loser = gamePlayer[1], gamePlayer[0]
                                else:
                                    winner, loser = gamePlayer[0], gamePlayer[1]
                                    
                                sendToSender(0, "you lose")    
                                sendToOne(0, str(loser) + " is surrendered. you win", str(winner))
                                sendToAllExceptTwo(0, str(loser) + " is surrendered. " + str(winner) + " won", str(winner))
                                    
                                (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                                
                            else:
                                sendToSender(0, "It's not your command")                                
                                                                                            
                        else:                         
                            sendToAll(0, str(senderClient[2]) + "> " + str(message))      
                    
                #if server didn't received data (client disconnected)
                else:           
                    if senderClient[2] == responseClient or senderClient[2] == requestClient:
                        if timerCheck2 == 1:
                            resTimer.cancel()
                            timerCheck2 = 0
                        
                        (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                    
                    if senderClient[2] in gamePlayer and gameState == 1:
                        if timerCheck == 1:
                            timer.cancel()
                            timerCheck = 0
                            
                        sendToAll(0, str(senderClient[2]) + " has left the chat room. Game is over")
                        (gameState, gamePlayer, gameTurn, gameWin, gameCount, board) = initGame()
                    removeSocket(s, senderClient)
    
    # Ctrl + C exception
    except KeyboardInterrupt:
        print('\nBye bye~')
        closeSocket()                            
        
closeSocket()
