import collections
import random

from ec import *
from primefields import *

p = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1
z = Z(p)
secp256k1 = EC(z, z.make(0), z.make(7))


class Signature(collections.namedtuple("Signature", ["s", "K"])):
    """Schnorr signatures over secp256k1."""
    H = secp256k1.fromX(z.make(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798))
    Hfield = ECSubfield(secp256k1, H, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
    nF = Z(Hfield.order)

    @classmethod
    def sign(cls, e, x):
        k = cls.gen_private_key()
        s = cls.nF.plus(k, cls.nF.mul(x, cls.nF.make(e)))
        return Signature(s, cls.Hfield.make(int(k)).point)

    @classmethod
    def merge(cls, s1, s2):
        return Signature(cls.nF.plus(s1.s, s2.s), secp256k1.plus(s1.K, s2.K))

    def verify(self, pubKey, e):
        S = Signature.Hfield.make(int(self.s)).point
        V = Signature.Hfield.ec.plus(self.K, pubKey.scalarMul(e))
        return S == V

    @classmethod
    def gen_private_key(cls):
        return cls.nF.make(random.randrange(1, Signature.Hfield.order))

    @classmethod
    def make_pub_key(cls, private_key):
      return Signature.Hfield.make(int(private_key)).point
