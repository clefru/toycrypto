import hashlib
import binascii


class Base(object):

  def __repr__(self):
    raise NotImplementedError

  def __hash__(self):
    return int(binascii.hexlify(hashlib.sha256(str(self)).digest()), 16)

  def __eq__(self, other):
    raise NotImplementedError


class Group(Base):

  def plusID(self):
    raise NotImplementedError

  def plus(self, a, b):
    raise NotImplementedError

  def mulID(self):
    raise NotImplementedError

  def mul(self, a, b):
    raise NotImplementedError

  def longDiv(self, a, b):
    raise NotImplementedError

  class Element(Base):

    def __init__(self, field):
      self.field = field

    def isPlusID(self):
      return self == self.field.plusID()

    def opN(self, n, neutral, op):
      """Applies op(self, op(self, ... op(self, neutral))) n-times"""

      # Assuming a binary operator "op", we create the operator lambda a: op1(self, a). Then we apply
      # op1 to neutral n-times as given by the scalar.
      #
      # The implementation here uses the double-and-add algorithm to optimize this to log_n steps.

      if n < 0:
        raise ValueError("Scalar %d can't be negative" % n)
      f = self.field
      res = neutral
      # This variable will double every step and whenever we hit a "true"-bit add itself to res.
      w = self
      while n:
        if n % 2:
          res = op(res, w)
        w = op(w, w)
        n = n // 2
      return res

    def scalarMul(self, scalar):
      """Scalar multiplication"""
      return self.opN(scalar, self.field.plusID(), self.field.plus)

    def __eq__(self, other):
      raise NotImplementedError


class Field(Group):

  def mulID(self):
    raise NotImplementedError

  def mul(self, a, b):
    raise NotImplementedError

  def longDiv(self, a, b):
    raise NotImplementedError

  class Element(Group.Element):

    def __init__(self, field):
      self.field = field

    def isMulID(self):
      return self == self.field.mulID()

    def scalarPow(self, scalar):
      """Scalar power"""
      return self.opN(scalar, self.field.mulID(), self.field.mul)
