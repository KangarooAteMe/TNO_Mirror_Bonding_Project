'''This code is supporting the use of an client to connect an 6 axis UR robotic arm to na RPI
Authored by: Dave vermeulen (Original author)
Version: 0.1.3

Note that this code isnt flawless might take some time debugging'''

import socket as sck
import time

class Network_client:
    def __init__(self, IP, PORT):
        self.IP_Adress = IP
        self.PORT_num = PORT
        
        print(f'Socket created on IP_Addres: {self.IP_Adress} with PORT_num: {self.PORT_num}')
        
        global Server_socket
        Server_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        Server_socket.bind((self.IP_Adress, self.PORT_num))
        
    def start(self): 
        Server_socket.listen(5)
        print("Socket Listening on given Port number")
        
    def close(self): 
        print("Socket closing down!!! ")
        Server_socket.close()
    
    def connect_client(self, message, trigger):
        Client_socket, addr = Server_socket.accept()
        
        with Client_socket: 
            
            timestamp = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
            print(f"Client connection ESTABLISHED From {addr} at {timestamp}")
            
            Client_socket.send("Server is listening".encode('utf-8'))
            
            while True: 
        
                datareceive = Client_socket.recv(2048).decode('utf-8')
                print(f"Now receiving Data from {addr}")
                
                if not datareceive:
                    print(f"No Data received from: {addr}:")
                    break
                
                elif datareceive != trigger: 
                    print(f"Data received from: {addr} does not equal trigger command")    
                    break
                
                print(f"Trigger Received from: {addr}")
                Client_socket.send(message.encode('utf-8'))
            
            print(f"Socket with Address: {addr} Is CLOSING")  
            Client_socket.close()    
                    
        
        
if __name__ == '__main__':
    IP_adress = "192.168.0.3"
    PORT_num = 62513
    Message = "hi from server"
    
    NetwkCl = Network_client(IP_adress, PORT_num)
     
    NetwkCl.start()
    
    try:
        while True: 
            NetwkCl.connect_client(Message, "TRG")
    
    except KeyboardInterrupt:
        NetwkCl.close()
