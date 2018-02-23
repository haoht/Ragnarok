from Crypto.PublicKey import RSA
import socket
import threading
import Cryptor
import time
import cfgloader
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

#byte Rx.

def prorecv(data,AESkey):
    nonce=data[:16]
    ciphertext=data[16:]
    pr=Cryptor.AES_dcpt(ciphertext, AESkey, nonce)
    return pr
                       
#byte Tx.

def presend(raw_data,AESkey):
    if raw_data:
        publicRx=RSA.import_key(open("public_Rx.pem").read())
        ciphertext,nonce=Cryptor.AES_ecpt(raw_data, AESkey)
        #256+16+N
        ps=nonce+ciphertext
        return (ps)
    else:
        None            


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

def send_aes():
    AESkey=Cryptor.AES_keygen()
    publicRx=RSA.import_key(open("public_Rx.pem").read())
    cipherkey=Cryptor.OAEP_ecpt(AESkey,publicRx)
    s.send(cipherkey)
    return AESkey

def recv_aes():
    cipherkey=s.recv(1024)
    AESkey=Cryptor.OAEP_dcpt(cipherkey)
    return AESkey

#verify file parameter    
def send_para(filename,filesize,AESkey):
    s.send(presend(filename.encode(),AESkey))
    fb_filename=prorecv(s.recv(1024),AESkey).decode()

    s.send(presend(str(filesize).encode(),AESkey))
    fb_filezise=int(prorecv(s.recv(1024),AESkey).decode())
    return filename==fb_filename and filesize==fb_filezise 

def echo_para(AESkey):
    filename=prorecv(s.recv(1024),AESkey).decode()
    s.send(presend(filename.encode(),AESkey))

    filesize=int(prorecv(s.recv(1024),AESkey).decode())
    s.send(presend(str(filesize).encode(),AESkey))
    return filename,filesize

def readfile(filename):
    r = open(filename, 'rb')
    while True:
        tmp = r.read(blocksize-16)
        if tmp == b'':
            r.close()
            break
        cache=presend(tmp,AESkey)
        s.send(cache)

def writefile(blocksize,AESkey,Rxsum=0):
    block=b""
    while 1:
        block+=s.recv(1024)
        if len(block)==blocksize:
            data=prorecv(block,AESkey)
            Rxsum+=len(data)
            w.write(data)
            block=b""
        #16 for nonce
        elif len(block)==(filesize%(blocksize-16))+16:
            data=prorecv(block,AESkey)
            Rxsum+=len(data)
            w.write(data)
        if Rxsum==filesize:
            break      
            w.close()

if __name__ == "__main__":
    #Initializing.
    Rxonce = key_exchange()
    
    #Load config.
    CFG=cfgloader.loadcfg()
    local_addr=(CFG["Local_IP"],CFG["Local_Port"])
    server_addr=(CFG["Target_IP"],CFG["Target_Port"])
    UserID=CFG["UserID"]
    TargetID=CFG["TargetID"]
    blocksize=CFG["Blocksize"]
    #Gen. RSA pair.
    Cryptor.RSA_keygen()

    #Connect to server
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(local_addr) 
    s.connect(server_addr)
    
    #Send IDs
    s.send(UserID.encode())
    print (s.recv(1024))
    s.send(TargetID.encode())
    print (s.recv(1024))
    print ("-"*75)
    
    # Holding 
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

    ############# 
    print("Input file name, empty for receive.")
    filename=input(">>>>>")
    
    #Send file
    if filename:
        filesize=os.path.getsize(filename)
        s.send(str(blocksize).encode())
        AESkey=send_aes()

        #Send name and size
        if send_para(filename,filesize,AESkey):
            print ()
            print ("Filename and size verified...")
            print ()
            print ("Start at:",time.strftime('%H:%M:%S',time.localtime(time.time())))

            #Start file transmit
            readfile(filename)
            print ()
            print ("All send at:",time.strftime('%H:%M:%S',time.localtime(time.time())))
            s.close()
            os.system("pause")
        else:
            print ("Filename and size feedback error...")
            s.close()
            #Stop

    #Receive file
    else:
        #Echo parameter
        blocksize=int(s.recv(1024).decode())
        AESkey=recv_aes()
        print ()
        print ("AES key Recieved")
        filename,filesize=echo_para(AESkey)
        print (filename,filesize)
        print ()
        print ("Start at:",time.strftime('%H:%M:%S',time.localtime(time.time())))
        w = open (filename, "wb")
        
        writefile(blocksize,AESkey)
        print ()
        print ("All received at:",time.strftime('%H:%M:%S',time.localtime(time.time())))
        s.close()
        os.system("pause")
    
    
    
