from toycrypto.base import *


class Z(Field):
  """Implementation of the mathemical set Z/nZ."""

  def __init__(self, order):
    super(Z, self).__init__()
    self.order = order

  def getOrder(self):
    return self.order

  def plusID(self):
    return self.Element(0, self)

  def plus(self, a, b):
    if a.field == b.field:
      return self.Element(a.value + b.value, self)
    else:
      raise ValueError('Trying to add ZElements from different Z classes')

  def mulID(self):
    return self.Element(1, self)

  def mul(self, a, b):
    return self.Element(a.value * b.value, self)

  def __str__(self):
    return "Z(%d)" % self.order

  def __repr__(self):
    return "Z(%d)" % self.order

  def make(self, i):
    if type(i) == self.Element:
      # Copy and return new element in my field
      return self.Element(i.value, self)

    if type(i) == int or type(i) == long:
      return self.Element(i, self)

    raise ValueError("Unknown object type to make from: %s" % type(i))

  def enum(self, i):
    return (self.Element(i % self.order, self), i // self.order)

  def __eq__(self, a):
    return type(self) == type(a) and self.order == a.order

  def __hash__(self):
    return hash(self.order)

  class Element(Field.Element):

    def __init__(self, value, field):
      super(Z.Element, self).__init__(field)
      if type(value) != int:
        raise ValueError("value must be an int")
      self.value = value % field.order

    def __str__(self):
      return "%(v)d" % {'v': self.value, 's': self.field}

    def __repr__(self):
      return "%(v)x" % {'v': self.value, 's': self.field}

    def setValue(self, value):
      if type(a) != int:
        raise ValueError("setValue must take an int")
      self.value = value % self.field.order
      return self

    def plusInv(self):
      return Z.Element(self.field.order - self.value, self.field)

    def mulInv(self):
      return self.scalarPow(self.field.order - 2)

    def clone(self):
      return self.field.Element(self.value, self.field)

    def __eq__(self, a):
      return type(self) == type(a) and self.value == a.value

    def __int__(self):
      return self.value

    def sqrt(self):
      if self.field.order % 4 == 3:
        # The x^(p+1)/4 = x^2 trick seems to work for fields that have a p+1 divisible by 4.
        # FIXME: Find out why.
        s = self.scalarPow((self.field.order + 1) // 4)
        if self.field.mul(s, s) == self:
          return s
        else:
          return None
      else:
        # Implement https://en.wikipedia.org/wiki/Tonelli%E2%80%93Shanks_algorithm here.
        raise ValueError("Unsupport sqrt")

    def __hash__(self):
      return hash((self.field, self.value))
