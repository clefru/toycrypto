import hashlib
import binascii
from typing import TypeVar, Generic, Callable, Tuple

T = TypeVar('T')
S = TypeVar('S')


def opN(self: S, n: int, neutral: S, op: Callable[[S, S], S]) -> S:
  """Applies op(self, op(self, ... op(self, neutral))) n-times"""

  # Assuming a binary operator "op", we create the operator lambda a: op1(self, a). Then we apply
  # op1 to neutral n-times as given by the scalar.
  #
  # The implementation here uses the double-and-add algorithm to optimize this to log_n steps.

  if n < 0:
    raise ValueError("Scalar %d can't be negative" % n)

  res = neutral
  # This variable will double every step and whenever we hit a "true"-bit add itself to res.
  w = self
  while n:
    if n % 2:
      res = op(res, w)
    w = op(w, w)
    n = n // 2
  return res


class Group(Generic[T]):

  def plusID(self) -> T:
    raise NotImplementedError

  def plus(self, a: T, b: T) -> T:
    raise NotImplementedError

  class Element(object):

    def __init__(self, group: 'Group[T]'):
      self.group = group

    def clone(self) -> T:
      raise NotImplementedError

    def isPlusID(self) -> bool:
      return self == self.group.plusID()

    def scalarMul(self, scalar: int) -> T:
      """Scalar multiplication"""
      return opN(self, scalar, self.group.plusID(), self.group.plus)

    def plusInv(self) -> T:
      raise NotImplementedError

    def __eq__(self, other: object) -> bool:
      raise NotImplementedError


class Field(Group[T]):

  def mulID(self) -> T:
    raise NotImplementedError

  def mul(self, a: T, b: T) -> T:
    raise NotImplementedError

  def longDiv(self, a: T, b: T) -> Tuple[T, T]:
    raise NotImplementedError

  def make(self, i: int) -> T:
    raise NotImplementedError

  def enum(self, i: int) -> Tuple[T, int]:
    raise NotImplementedError

  class Element(Group.Element):

    def __init__(self, field: 'Field[T]'):
      super(Field.Element, self).__init__(field)
      self.field = field

    def isMulID(self) -> bool:
      return self == self.field.mulID()

    def mulInv(self) -> T:
      raise NotImplementedError

    def scalarPow(self, scalar: int) -> T:
      """Scalar power"""
      return opN(self, scalar, self.field.mulID(), self.field.mul)
