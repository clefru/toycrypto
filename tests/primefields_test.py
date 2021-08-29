from toycrypto.primefields import *
import base_test
import random
import unittest


class ZFieldTests(base_test.FieldTests):

  def setUp(self):
    raise unittest.SkipTest("superclass")

  def test_plus(self):
    for i in [random.randrange(0, 100) for x in range(0, 5)]:
      for j in [random.randrange(0, 100) for x in range(0, 5)]:
        self.assertEqual(
            self.field.plus(self.field.make(i), self.field.make(j)),
            self.field.make(i + j))

  def test_generate_all_elements(self):
    if (self.field.order > 1000):
      raise unittest.SkipTest("order to large to enumerate all elements")
    all_elements = [
        int(self.generator.scalarMul(i)) for i in range(0, self.field.order)
    ]
    self.assertEqual(sorted(all_elements), list(range(0, self.field.order)))

  def xtestGFZ(self):
    z = Z(2)
    rp = L2POL([1, 1, 0, 1, 1, 0, 0, 0, 1], z)
    field = GFPOF(z, rp)
    self.scalarMulTest(field, field.mulID())
    self.inversePlus(field)
    self.inverseMul(field)

  def xtestPOFZ13(self):
    field = POF(Z(13))
    self.scalarMulTest(field, field.mulID())


class Z17FieldTests(ZFieldTests):

  def setUp(self):
    self.field = Z(17)
    self.generator = self.field.make(5)


class Z311FieldTests(ZFieldTests):

  def setUp(self):
    self.field = Z(311)
    self.generator = self.field.make(20)


if __name__ == '__main__':
  unittest.main()
