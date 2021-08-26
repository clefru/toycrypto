# Remove Field super-class as polynomials don't form a field.
from base import *


class POF(Field):
  """Implementation of a polynomial over an arbitrary field.

  POF=PolynomialOverField
  """

  def __init__(self, field):
    super(POF, self).__init__()
    self.field = field

  def plus(self, a, b):
    newp = a.clone()
    for i in b.nonZeroCoefficients():
      newp.addToCoefficient(i, b.getCoefficient(i))
    return newp

  def mul(self, a, b):
    # Get new result polynomial with all zero coefficients.
    newp = self.plusID()
    for k1 in a.nonZeroCoefficients():
      for k2 in b.nonZeroCoefficients():
        newp.addToCoefficient(
            k1 + k2, self.field.mul(a.getCoefficient(k1), b.getCoefficient(k2)))
    return newp

  def longDiv(self, dividend, divisor):
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

    while reminder.getDegree() is not None and reminder.getDegree() >= divisor.getDegree():
      xtimes = reminder.getDegree() - divisor.getDegree()
      q = self.field.mul(
          divisor.getCoefficient(divisor.getDegree()).mulInv(),
          reminder.getCoefficient(reminder.getDegree()))
      # Accumulate coefficient in quotient.
      quotient.setCoefficient(xtimes, q)
      for k in divisor.nonZeroCoefficients():
        # Subtract shifted divisor polynomial
        reminder.addToCoefficient(
            k + xtimes,
            self.field.mul(divisor.getCoefficient(k), q).plusInv())
    return (quotient, reminder)

  def plusID(self):
    return self.make([])

  def mulID(self):
    return self.make([self.field.mulID()])

  def make(self, x):

    def makeFromDict(d):
      pofi = self.Element(self)
      for (k, v) in d.items():
        pofi.setCoefficient(k, self.field.make(v))
      return pofi

    def makeFromList(lst):
      """Create polynomial from field coefficient list."""
      pofi = self.Element(self)
      for i in range(0, len(lst)):
        pofi.setCoefficient(i, self.field.make(lst[i]))
      return pofi

    def makeFromInt(i):
      res = self.Element(self)
      n = 0
      while i:
        c, i = self.field.enum(i)
        res.setCoefficient(n, c)
        n += 1
      return res

    if type(x) == int:
      return makeFromInt(x)
    if type(x) == list:
      return makeFromList(x)
    if type(x) == dict:
      return makeFromDict(x)
    raise ValueError("Unknown object to make from.")

  def __eq__(self, other):
    return type(self) == type(other) and self.field == other.field

  class Element(Field.Element):

    def __init__(self, pof):
      super(POF.Element, self).__init__(pof)
      self.pof = pof
      self.c = {}

    def setCoefficient(self, n, c):
      """Sets coefficient of x^n."""
      if c.isPlusID():
        if n in self.c:
          self.c.pop(n)
      else:
        self.c[n] = c
      return self

    def getCoefficient(self, n):
      return self.c.get(n, self.pof.field.plusID())

    def addToCoefficient(self, n, i):
      return self.setCoefficient(n,
                                 self.pof.field.plus(self.getCoefficient(n), i))

    def getDegree(self):
      keys = self.c.keys()
      if keys:
        return max(keys)
      else:
        return None

    def nonZeroCoefficients(self):
      return self.c.keys()

    def plusInv(self):
      return self.pof.make(dict((k, v.plusInv()) for k, v in self.c.items()))

    def __str__(self):
      return self.__repr__()

    def __repr__(self):
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

    def clone(self):
      clone = self.pof.plusID()
      for i in self.nonZeroCoefficients():
        clone.setCoefficient(i, self.getCoefficient(i).clone())
      return clone

    def xtime(self):
      # Shift all coefficients higher by one
      return self.pof.make(dict((k + 1, v) for k, v in self.c.items()))

    def __eq__(self, other):
      return type(self) == type(
          other) and self.pof == other.pof and self.c == other.c

    def toEL(self):
      """Get coefficient list in underlying field from polynomial."""
      return [self.getCoefficient(i) for i in range(0, self.getDegree() + 1)]

    def __int__(self):
      res = 0
      for i in range(self.getDegree() + 1, 0):
        res += self.getCoefficient(i)
        res *= self.field.getOrder()
      return res
