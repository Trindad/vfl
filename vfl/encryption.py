# from applications.server_app.app.app import main
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from pathlib import Path
import numpy as np
import tempfile
import base64

from torch import Tensor


def generate_keys():
    return "", ""

def encrypt(info):
    return info

def decrypt(info):
    return info

def send(destination, *args):
    return


class HomomorphicEncryption():
    def __init__(self, client=False):
        self.client = client

        self.HE = Pyfhel()
        self.HE.contextGen(p=65537, flagBatching=True)

        if client:
            self.restore_public_key()
        else:
            self.HE.keyGen()
            Path("./encryption").mkdir(parents=True, exist_ok=True)
            self.HE.savepublicKey("./encryption/pub.key")
        
    
    def has_public_key(self):
        return not self.HE.is_publicKey_empty()

    def restore_public_key(self):
        self.HE.restorepublicKey("./encryption/pub.key")

    def encrypt_tensor(self, tensor):
        assert self.has_public_key(), "Must have a public key to encrypt"

        encrypt_vec = np.vectorize(self.HE.encryptFrac)
        return encrypt_vec(tensor.detach().cpu().numpy())

    def decrypt_tensor(self, tensor):
        assert not self.client, "Clients are not able to decrypt"

        decrypt_vec = np.vectorize(self.HE.decryptFrac)
        return Tensor(decrypt_vec(tensor))

    
    def encode_frac(self, tensor):
        temp_file = tempfile.NamedTemporaryFile()
        # tensor.to_file(temp_file.name)
        with open(temp_file.name, mode="w+b") as f:
            tensor.save(temp_file.name)
            bc = f.read()
            b64 = str(base64.b64encode(bc))[2:-1]
            return b64
        # return tensor.to_bytes()

    def encode(self, tensor):
        print("Encoding message")
        encode_vec =  np.vectorize(self.encode_frac)
        res = encode_vec(tensor)
        print("Message encoded")
        return res
        # return tensor
        # return [self.encode_frac(t) for t in tensor]

    def decode_frac(self, b64):
        temp_file = tempfile.NamedTemporaryFile()
        with open(temp_file.name, mode='w+b') as f:
            x = bytes(b64, encoding='utf-8')
            x = base64.decodebytes(x)
            f.write(x)
            c = self.HE.encryptFrac(0)
            c.load(temp_file.name, "float")
            return c

        c = self.HE.encryptFrac(0)
        c.load(temp_file.name, "float")
        return c
        # val = PyCtxt(pyfhel=self.HE)
        # val.from_bytes(bytes(tensor), float)
        # return val

    def decode(self, tensor):
        print("Decoding message")
        decode_vec = np.vectorize(self.decode_frac)
        res = decode_vec(tensor)
        print("Message decoded")
        return res
        # return tensor
        # return [self.decode_frac(t) for t in tensor]




if __name__ == "__main__":
    h1 = HomomorphicEncryption()

    h2 = HomomorphicEncryption(client=True)
    print("has_public_key:", h2.has_public_key())

    h2.restore_public_key()
    print("has_public_key:", h2.has_public_key())

    tensor = np.array([1, 2, 1.5, 2.5])
    encrypted_tensor = h2.encrypt_tensor(tensor)

    encrypted_tensor_sum = [encrypted_tensor.mean()]

    decrypted_tensor_sum = h1.decrypt_tensor(encrypted_tensor_sum)
    
    print(decrypted_tensor_sum)



    # HE = Pyfhel()
    # HE.contextGen(p=65537, flagBatching=True) 
    # HE.keyGen()

    # # HE.saveContext("./encryption/context")
    # HE.savepublicKey("./encryption/pub.key")
    # # HE.savesecretKey("./encryption/sec.key")
    # # HE.saverelinKey("./encryption/relin.key")
    # # HE.saverotateKey("./encryption/rotate.key")

    # print("3. Restore all keys")
    # HE2 = Pyfhel()
    # HE2.contextGen(p=65537, flagBatching=True)
    # HE2.restorepublicKey("./encryption/pub.key")

    # print(HE)
    # print(HE2)
    # print()

    # integer1 = 127.1
    # integer2 = -2.1
    # ctxt1 = HE2.encryptFrac(integer1) # Encryption makes use of the public key
    # ctxt2 = HE2.encryptFrac(integer2) # For integers, encryptInt function is used.
    # print("3. Integer Encryption")
    # print("    int ", integer1, '-> ctxt1 ', type(ctxt1))
    # print("    int ", integer2, '-> ctxt2 ', type(ctxt2))
    # print()

    # ctxtSum = ctxt1 + ctxt2         # `ctxt1 += ctxt2` for quicker inplace operation
    # ctxtSub = ctxt1 - ctxt2         # `ctxt1 -= ctxt2` for quicker inplace operation
    # ctxtMul = ctxt1 * ctxt2         # `ctxt1 *= ctxt2` for quicker inplace operation

    # print("4. Operating with encrypted integers")
    # # print(f"Sum: {ctxtSum}") # this generates an error because it expects to have a private key for some reason
    # # print(f"Sub: {ctxtSub}")
    # # print(f"Mult:{ctxtMul}")
    # print()


    # resSum = HE.decryptFrac(ctxtSum) # Decryption must use the corresponding function decryptFrac.
    # resSub = HE.decryptFrac(ctxtSub)
    # resMul = HE.decryptFrac(ctxtMul)
    # print("#. Decrypting result:")
    # print("     addition:       decrypt(ctxt1 + ctxt2) =  ", resSum)
    # print("     substraction:   decrypt(ctxt1 - ctxt2) =  ", resSub)
    # print("     multiplication: decrypt(ctxt1 * ctxt2) =  ", resMul)