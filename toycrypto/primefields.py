from toycrypto.base import *
from typing import Any, Union, Tuple


class Z(Field['Z.Element']):
  """Implementation of the mathemical set Z/nZ."""

  def __init__(self, order: int):
    super(Z, self).__init__()
    self.order = order

  def getOrder(self) -> int:
    return self.order

  def plusID(self) -> 'Z.Element':
    return self.Element(0, self)

  def plus(self, a: 'Z.Element', b: 'Z.Element') -> 'Z.Element':
    if a.z_field != b.z_field:
      raise ValueError('Trying to add ZElements from different Z classes')

    return self.Element(a.value + b.value, self)

  def mulID(self) -> 'Z.Element':
    return self.Element(1, self)

  def mul(self, a: 'Z.Element', b: 'Z.Element') -> 'Z.Element':
    if a.z_field != b.z_field:
      raise ValueError('Trying to add ZElements from different Z classes')

    return self.Element(a.value * b.value, self)

  def __str__(self) -> str:
    return "Z(%d)" % self.order

  def __repr__(self) -> str:
    return "Z(%d)" % self.order

  def make(self, i: Union['Z.Element', int]) -> 'Z.Element':
    if type(i) == self.Element:
      assert isinstance(i, Z.Element)
      # Copy and return new element in my field
      return self.Element(i.value, self)

    if type(i) == int:
      assert isinstance(i, int)
      return self.Element(i, self)

    raise ValueError("Unknown object type to make from: %s" % type(i))

  def enum(self, i: int) -> Tuple['Z.Element', int]:
    return (self.Element(i % self.order, self), i // self.order)

  def __eq__(self, a: object) -> bool:
    if type(a) != Z:
      return False

    assert isinstance(a, Z)
    return self.order == a.order

  def __hash__(self) -> int:
    return hash(self.order)

  class Element(Field.Element):

    def __init__(self, value: int, field: 'Z'):
      super(Z.Element, self).__init__(field)
      self.z_field = field
      if type(value) != int:
        raise ValueError("value must be an int")
      self.value = value % field.order

    def __str__(self) -> str:
      return "%(v)d" % {'v': self.value, 's': self.z_field}

    def __repr__(self) -> str:
      return "%(v)x" % {'v': self.value, 's': self.z_field}

    def setValue(self, value: int) -> 'Z.Element':
      self.value = value % self.z_field.order
      return self

    def plusInv(self) -> 'Z.Element':
      return Z.Element(self.z_field.order - self.value, self.z_field)

    def mulInv(self) -> 'Z.Element':
      r = self.scalarPow(self.z_field.order - 2)
      assert isinstance(r, Z.Element)
      return r

    def clone(self) -> 'Z.Element':
      return self.z_field.Element(self.value, self.z_field)

    def __eq__(self, a: object) -> bool:
      if not isinstance(a, Z.Element):
        return False
      assert isinstance(a, Z.Element)
      return self.z_field == a.z_field and self.value == a.value

    def __int__(self) -> int:
      return self.value

    def sqrt(self) -> Union[None, 'Z.Element']:
      if self.z_field.order % 4 == 3:
        # The x^(p+1)/4 = x^2 trick seems to work for fields that have a p+1 divisible by 4.
        # FIXME: Find out why.
        s = self.scalarPow((self.z_field.order + 1) // 4)
        assert isinstance(s, Z.Element)
        if self.z_field.mul(s, s) == self:
          return s
        else:
          return None
      else:
        # Implement https://en.wikipedia.org/wiki/Tonelli%E2%80%93Shanks_algorithm here.
        raise ValueError("Unsupport sqrt")

    def __hash__(self) -> int:
      return hash((self.z_field, self.value))
