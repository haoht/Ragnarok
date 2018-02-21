import random
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


#Output RSA pair to file
def RSA_keygen():
    new_key = RSA.generate(2048)
    public_key = new_key.publickey().exportKey("PEM") 
    private_key = new_key.exportKey("PEM") 
    f = open('public.pem','w')
    f.write(public_key.decode())
    f.close()
    f = open('private.pem','w')
    f.write(private_key.decode())
    f.close()

#AES key
def AES_keygen():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
    sa = []
    for i in range(16):
        sa.append(random.choice(seed))
         
    AES_key = ''.join(sa)
    return AES_key.encode()

#AES encrypt.
def AES_ecpt(rawdata, key): 
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(rawdata)
    return ciphertext, nonce

#AES decrypt.
def AES_dcpt(ciphertext, key, nonce):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

#Encrypt AES key with RSA public key.
def OAEP_ecpt(AESkey,publicRx):
    cipher = PKCS1_OAEP.new(publicRx)
    cipherkey = cipher.encrypt(AESkey)
    return cipherkey

#Decrypy AES key with RSA private key.
def OAEP_dcpt(cipherkey):
    privatekey = RSA.importKey(open('private.pem').read())
    cipher = PKCS1_OAEP.new(privatekey)
    AESkey = cipher.decrypt(cipherkey)
    return AESkey

#Just for test...
if __name__ == "__main__":
    AESkey=AES_keygen()
    print (AESkey)
    #rdata=input("Input data:")
    rdata="sssssssssssssssssssssss"
    rdata=rdata.encode()
    ciphertext,nonce=AES_ecpt(rdata, AESkey)
    #print (ciphertext)
    #print (nonce)
    #print(RSA_keygen())
    publicRx= RSA.import_key(open("public.pem").read())
    cipherkey=OAEP_ecpt(AESkey,publicRx)
    #print(cipherkey)
    print(len(ciphertext))
    ps=cipherkey+nonce+ciphertext
    #print (OAEP_dcpt(cipherkey))
