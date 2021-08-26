import base


class EC(base.Group):
  """Elliptic Curve Group.

  y^2 = x^3 + a x + b
  """

  def __init__(self, field, A, B):
    self.field = field
    self.A = A
    self.B = B
    self.O = EC.Element(self, None, None)

  def __eq__(self, other):
    return self.field == other.field and self.A == other.A and self.B == other.B

  def fromX(self, x):
    y = self.field.plus(x.scalarPow(3),
                        self.field.plus(self.field.mul(self.A, x),
                                        self.B)).sqrt()
    if not y:
      return None

    return self.Element(self, x, y)

  def plusID(self):
    return self.O

  def plus(self, a, b):
    # Implemented according to
    # https://www.math.brown.edu/~jhs/Presentations/WyomingEllipticCurve.pdf
    f = self.field

    if a.isPlusID():
      return b

    if b.isPlusID():
      return a

    if a.x == b.x and a.y == b.y:
      if a.y == f.plusID():
        return self.plusID()
      else:
        # This is the tangency case
        # x^2
        x2 = f.mul(a.x, a.x)
        # 3x^2
        x23 = f.plus(f.plus(x2, x2), x2)
        # y^2
        twoy = f.plus(a.y, a.y)
        # y^-2
        twoy_inv = twoy.mulInv()
        lmbd = f.mul(f.plus(x23, self.A), twoy_inv)

        minus_x3 = f.mul(a.x, x2).plusInv()
        vu = f.mul(
            f.plus(minus_x3, f.plus(f.mul(self.A, a.x),
                                    f.plus(self.B, self.B))), twoy_inv)
    else:
      # As This implies a.y != b.y, which can only happen when a.y = -b.y. Hence, return O.
      if a.x == b.x:
        return self.plusID()
      else:
        lmbd = f.mul(f.plus(b.y, a.y.plusInv()),
                     f.plus(b.x, a.x.plusInv()).mulInv())
        vu = f.mul(f.plus(f.mul(a.y, b.x),
                          f.mul(b.y, a.x).plusInv()),
                   f.plus(b.x, a.x.plusInv()).mulInv())
    lmbd2 = f.mul(lmbd, lmbd)
    return self.Element(
        self, f.plus(lmbd2,
                     f.plus(a.x, b.x).plusInv()),
        f.plus(f.mul(lmbd, f.plus(a.x, b.x)),
               f.plus(vu, f.mul(lmbd2, lmbd)).plusInv()))

  def __repr__(self):
    return "EC: x^3 + %r x + %r" % (self.A, self.B)

  class Element(base.Group.Element):
    """Element in an Elliptic Curve."""

    def __init__(self, ec, x, y):
      # FIXME, verify that we are on the curve here.
      self.field = ec
      self.x = x
      self.y = y

    def plusInv(self):
      # Check this. I think that it's just and inversion of y.
      if self.isPlusID():
        return self
      return self.field.Element(self.field, self.x, self.y.plusInv())

    def __repr__(self):
      return "ECElement: %(x)r %(y)r" % {'x': self.x, 'y': self.y}

    def __eq__(self, a):
      return type(self) == type(
          a) and self.field == a.field and self.x == a.x and self.y == a.y


class ECSubfield(base.Group):

  def __init__(self, ec, g, order):
    self.ec = ec
    self.g = g
    self.order = order

  def make(self, n):
    # FIXME type
    return self.Element(self, self.g.scalarMul(n))

  def plus(self, a, b):
    new_point = self.ec.plus(a.point, b.point)
    return self.Element(self, new_point)

  def plusID(self):
    return self.Element(self, self.ec.plusID())

  def __str__(self):
    return "ECSubfield(%r, %r, %x)" % (self.ec, self.g, self.order)

  def __repr__(self):
    return self.__str__()

  # TODO: Either remove this class or remove it, as the subfield
  # element is just an ellipitic curve field element, and users are
  # likely to mix and match between those.
  class Element(base.Group.Element):

    def __init__(self, field, point):
      self.point = point
      self.field = field

    def __int__(self):
      raise NotSupported("ECDLP is in my way, please fix.")

    def __repr__(self):
      return "ECSubfieldElement: %r" % self.point

    def __eq__(self, a):
      return type(self) == type(
          a) and self.field == a.field and self.point == a.point
