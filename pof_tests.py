from pof import *
import primefields
import base_tests
import unittest

Z2 = primefields.Z(2)
Z5 = primefields.Z(5)
Z17 = primefields.Z(17)


class POFTests(base_tests.GroupTests):

  def setUp(self):
    self.field = POF(Z17)
    self.generator = self.field.make(5)

  def xtestGFZ(self):
    z = Z(2)
    rp = L2POL([1, 1, 0, 1, 1, 0, 0, 0, 1], z)
    field = GFPOF(z, rp)
    self.scalarMulTest(field, field.mulID())
    self.inversePlus(field)
    self.inverseMul(field)


class POFTest(unittest.TestCase):

  def testPOFInterface(self):
    POFZ5 = POF(Z5)
    a = POFZ5.plusID()
    # Make sure we get a polynomial with zeros in a few randomly
    # selected coefficients (selected via unfair dice role)
    self.assertEqual(a.getCoefficient(5), Z5.plusID())
    self.assertEqual(a.getCoefficient(2), Z5.plusID())
    self.assertEqual(a.getCoefficient(10), Z5.plusID())

    # x^13 + x^8 + x^5
    a.setCoefficient(5, Z5.mulID())
    a.setCoefficient(8, Z5.mulID())
    a.setCoefficient(13, Z5.mulID())
    # Assert correct coefficients.

    self.assertEqual(a.getCoefficient(5), Z5.mulID())
    self.assertEqual(a.getCoefficient(8), Z5.mulID())
    self.assertEqual(a.getCoefficient(12), Z5.plusID())
    self.assertEqual(a.getCoefficient(13), Z5.mulID())
    self.assertEqual(a.getCoefficient(14), Z5.plusID())
    self.assertEqual(a.getDegree(), 13)

    # Make it 0 * x^13 and observe degree shrinking.
    a.setCoefficient(13, Z5.plusID())
    self.assertEqual(a.getDegree(), 8)

  def testScalar(self):
    POFZ5 = POF(Z5)
    a = POFZ5.plusID().setCoefficient(1, primefields.Z.Element(1, Z5))
    x = a.scalarPow(4)
    self.assertEqual(
        x,
        POFZ5.plusID().setCoefficient(4, primefields.Z.Element(1, Z5)))

  def testFromInt(self):
    POFZ5 = POF(Z5)
    pol = POFZ5.make(8)
    self.assertEqual(int(pol.getCoefficient(0)), 3)
    self.assertEqual(int(pol.getCoefficient(1)), 1)

    self.assertEqual(
        POF(Z2).make([1, 1, 0, 1, 1, 0, 0, 0, 1]),
        POF(Z2).make(0x11b))

  def testXtime(self):
    POFZ5 = POF(Z5)
    pol = POFZ5.mulID().xtime()
    self.assertEqual(pol.getCoefficient(1).toInt(), 1)

  def testOneReduction(self):
    POFZ5 = POF(Z5)
    # 3x^4 + 3x^2 + 1 over Z(5)
    red = POFZ5.make([Z5.make(0), Z5.make(1), Z5.make(0), Z5.make(2)])
    # divided by 2x^3 + x over Z(5)
    a = POFZ5.make([Z5.make(1), Z5.make(0), Z5.make(3), Z5.make(0), Z5.make(3)])

    q, r = POFZ5.longDiv(a, red)
    # Should be 4x with 1 + 4x as reminder.
    # Handchecked that resut. I hope :)
    self.assertEqual(q, POFZ5.make([Z5.make(0), Z5.make(4)]))
    self.assertEqual(r, POFZ5.make([Z5.make(1), Z5.make(0), Z5.make(4)]))

    # Let's multiply things together again.
    self.assertEqual(POFZ5.plus(POFZ5.mul(q, red), r), a)

  def testXtime(self):
    POFZ5 = POF(Z5)
    red = POFZ5.plusID()
    red.setCoefficient(3, Z5.make(2))
    red.setCoefficient(1, Z5.make(1))


#    GFZ5 = GFPOF(Z5, red)
#    x = GFZ5.mulID().xtime()
#print x.scalarPow(3)
#print GFZ5.mul(a, a)
#print POF(Z(2)).make(19)

if __name__ == '__main__':
  unittest.main()
