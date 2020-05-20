import os
import sys
import time
import random
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from threading import Thread

if os.geteuid() != 0:
    exit("Error. This User is not root. Use 'Sudo'")

BLOCK_SIZE = 16
ENC_BLOCK_SIZE = 16777216  # 16 MB
B64_BLOCK_SIZE = 22369664  # 16mb

print("DenigmaDisk By Zpon\nBlock Size: "+str(BLOCK_SIZE) + " Bytes\nAES "+str(pow(BLOCK_SIZE, 2))+" Bit")



def existElem(arr, el):
    try:
        arr[el]
        return True
    except:
        return False


class DictList():

    def __init__(self, countOfBlocks, name):
        self.countOfBlocks = countOfBlocks
        self.dl = dict([[i, False] for i in range(countOfBlocks)])
        self.name = name

    def GetDL(self):
        return self.dl

    def SetDL(self, dl):
        self.dl = dl

    def WriteFile(self):
        f = open(self.name, "ab")
        print("\n", end='')
        for i in range(self.countOfBlocks):
            print("\r", end='')
            print("->", "["+str(round(int(i + 1,) / self.countOfBlocks * 100, 2)) + "%]", self.name, end=' Completed.')
            sys.stdout.flush()
            while True:
                time.sleep(0.1)
                if not self.dl[i]:
                    continue
                else:
                    f.write(self.dl[i])
                    self.dl[i] = True
                    break
        
        f.close()
        


class MainThread(Thread):
    def __init__(self, dl, countOfBlocks, password, i, data):
        Thread.__init__(self)
        self.dl = dl
        self.countOfBlocks = countOfBlocks
        self.password = password
        self.tid = i
        self.data = data


class CryptThread(MainThread):

    def ReturnCryptDL(self):
        self.dl[self.tid] = self.encrypt(self.data)
        return self.dl

    def ReturnDecryptDL(self):
        self.dl[self.tid] = self.decrypt(self.data)
        return self.dl

    def Unvar(self):
    	return
    	self.dl[self.tid] = True

    def run(self):
        pass


    def pad(self, s): return s + ((BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode("utf-8")

    def unpad(self, s): return s[:-ord(s[len(s) - 1:])]

    def encrypt(self, data):
        private_key = hashlib.sha256(password.encode("utf-8")).digest()
        data = self.pad(data)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(data))

    def decrypt(self, enc):
        private_key = hashlib.sha256(password.encode("utf-8")).digest()
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        res = cipher.decrypt(enc[16:])
        return self.unpad(res)


def main(filePath, password):  
    try:  
        fileSize = os.path.getsize(filePath)
    except FileNotFoundError:
        print("Error. File Not Found.")
        sys.exit()

    countOfCryptBlocks = (fileSize // ENC_BLOCK_SIZE) # NO CRYPT
    countOfDecryptBlocks = (fileSize // B64_BLOCK_SIZE) # CRYPT

    if fileSize % ENC_BLOCK_SIZE != 0: countOfCryptBlocks += 1
    if fileSize % B64_BLOCK_SIZE != 0: countOfDecryptBlocks += 1

    f = open(filePath, "rb")
    name, ext = os.path.splitext(filePath)

    if ext == ".dd":

        dl = DictList(countOfDecryptBlocks, filePath[:-3])
        k = Thread(target=dl.WriteFile)
        k.start()    	
        # Decrypt
        for i in range(countOfDecryptBlocks):
            data = f.read(B64_BLOCK_SIZE)
            thread = CryptThread(dl.GetDL(), countOfDecryptBlocks, password, i, data)
            thread.start()
            dl.SetDL(thread.ReturnDecryptDL())
            thread.Unvar()
    else:

        dl = DictList(countOfCryptBlocks, filePath + ".dd")
        k = Thread(target=dl.WriteFile)
        k.start()     	
        # Crypt
        for i in range(countOfCryptBlocks):
            data = f.read(ENC_BLOCK_SIZE)
            thread = CryptThread(dl.GetDL(), countOfCryptBlocks, password, i, data)
            thread.start()
            dl.SetDL(thread.ReturnCryptDL())
            thread.Unvar()

    os.remove(filePath)


def FindFiles(path, password):
    if os.path.isdir(path):
    	for i in os.listdir(path):
    		if os.path.isdir(path + os.sep + i):
    			FindFiles(path + os.sep + i, password)
    		else:
    			main(path + os.sep + i, password)
    else:
    	main(path, password)


if __name__ == '__main__':

    if len(sys.argv) == 3:
        password = sys.argv[2]
        path = sys.argv[1]
    else:
        exit("Error: Param.")

    if path[:1] in ["'", "\""]:
        path = path[1:-1]

    if password[:1] in ["'", "\""]:
        password = password[1:-1]

    FindFiles(path, password)
    print("\n\nEND.")