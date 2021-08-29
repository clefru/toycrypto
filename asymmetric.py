import collections
import random

from ec import *
from primefields import *

p = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1
z = Z(p)
secp256k1 = EC(z, z.make(0), z.make(7))
secp256k1_G = secp256k1.fromX(
    z.make(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798))
secp256k1_GField = ECSubfield(
    secp256k1, secp256k1_G,
    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)


class Signature(collections.namedtuple("Signature", ["s", "K"])):
  """Schnorr signatures over secp256k1."""
  Hfield = secp256k1_GField
  nF = Z(Hfield.order)

  @classmethod
  def sign(cls, e, x):
    k = cls.gen_private_key()
    s = cls.nF.plus(k, cls.nF.mul(x, cls.nF.make(e)))
    return Signature(s, cls.Hfield.make(int(k)))

  @classmethod
  def merge(cls, s1, s2):
    return Signature(cls.nF.plus(s1.s, s2.s),
                     Signature.Hfield.ec.plus(s1.K, s2.K))

  def verify(self, pubKey, e):
    S = Signature.Hfield.make(int(self.s))
    V = Signature.Hfield.ec.plus(self.K, pubKey.scalarMul(e))
    return S == V

  @classmethod
  def gen_private_key(cls):
    return cls.nF.make(random.randrange(1, Signature.Hfield.order))

  @classmethod
  def make_pub_key(cls, private_key):
    return Signature.Hfield.make(int(private_key))


"""DH key exchange: A regenerates a secret, x and computes, X=xG. B
generates a secret y and computes Y=yG. Both parties exchange X & Y
which are elliptic curve points that can't be factored back into x & G
nor y & G. A scalar multiplies Y with x and gets xyG, while B scalar
multiplies X with y and gets xyG. xyG is the shared secret now."""

import hashlib


class RingSignatureRSA(
    collections.namedtuple("RignSignatureRSA", ["xs", "m", "v"])):

  # E implements a simple 'encryption' method. Sadly it has no
  # decryption method.
  @classmethod
  def E(cls, k, v):
    m = hashlib.sha256()
    m.update(k)
    m.update(v)
    return m.digest()

  @classmethod
  def C(cls, k, ys, v):
    for y in ys:
      v = E(y ^ v)
    return v

  # IDEAS
  # Can we create a trapdoor function based on EC?
  # ---------------------------------------------
  # Have your public component consist of s & X where s is a scalar
  # and X is a EC point. The trapdoor function is "Y = sG + X".
  #
  # Assume that we know 'x', which is the factor of X, x=xG. Then we
  # can produce a Y with a chosen factor y, such that Y=yG.

  @classmethod
  def trapdoor(cls, x):
    raise NotImplementedError()

  @classmethod
  def trapdoor_invert(cls, y):
    raise NotImplementedError()

  # The verification is defined as:
  #
  # Compute ys = [ trapdoor(x) for x in xs ]
  # Then
  # C(k,v) = E(ys[n] ^ E(ys[n-1] ^ E(ys[n-2] ^ .... E(y[1] ^ E(y[0] ^ v)))))
  #
  # A ring signature is valid, when C(k,v) = v. This condition can
  # only hold when for one x, the signature constructor was able to
  # invert the trapdoor function.

  def verify(self, m):
    ys = map(RignSignatureRSA.trapdoor, self.xs)
    v_ = RignSignatureRSA.C(sha256(m), ys, v)
    return v_ == v

  # Signature construction:
  #
  # We start with a minimal formulation of the ring equation above
  # for 5 elements, with y-s already having applied the trapdoor
  # function to it.
  #
  # w = E(y_5 ^ E(y_4 ^ E(y_3 ^ E(y_2 ^ E(y_1 ^ v)))))
  #
  # The ring equation holds if w == v. To achieve that, we must
  # control be able to control one y value. Let's presume that we
  # can control the y_3 by knowning how to invert x_3. To make the
  # ring equation hold, we compute;
  #
  # y_3 = D(y_4 ^ D(y_5 ^ D(v))) ^ E(y_2 ^ E(y_1 ^ v)))
  #
  # where, D=E^-1. Then compute x_3 = trapdoor_invert(y_3).
  #
  # In the formulation above, we used an invertable E. But we can
  # also satisfy the ring equation with E being uninvertable, like a
  # hash. For 5 elements the ring equation is:
  #
  # v = E(y_5 ^ E(y_4 ^ E(y_3 ^ E(y_2 ^ E(y_1 ^ v)))))
  #
  # Let's assume that we control y_1. To make the equatoin hold, We
  # start with a random w replacing y_1 ^ v:
  #
  # v = E(y_5 ^ E(y_4 ^ E(y_3 ^ E(y_2 ^ E(w)))))     (1)
  #
  # After we compute v, we set y_1 = w ^ v. When we apply the
  # original equation,
  #
  # v = E(y_5 ^ E(y_4 ^ E(y_3 ^ E(y_2 ^ E(y_1 ^ v)))))
  #
  # and compute y_1 ^ v = w ^ v ^ v = w, we find that the original
  # equation holds.
  #
  # However, fixing which public key index we control to x_1 would
  # defeat the purpose of ring signatures being a tool for hiding
  # which exact public key is known. But luckily, we can relax this
  # requirement. Let's assume we control x_3/y_3. Let's pick a
  # random w and substitute y_3 ^ E(y_2 ^ ...) with just w.
  #
  # v = E(y_5 ^ E(y_4 ^ E(w)))     (1)
  #
  # then we compute
  #
  # w_ = E(y_2 ^ E(y_1 ^ v))
  #
  # where w_ is the w that we would like to have chosen for
  # w. Luckily we can force, w == w_ by using y_3, which is achieved
  # by w ^ w_ = y_3.
  #
  # We now have a way to construct values for our ring equation
  # without having D and with a free choice of our public key index.

  @classmethod
  def sign(cls, myPubKey, otherPubKeys, m):
    k = sha256(m)
    ys = map(trapdoor, otherPubKeys)
    randomInsertPoint = random(len(otherPubKeys))
    w = random()
    v = C(k, ys[0:randomInsertPoint], w)
    w_ = C(k, ys[randomInsertPoint:], v)
    y = w ^ w_
    x = trapdoor_invert(y)
    return RignSignatureRSA(
        other_xs[0:randomInsertPoint] + [my_x] + other_xs[randomInsertPoint:],
        m, v)


class RingSignatureEC(
    collections.namedtuple("RignSignatureEC", ["xs", "m", "v"])):

  @classmethod
  def E(cls, k, v):
    m = hashlib.sha256()
    m.update(k)
    m.update(v)
    return m.digest()

  @classmethod
  def C(cls, k, ys, v):
    for y in ys:
      v = H(
          k,
          sec256p1k.plus(secp256k1_Hfield.make(ps[i - 1].r),
                         ps[i].X.scalarmul(c)))
    return v

  def verify(self, m):
    ys = map(RignSignatureRSA.trapdoor, self.xs)
    v_ = RignSignatureRSA.C(sha256(m), ys, v)
    return v_ == v

  @classmethod
  def sign(cls, myPubKey, otherPubKeys, m):
    k = sha256(m)
    ys = map(trapdoor, otherPubKeys)
    randomInsertPoint = random(len(otherPubKeys))
    w = random()
    v = C(k, ys[0:randomInsertPoint], w)
    w_ = C(k, ys[randomInsertPoint:], v)
    y = w ^ w_
    x = trapdoor_invert(y)
    return RignSignatureRSA(
        other_xs[0:randomInsertPoint] + [my_x] + other_xs[randomInsertPoint:],
        m, v)
