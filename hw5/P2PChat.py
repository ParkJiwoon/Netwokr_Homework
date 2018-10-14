#
# P2PChat.py
# 20131902 Park Ji Woon
#

import socket
import select
import sys
import signal
import threading

targetPort = [21902, 31902, 41902, 51902]
timer = []

def setNode():
    # Set port number and nickname
    global serverName, serverPort, nickname
    if len(sys.argv) == 3:
        if sys.argv[2].find("\\") == -1:
            if sys.argv[1] == '1':
                serverPort = 21902
            elif sys.argv[1] == '2':
                serverPort = 31902
            elif sys.argv[1] == '3':
                serverPort = 41902
            elif sys.argv[1] == '4':
                serverPort = 51902
            else:
                print('Input port number range 1~4')
                sys.exit()
                
            nickname = sys.argv[2]
            serverName = '165.194.35.202'
            
        else:
            print("Input correct nickname: do not use '\\' in the nickname")
            sys.exit()
        
    else:
        print('Input correct argv: python P2PChat.py <NodeID> <Nickname>')
        sys.exit()
        
        
class Node:
    ip = None
    port = None
    nodeid = None
    nickname = None
    adddr = None
    outgoingPeers = []
    incomingPeers = []
    totalPeers = []
    seqno = 0
    cacheList = [] # cachelist = [[ip, seqno], [ip, seqno], ... , [ip, seqno]]
    
    def __init__(self, ip, port, nickname, nodeid):
        self.ip = ip
        self.port = port
        self.nickname = nickname
        self.addr = (ip, port)
        self.nodeid = nodeid
    
    def setIncomingPeer(self, addr, nodeid):
        peer = [addr, nodeid]
        self.incomingPeers.append(peer)
        self.totalPeers.append(peer)
        
    def setOutgoingPeer(self, addr, nodeid):
        peer = [addr, nodeid]
        self.outgoingPeers.append(peer)
        self.totalPeers.append(peer)
    
    def removeIncomingPeer(self, addr, nodeid):
        peer = [addr, nodeid]
        self.incomingPeers.remove(peer)
        self.totalPeers.remove(peer)
        
    def removeOutgoingPeer(self, addr, nodeid):
        peer = [addr, nodeid]
        self.outgoingPeers.remove(peer)
        self.totalPeers.remove(peer)
        
    def addSeqNo(self):
        self.seqno = self.seqno + 1        
        
    def removeCache(self, addr):
        for cache in self.cacheList:
            if addr in cache:
                self.cacheList.remove(cache)
                return                
        
    def cacheHandler(self, msgType, addr, seqno):
        for cache in self.cacheList:            
            if addr in cache:
                if seqno <= cache[1]:      
                    ''' receive it already -> discard '''     
                    return False
                else:         
                    ''' receive new chat message already src '''
                    cache[1] = cache[1] + 1 
                    return True            
            
        ''' new chat message and new src'''
        if msgType != 4:            
            self.cacheList.append([addr,seqno])
            return True
        
        return False

def handler(signum, frame):
    exitNode(p2pSocket)
    
def makeSendList(msgType, data):
    sendData = []
    sendData.append(msgType)
    sendData.append(data)
    sendData.append(myNode.addr)
    sendData.append(myNode.seqno)
    sendData.append(myNode.nodeid)
    
    return str(sendData).encode()    

def exitNode(socket):
    message = myNode.nickname + " connection closed"
    quitMsg = makeSendList(4, message)
    
    for time in timer:
        time[0].cancel()
                    
    for peer in myNode.totalPeers:
        socket.sendto(quitMsg, peer[0])
        
    print('\nBye bye~')
    socket.close()
    sys.exit()
    
def connectionFail(addr):
    print("Time Out! connection FAIL to " + str(addr))
    

def requestConnection(socket):
    global timer
    i = 0
    message = "connection REQUEST"
    for port in targetPort:               
        if port != myNode.port:
            ''' send request '''
            targetAddr = (myNode.ip, port)
            requestMsg = makeSendList(1, message)
            socket.sendto(requestMsg, targetAddr)  
            
            timer.append([threading.Timer(5, connectionFail, args=[targetAddr]), targetAddr])
            timer[i][0].start()
            i = i+1
    
            
    
def deleteDuplicatePeer(addr, nodeid):
    ''' less nodeid will be server '''
    for peer in myNode.totalPeers:
        if peer in myNode.incomingPeers and peer in myNode.outgoingPeers:
            if myNode.nodeid < peer[1]:
                myNode.removeOutgoingPeer(addr, nodeid)
            else:
                myNode.removeIncomingPeer(addr, nodeid)
                
            return
                
    
             
# Ctrl+C exception handling
signal.signal(signal.SIGINT, handler)


''' main start '''
setNode()
chatingStatus = 0
myNode = Node(serverName, serverPort, nickname, int(sys.argv[1]))

p2pSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
p2pSocket.bind(('', myNode.port))

print("\nThe server is ready to receive on port", myNode.port)
print("")
requestConnection(p2pSocket)

while True:        
    try:     
        # inputs : socket list
        inputs = [sys.stdin, p2pSocket]  
        readable, writable, exceptional = select.select(inputs, [], [], 5)
        
        for s in readable:
            if s is p2pSocket:
                ''' you receive data '''
                data, senderAddress = s.recvfrom(2048)  
                recvList = eval(data.decode())
                [recvMessageType, recvMessage, srcAddr, srcSeqNo, srcNodeId] = recvList
                
                if recvMessageType == 1:
                    ''' data is connection REQUEST message '''                    
                    if len(myNode.incomingPeers) < 2 and len(myNode.totalPeers) < 3:
                        message = "Respond connection ACK from " + str(myNode.addr)
                        respondMsg = makeSendList(2, message)
                        myNode.setIncomingPeer(srcAddr, srcNodeId)
                    else:
                        message = "Respond connection FAIL from " + str(myNode.addr)
                        respondMsg = makeSendList(3, message)
                        
                    p2pSocket.sendto(respondMsg, senderAddress)
                    
                elif recvMessageType == 2:
                    ''' data is connection ACK message '''
                    for time in timer:
                        if time[1] == srcAddr:
                            time[0].cancel()
                            
                    print(recvMessage)
                    if len(myNode.outgoingPeers) < 2 and len(myNode.totalPeers) < 3:
                        myNode.setOutgoingPeer(srcAddr, srcNodeId)
                        deleteDuplicatePeer(srcAddr, srcNodeId)
                        
                        if chatingStatus == 0:
                            message = myNode.nickname + " enter the chat room"       
                            sendMsg = makeSendList(0, message)
                            myNode.addSeqNo()
                            
                            for peer in myNode.totalPeers:
                                p2pSocket.sendto(sendMsg, peer[0])
                                
                            chatingStatus = 1
                    
                elif recvMessageType == 3:
                    ''' data is connection FAIL message '''    
                    for time in timer:
                        if time[1] == srcAddr:
                            time[0].cancel()
                            
                    print(recvMessage)
                    
                else:                    
                    ''' data is chat message '''
                    ''' check duplicate message and send to connected nodes '''
                    checkCache = myNode.cacheHandler(recvMessageType, srcAddr, srcSeqNo)                    
                    
                    if checkCache is True:
                        print(recvMessage)
                        
                        for peer in myNode.totalPeers:
                            if peer[0] != senderAddress and peer[0] != srcAddr:
                                p2pSocket.sendto(data, peer[0])
                                
                    if recvMessageType == 4:
                        ''' data is quit connection message '''
                        if [srcAddr, srcNodeId] in myNode.incomingPeers:
                            myNode.removeIncomingPeer(srcAddr, srcNodeId)
                        elif [srcAddr, srcNodeId] in myNode.outgoingPeers:
                            myNode.removeOutgoingPeer(srcAddr, srcNodeId)
                            
                        myNode.removeCache(srcAddr)
                        
                        if len(myNode.totalPeers) == 0:
                            timer[:] = []
                            requestConnection(s)
                                
            else:           
                ''' you can send message when you chat '''       
                inputMessage = input()          
                
                # input \quit
                if inputMessage == '\quit':
                    exitNode(p2pSocket)
                    
                #input \connection
                elif inputMessage == '\connection':
                    print("")
                    for index, peer in enumerate(myNode.totalPeers):
                        print(str(index+1) + "." + str(peer[0]))
                    print("")
                    
                else:                     
                    message = myNode.nickname + "> " + inputMessage       
                    sendMsg = makeSendList(0, message)
                    myNode.addSeqNo()
                    
                    for peer in myNode.totalPeers:
                        p2pSocket.sendto(sendMsg, peer[0])
                    
            
    # Ctrl + C exception
    except KeyboardInterrupt:
        exitNode(p2pSocket)

p2pSocket.close()
