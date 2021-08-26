import pof
import base


class GFPOF(pof.POF, base.Field):
  """Implementation of a Galois field."""

  def __init__(self, field, rp):
    # Field is coefficent field.
    super(GFPOF, self).__init__(field)
    self.rp = rp

  def plusID(self):
    return self.Element(self)

  def mul(self, a, b):
    """Multiplies two polynomials and applies the reduction polynomial."""

    # We classically think about polynomial multiplication as:
    #
    # (a_3 x^3 + a_2 x^2 + a_1 x + a_0) * (b_3 x^3 + b_2 x^2 + b_1 x + b_0) as
    # (a_3 x^3 + a_2 x^2 + a_1 x + a_0) *  b_3 x^3 +
    # (a_3 x^3 + a_2 x^2 + a_1 x + a_0) *  b_2 x^2 +
    # (a_3 x^3 + a_2 x^2 + a_1 x + a_0) *  b_1 x   +
    # (a_3 x^3 + a_2 x^2 + a_1 x + a_0) *  b_0
    #
    # As the A-polynomial does not change in this, let's abbreviate it with A:
    #
    # A * b_3 x^3 +
    # A * b_2 x^2 +
    # A * b_1 x   +
    # A * b_0
    #
    # An equivalent from is:
    #
    # (((0 * x + A * b_3) * x + A * b_2) * x + A * b_1) * x + A * b_0)
    #
    # Writing this as lisp S-expression makes the bracketing structure more
    # visible:
    #
    # (+ (* x (+ (* x (+ (* x (+ (* x 0)
    #                            (* A b_3))
    #                    (* A b_2))
    #            (* A b_1))
    #    (* A b_0))
    #
    # The recursive nature of this expression becomes visible, and it is
    # generated by the following
    #
    # T = (+ (* x T')
    #        (* A b_n)
    #
    # where T' is the previous iteration starting with off with 0.
    #
    # The multiplication with of T' with x is the xtime algorithm, which takes
    # care of polynomial reduction. The multiplication with a coefficient of b
    # and the addition can not cause the polynomial to shift to a higher degree.
    #
    # The following algorithm implements this idea.
    #
    # FIXME: Lift this into the superclass POF and give the superclass an xtime
    #        implementation, as this algorithm is not GF specific.

    result = self.plusID()
    for b_p in range(b.getDegree(), -1, -1):
      result = result.xtime()
      for a_p in a.nonZeroCoefficients():
        result.addToCoefficient(
            a_p, self.field.mul(b.getCoefficient(b_p), a.getCoefficient(a_p)))
    return result

  class Element(pof.POF.Element):

    def __init__(self, pof):
      super(GFPOF.Element, self).__init__(pof)
      self.pof = pof
      self.c = {}

    def setCoefficient(self, n, c):
      if n >= self.pof.rp.getDegree():
        raise ValueError(
            "can't set coefficient larger than the reduction polynomial's degree."
        )
      return super(GFPOF.Element, self).setCoefficient(n, c)

    def mulInv(self):
      pof_element = ExtEuclidean(pof.POF(self.pof.field), self.pof.rp, self)[2]
      return self.pof.make(pof_element.c)

    def xtime(self):
      """Multiplies the polynomial by x.

      It is a building block of the multiplication algorithm mul.
      """
      result = self.pof.plusID()

      # The polynomial
      #   a_n x^n     + a_{n-1} x^{n-1} + ... + a_1 x   + a_0
      # gets multiplied by x resulting in
      #   a_n x^{n+1} + a_{n-1} x^n     + ... + a_1 x^2 + a_0 x
      # ... essentially shifting the coefficients by one index higher.
      #
      # The resulting polynomial needs to be reduced by the reduction
      # polynomial. The following loop subtracts the reduction
      # polynomial a_n times from the result, and also shifts the
      # indices.

      # Get the highest coefficient of the reduction polynomial, and
      # subtract the reduction polynomial a_n times from a.
      a_n = self.getCoefficient(self.pof.rp.getDegree() - 1)
      for i in range(0, self.pof.rp.getDegree()):
        result.setCoefficient(
            i,
            self.pof.field.plus(
                # Get plusID from the underlying field for the lowest
                # coefficient
                self.getCoefficient(i - 1) if i else self.pof.field.plusID(),
                self.pof.field.mul(a_n,
                                   self.pof.rp.getCoefficient(i)).plusInv()))
      return result


def ExtEuclidean(field, a, b):
  """Extended Euclidean algorithm."""
  n1 = a
  n2 = b
  (q, r) = field.longDiv(n1, n2)
  x0 = field.mulID()
  x1 = field.plusID()
  y0 = field.plusID()
  y1 = field.mulID()
  #  print "n1:",n1," n2:",n2," q:",q," r:",r
  while not r.isPlusID():
    n1 = n2
    n2 = r
    #    print "x1:", x1, "q:", q, "x0:", x0, "qx1: ", field.mul(q,x1)
    x2 = field.plus(x0, (field.mul(q, x1).plusInv()))
    y2 = field.plus(y0, (field.mul(q, y1).plusInv()))
    x0 = x1
    x1 = x2
    y0 = y1
    y1 = y2
    (q, r) = field.longDiv(n1, n2)


#    print "n1:",n1," n2:",n2," q:",q," r:",r, " x2: ", x2 #, " y2:",y2
  return [n2, x1, y1]
