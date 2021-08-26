from asymmetric import *
import unittest

# Deterministic tests for the moment
seed = 70
random.seed(seed)

class SignatureTests(unittest.TestCase):
  def test_generate_private_key(self):
    # Generate a bunch of private keys
    for i in range(0,100):
      Signature.gen_private_key()

  def test_sign_and_verify(self):
    # Pick a random scalar to sign
    e = 44099

    priv_key = Signature.gen_private_key()
    sig = Signature.sign(e, priv_key)
    pub_key = Signature.make_pub_key(priv_key)
    self.assertTrue(sig.verify(pub_key, e))

    wrong_e = e - 1 
    self.assertFalse(sig.verify(pub_key, wrong_e))
    
    wrong_pub_key = Signature.make_pub_key(Signature.gen_private_key())
    self.assertFalse(sig.verify(wrong_pub_key, e))

    priv_key2 = Signature.gen_private_key()
    sig2 = Signature.sign(e, priv_key)
    pub_key2 = Signature.make_pub_key(priv_key)
    self.assertTrue(sig.verify(pub_key, e))

    sig_merged = Signature.merge(sig, sig2)
    # FIXME, don't call secp256k1 directly but abstract clearly.
    pub_key_merged = secp256k1.plus(pub_key.plus(pub_key2))
    self.assertTrue(sig_merged.verify(pub_key_merged, e))
    
  
if __name__ == '__main__':
    unittest.main()
