from Crypto.PublicKey import RSA
import socket
import threading
import Cryptor
import time
import cfgloader
import hashlib
import os
global pubkey, TargetID
pubkey=""

#RSA public key Rx
class key_exchange(threading.Thread):
    
    def __init__(self): 
        threading.Thread.__init__(self)
        
    def run(self):
        global pubkey
        print("Waiting for key.")
        pubkey=s.recv(1024).decode()
        print("RSA public key received.")

#msg Rx.
class Rx(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self)
        
    def run(self):
        while 1:
            i=s.recv(1024)
            print ()
            print ("-"*75)
            print ("Message From %s:"%TargetID)
            print (prorecv(i).decode())
            print ()
            print ("-"*75)
            print ("Input msg:")
                       
#msg Tx.
class Tx(threading.Thread):                                                 
    def __init__(self): 
        threading.Thread.__init__(self)
    def run(self):
        
        while 1:
            i=presend()
            s.send(i)

def pubkey_Exchange():
    time.sleep(3)
    print ("RSA public key send.")
    s.send(open("public.pem").read().encode())
    Rxonce.join()
    f = open('public_Rx.pem','w')
    f.write(pubkey)
    f.close()

def show_me_the_key():
    global pubkey
    print ("-"*75)
    print ("Your RSA public key:")
    print ()
    print (open("public.pem").read())
    print ()
    print ("-"*75)
    print ("Recieved RSA public key:")
    print ()
    print (pubkey)
    print ()
    print ("-"*75)
    os.system("pause")
    print ("Verify public key through any other channel")
    os.system("pause")
    print ("Pls make sure there's no MITM attack.")
    os.system("pause")
    print ("If something wrong. Shutdown your computer and...")
    os.system("pause")
    print ("RUN!!!!!!!")       
    os.system("pause")
    
def presend():
    raw_data=input("Input msg:").encode()
    if raw_data:
        AESkey=Cryptor.AES_keygen()
        publicRx=RSA.import_key(open("public_Rx.pem").read())
        cipherkey=Cryptor.OAEP_ecpt(AESkey,publicRx)
        ciphertext,nonce=Cryptor.AES_ecpt(raw_data, AESkey)
        #256+16+N
        ps=cipherkey+nonce+ciphertext
        return (ps)
    else:
        None

def prorecv(data):
    cipherkey=data[:256]
    data=data[256:]
    nonce=data[:16]
    ciphertext=data[16:]
    AESkey=Cryptor.OAEP_dcpt(cipherkey)
    pr=Cryptor.AES_dcpt(ciphertext, AESkey, nonce)
    return pr

    
if __name__ == "__main__":
    #Initializing.
    Recv  = Rx()
    Trans = Tx()
    Rxonce = key_exchange()
    
    #Read config.
    CFG=cfgloader.loadcfg()
    local_addr=(CFG["Local_IP"],CFG["Local_Port"])
    server_addr=(CFG["Target_IP"],CFG["Target_Port"])
    UserID=CFG["UserID"]
    TargetID=CFG["TargetID"]
    #生成RSA pair.
    Cryptor.RSA_keygen()

    #connect to server
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(local_addr) 
    s.connect(server_addr)
    
    #send ID
    s.send(UserID.encode())
    print (s.recv(1024))
    s.send(TargetID.encode())
    print (s.recv(1024))
    print ("-"*75)
    
    # holding 
    while 1:
        holding=s.recv(1024)
        print (holding)
        if holding == b"In coming":
            break
    print (s.recv(1024))
    print ("-"*75)

    #RSA public key exchange.
    Rxonce.start()
    pubkey_Exchange()
    show_me_the_key()
    print ("-"*75)
    
    #Start 
    if pubkey:
        Recv.start()
        Trans.start()
        
    else:
        print ("RSA public key not recieved.")
    
