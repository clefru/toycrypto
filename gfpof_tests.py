from gfpof import *
from pof import *
import base_tests
import unittest
import primefields

Z5 = primefields.Z(5)
Z2 = primefields.Z(2)

def fromBin(a):
  """List of binary values to integer."""
  r = 0
  try:
    while True:
      r = r*2
      r = r+a.pop()
  except IndexError:
    pass
  return r/2

def L2EL(lst, field):
  """List of raw values to a list of field elements."""
  return [field.make(x) for x in lst]

def L2POL(a, field):
  """Create polynomial from raw coefficient list in field."""
  return POF(field).make(L2EL(a, field))

def EL2L(lst):
  """List of field elements to list of raw values."""
  return [x.value for x in lst]

def POL2L(pofi):
  """Polynomial to list of raw values of its coefficients."""
  return EL2L(pofi.toEL())

def toBin(a):
  """Integer to list of binary values."""
  r = []
  for i in range(0, 8):
    r.append(a%2)
    a = a/2
  return r

@unittest.skip("broken")
class GFPOF_FieldTests(base_tests.FieldTests):
  pass
  
class GFPOF_FieldTests(unittest.TestCase):    
  def testXtime(self):
    POFZ5 = POF(Z5)
    red = POFZ5.plusID()
    red.setCoefficient(3, Z5.make(2))
    red.setCoefficient(1, Z5.make(1))
    GFZ5 = GFPOF(Z5, red)
    x = GFZ5.mulID().xtime()
    #print x.scalarPow(3)
    #print GFZ5.mul(a, a)
    #print POF(Z(2)).fromInt(19)

class TmathTests(unittest.TestCase):
  def test_self_inverse(self):
    # Residue class 2 field

    # Polynomial over field Z2
    POFZ2 = POF(Z2)
    # Reduction polynomial in POFZ2 as defined by Page 36 of the Rijndael book. MAGIC
    rp = POFZ2.make([1, 1, 0, 1, 1, 0, 0, 0, 1])

    # Galois field over Z2 with reduction polynomial
    GFPOFZ2 = GFPOF(Z2, rp)

    for i in range(1, 256):
      g = GFPOFZ2.make(POFZ2.make(i).c)      
      inverse=g.mulInv()
      inverseinverse=inverse.mulInv()
      self.assertEqual(inverseinverse, g)

if __name__ == '__main__':
    unittest.main()
    
