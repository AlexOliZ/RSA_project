import sys
from socket import socket, AF_INET, SOCK_DGRAM

ip = "192.168.1.1"
PORT_NUMBER = 8080
SIZE = 1024

def main():
	listensocket = socket(AF_INET, SOCK_DGRAM)
	listensocket.bind((ip,PORT_NUMBER))
	while(1):
		(data,addr) = listensocket.recvfrom(SIZE)
		print(data,addr)


if __name__ == "__main__":
    main()
