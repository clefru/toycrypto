from ec import *
import unittest
import primefields

Z = primefields.Z

class ECTests(unittest.TestCase):
  def testEC(self):
    p = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1
    z = Z(p)
    secp256k1 = EC(z, z.make(0), z.make(7))
    x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    g = secp256k1.fromX(z.make(x))
    self.assertEqual(g.y, z.make(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8))

    # Known good values, checked via sage script.
    g2 = secp256k1.plus(g, g)
    self.assertEqual(g2.x, z.make(0xc6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5))
    self.assertEqual(g2.y, z.make(0x1ae168fea63dc339a3c58419466ceaeef7f632653266d0e1236431a950cfe52a))
    g3 = secp256k1.plus(g2, g)
    self.assertEqual(g3.x, z.make(0xf9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f9))
    self.assertEqual(g3.y, z.make(0x388f7b0f632de8140fe337e62a37f3566500a99934c2231b6cb9fd7584b8e672))


class ECSubfieldTests(unittest.TestCase):
  def testECSubField(self):
    p = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1
    z = Z(p)
    secp256k1 = EC(z, z.make(0), z.make(7))
    x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    g = secp256k1.fromX(z.make(x))
    ecsf = ECSubfield(secp256k1, g, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
    print ecsf.make(404)

if __name__ == '__main__':
  unittest.main()
    
