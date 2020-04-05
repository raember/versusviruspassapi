from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey


def create_pub_priv_key_key_pair(key_size: int = 1024, randfunc=None) -> RsaKey:
    return RSA.generate(key_size, randfunc)
