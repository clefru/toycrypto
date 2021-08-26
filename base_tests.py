import unittest
import random


class GroupTests(unittest.TestCase):

  def test_scalarMul(self):
    e15 = self.generator.scalarMul(15)
    e18 = self.generator.scalarMul(9).scalarMul(2)
    e3 = self.generator.scalarMul(3)
    self.assertEqual(e18, self.field.plus(e15, e3))
    # Check commutativeness.
    self.assertEqual(self.generator.scalarMul(2).scalarMul(9), e18)


class FieldTests(GroupTests):

  def test_mulInv(self):
    for i in range(40):
      e = self.field.make(i)
      # Plus ID (zeros) don't have a multiplicative inverse
      if not e.isPlusID():
        inv_e = e.mulInv()
        self.assertEqual(self.field.mul(e, inv_e), self.field.mulID())
