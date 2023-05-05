# The no-setup script, settings are in variables

# SETTINGS ARE HERE #

LocalPort = 5454 # The port the proxy will listen to on the local machine
ListenType = "0" # Where the proxy socket should bind. local for localhost, 0 for 0.0.0.0, or an IP
RemoteHost = "example.com" # The remote host to proxy to. This can also be an IP
RemotePort = 80 # The port that you want to proxy on the remote host

# SETTINGS END HERE #

import socket
from threading import Thread
from re import match
from time import sleep
from math import floor

BufferSize = 4096 # Use a value divisible by 1024, ex. 1024, 2048, 4096
# Depending on the amount of data being sent, you might want to increase/decrease the buffer size.
# If you don't know what this means, keeping the default is fine.

IPRegex = "^([0-9]{1,3}\.){3}[0-9]{1,3}$"
# Regular Expression to detect IP addresses

DomainRegex = "^([a-zA-Z0-9\-\.]*)\.([a-zA-Z0-9]*)$"
# Regular Expression to detect domains

debugMode = False # print when the server and proxy communicate (will spam the console)

def dbPrint(val):
	if debugMode:
		print(val)

def InputSanityCheck(inputPort): # should've been named InputPortSanityCheck
	try:
		inputPort = int(inputPort)
	except:
		print("Not a valid port, please input a number 1-65535")
	else:
		if inputPort >= 1 and inputPort <= 65535:
			return inputPort
		else:
			print("Not a valid port, please input a number 1-65535")

port = InputSanityCheck(LocalPort)

if ListenType == "local":
	laddr = "localhost"
elif ListenType == "0":
	laddr = "0.0.0.0"
elif match(IPRegex,ListenType):
	laddr = addr
else:
	print("Input local, 0, or an IP address to listen on")
	exit(0)

addr2 = RemoteHost
if addr2 == "local":
	addr2 = "localhost"
elif match(DomainRegex,addr2):
	print("WARNING: detected a domain, attempting to proxy to {0}".format(addr2))
else:
	print("Not a valid input. Input an IP address or a domain without a protocol (domain.name)")
	exit(0)

rport = InputSanityCheck(RemotePort)

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((laddr,port))
sock.listen(100)

print("\n\nListening on {0}:{1}\nProxying to {2}:{3}".format(laddr,port,addr2,rport))

def SockRecv(proxyCon,serverSock):
	while True:
		if serverSock == None or proxyCon == None:
			dbPrint("(killing thread)")
			break
		serverRecvData = None
		try:
			serverRecvData = serverSock.recv(BufferSize)
		except:
			dbPrint("Killing thread, server recieve error")
			break
		if not serverRecvData:
			dbPrint("(killing thread)")
			break
		try:
			proxyCon.sendall(serverRecvData)
			dbPrint("SERVER -> PROXY: {0}".format(len(serverRecvData)))
		except:
			dbPrint("Killing thread, proxy send error")
			break

def SockSend(proxyCon,serverSock):
	while True: # The proxy send/recieve task
		proxyRecvData = proxyCon.recv(BufferSize) # Recieve data from local connector
		if not proxyRecvData: # If the server sent back no data, it means a terminated connection
			dbPrint("Server sent null packet, terminating connection")
			proxyCon.close() # close the connection
			del serverSock # delete old server socket
			break
		dbPrint("PROXY -> SERVER: {0}".format(len(proxyRecvData))) # debug
		serverSock.sendall(proxyRecvData) # Send the server all the data we recieved from the client

while True:
	proxyCon,addr = sock.accept() # Accept the connection from the proxy's socket
	
	serverSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # Make a new socket for the proxy to talk to the server with
	serverSock.connect((addr2,rport)) # Connect to the server
	
	Thread(target = SockRecv, args = (proxyCon, serverSock)).start() # Start the server recieve thread
	Thread(target = SockSend, args = (proxyCon, serverSock)).start() # Start the server send thread