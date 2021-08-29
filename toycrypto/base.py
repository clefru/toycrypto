import hashlib
import binascii
from typing import TypeVar, Generic, Callable

T = TypeVar('T')


def opN(self, n: int, neutral: T, op: Callable[[T, T], T]) -> T:
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


class Base(object):

  def __repr__(self) -> str:
    raise NotImplementedError

  def __eq__(self, other: object) -> bool:
    raise NotImplementedError


class Group(Base):

  def plusID(self) -> 'Group.Element':
    raise NotImplementedError

  def plus(self, a: 'Group.Element', b: 'Group.Element') -> 'Group.Element':
    raise NotImplementedError

  class Element(Base):

    def __init__(self, field: 'Group'):
      self.field = field

    def isPlusID(self) -> bool:
      return self == self.field.plusID()

    def scalarMul(self, scalar: int) -> 'Group.Element':
      """Scalar multiplication"""
      return opN(self, scalar, self.field.plusID(), self.field.plus)

    def __eq__(self, other: object) -> bool:
      raise NotImplementedError


class Field(Group):

  def mulID(self) -> 'Field.Element':
    raise NotImplementedError

  def mul(self, a: 'Field.Element', b: 'Field.Element') -> 'Field.Element':
    raise NotImplementedError

  def longDiv(self, a: 'Field.Element', b: 'Field.Element') -> 'Field.Element':
    raise NotImplementedError

  class Element(Group.Element):

    def __init__(self, field: 'Field'):
      self.field = field

    def isMulID(self) -> bool:
      return self == self.field.mulID()

    def scalarPow(self, scalar: int) -> 'Field.Element':
      """Scalar power"""
      return opN(self, scalar, self.field.mulID(), self.field.mul)
