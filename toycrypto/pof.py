# Remove Field super-class as polynomials don't form a field.
from toycrypto.base import *
from functools import reduce
from typing import Union, Dict, List, Any, Tuple


class POF(Field):
  """Implementation of a polynomial over an arbitrary field.

  POF=PolynomialOverField
  """

  def __init__(self, field: Field):
    super(POF, self).__init__()
    self.field = field

  def plus(self, a: Group.Element, b: Group.Element) -> 'POF.Element':
    assert isinstance(a, POF.Element)
    assert isinstance(b, POF.Element)
    newp = a.clone()
    for i in b.nonZeroCoefficients():
      newp.addToCoefficient(i, b.getCoefficient(i))
    return newp

  def mul(self, a: Field.Element, b: Field.Element) -> 'POF.Element':
    assert isinstance(a, POF.Element)
    assert isinstance(b, POF.Element)
    # Get new result polynomial with all zero coefficients.
    newp = self.plusID()
    for k1 in a.nonZeroCoefficients():
      for k2 in b.nonZeroCoefficients():
        newp.addToCoefficient(
            k1 + k2, self.field.mul(a.getCoefficient(k1), b.getCoefficient(k2)))
    return newp

  def longDiv(self, dividend: 'POF.Element',
              divisor: 'POF.Element') -> Tuple['POF.Element', 'POF.Element']:
    """Divides dividend by divisor."""

    # Divides
    #   a_n x^n + a_n-1 x^n-1 + a_n-2 x^n-2 + ... + a_1 x + a_0
    # by
    #   b_m x^m + b_m-1 x^m-1 + b_m-2 x^m-2 + ... + b_1 x + b_0
    # This works as long as n >= m
    #
    # Let's assume that we want to divide
    # 6 x^4 + 2 x^3 + 9 x^2 + x + 3    by
    #                 2 x^2 +   + 7
    # The difference in the highest degrees (x^4 vs x^2). So the quotient
    # polynomial will have a coefficient for x^2. To find out what coefficient
    # it is, we do a field division and find that have 6/2 = 3. We multiply
    # the rest of the division polynomial by 3 and subtract it.
    # We end up at up:
    #   6 x^4 + 2 x^3 +  9 x^2 + x + 3 (original polynomial)
    # subtracted by
    #   6 x^4 +       + 21 x^2         (divisor multiplied by 3 x^2)
    # ending in:
    #   2 x^3 - 12 x^2 + x + 3         (potential reminder)
    # and we accumulate 3 x^2 in the quotient polynomial.
    #
    # We repeat the game, find that the highest degree difference has
    # shrunk to 1 (x^3 vs x^2) multiply the divisor by 3/2 and
    # subtract again. Once the potential reminder has a lower degree
    # than the divisor, we stop.
    #
    # The algorithm below is built on that illustration. xtimes is the
    # difference in the polynomial degree, while q is the quotient
    # between the coefficients of the highest degrees.
    #
    # We start off with the whole dividend as potential reminder
    reminder = dividend.clone()
    quotient = self.plusID()

    while reminder.getDegree(
    ) is not None and reminder.getDegree() >= divisor.getDegree():
      xtimes = reminder.getDegree() - divisor.getDegree()

      #while True:
      #  rem_deg = reminder.getDegree()
      #  if rem_deg is None:
      #    break
      #  assert isinstance(rem_deg, int)
      #  div_deg = divisor.getDegree()
      #  assert isinstance(div_deg, int)
      #  if rem_deg >= div_deg:
      #    break
      #  xtimes = rem_deg - div_deg
      q = self.field.mul(
          divisor.getCoefficient(divisor.getDegree()).mulInv(),
          reminder.getCoefficient(reminder.getDegree()))
      # Accumulate coefficient in quotient.
      quotient.setCoefficient(xtimes, q)
      for k in divisor.nonZeroCoefficients():
        # Subtract shifted divisor polynomial
        pol = self.field.mul(divisor.getCoefficient(k), q).plusInv()
        assert isinstance(pol, Field.Element)
        reminder.addToCoefficient(k + xtimes, pol)
    return (quotient, reminder)

  def plusID(self) -> 'POF.Element':
    return self.make([])

  def mulID(self) -> 'POF.Element':
    return self.make([self.field.mulID()])

  def make(self, x: Union[Dict[int, int], int, List[int]]) -> 'POF.Element':

    def makeFromDict(d: Dict[int, int]) -> 'POF.Element':
      pofi = self.Element(self)
      for (k, v) in d.items():
        pofi.setCoefficient(k, self.field.make(v))
      return pofi

    def makeFromList(lst: List[int]) -> 'POF.Element':
      """Create polynomial from field coefficient list."""
      pofi = self.Element(self)
      for i in range(0, len(lst)):
        pofi.setCoefficient(i, self.field.make(lst[i]))
      return pofi

    def makeFromInt(i: int) -> 'POF.Element':
      res = self.Element(self)
      n = 0
      while i:
        c, i = self.field.enum(i)
        res.setCoefficient(n, c)
        n += 1
      return res

    if type(x) == int:
      assert isinstance(x, int)
      return makeFromInt(x)
    if type(x) == list:
      assert isinstance(x, list)
      return makeFromList(x)
    if type(x) == dict:
      assert isinstance(x, dict)
      return makeFromDict(x)
    raise ValueError("Unknown object to make from.")

  def __eq__(self, other: object) -> bool:
    # TODO: Check all __eq__ for proper type mismatch handling
    assert isinstance(other, POF)
    return self.field == other.field

  def __hash__(self) -> int:
    return hash(self.field)

  class Element(Field.Element):

    def __init__(self, pof: 'POF'):
      super(POF.Element, self).__init__(pof)
      self.pof = pof
      self.c = {}

    def setCoefficient(self, n: int, e: 'Field.Element') -> 'POF.Element':
      """Sets coefficient of x^n."""
      if e.isPlusID():
        if n in self.c:
          self.c.pop(n)
      else:
        self.c[n] = e
      return self

    def getCoefficient(self, n: int) -> 'Field.Element':
      default = self.pof.field.plusID()
      assert isinstance(default, Field.Element)
      return self.c.get(n, default)

    def addToCoefficient(self, n: int, elem: 'Field.Element') -> 'POF.Element':
      added = self.pof.field.plus(self.getCoefficient(n), elem)
      assert isinstance(added, Field.Element)
      return self.setCoefficient(n, added)

    def getDegree(self) -> Union[None, int]:
      keys = self.c.keys()
      if keys:
        return max(keys)
      else:
        return None

    def nonZeroCoefficients(self) -> List[int]:
      return self.c.keys()

    def plusInv(self) -> 'POF.Element':
      return self.pof.make(dict((k, v.plusInv()) for k, v in self.c.items()))

    def __str__(self) -> str:
      return self.__repr__()

    def __repr__(self) -> str:
      es = ""
      keys = self.c.keys()
      for k in sorted(keys):
        cof = self.getCoefficient(k)
        if not cof.isMulID() or k == 0:
          es = es + cof.__str__()
        if (k > 0):
          es = es + " x"
          if (k > 1):
            es = es + "^" + k.__str__()
        es = es + " + "
      if es == "":
        return self.pof.field.plusID().__str__()
      else:
        # Remove trailing plus
        return es[:-3]

    def clone(self) -> 'POF.Element':
      clone = self.pof.plusID()
      for i in self.nonZeroCoefficients():
        clone.setCoefficient(i, self.getCoefficient(i).clone())
      return clone

    def xtime(self) -> 'POF.Element':
      # Shift all coefficients higher by one
      return self.pof.make(dict((k + 1, v) for k, v in self.c.items()))

    def __eq__(self, other: object) -> bool:
      if type(other) != type(self):
        return False
      assert isinstance(other, POF.Element)
      return self.pof == other.pof and self.c == other.c

    def toEL(self) -> List[Field.Element]:
      """Get coefficient list in underlying field from polynomial."""
      return [self.getCoefficient(i) for i in range(0, self.getDegree() + 1)]

    def __int__(self) -> int:
      res = 0
      for i in range(self.getDegree() + 1, 0):
        res += int(self.getCoefficient(i))
        res *= self.field.getOrder()
      return res

    def __hash__(self) -> int:
      return reduce(lambda x, h: hash((x, h)), sorted(self.c.items()),
                    hash(self.pof))
