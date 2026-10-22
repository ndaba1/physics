#import "../_template.typ": essay

#show: essay.with(
  title: "What I learned: proof by contradiction",
  module: "M0.1 Proof, logic, mathematical writing",
  date: datetime(year: 2026, month: 10, day: 22),
)

= Claim

$sqrt(2)$ is irrational: there are no integers $p, q$ with $q != 0$ and $(p/q)^2 = 2$.

= Derivation

Suppose $sqrt(2) = p/q$ with $gcd(p, q) = 1$. Squaring,
$ p^2 = 2 q^2. $ <sq>
So $p^2$ is even, hence $p$ is even (an odd number squared is odd). Write $p = 2k$.
Substituting into @sq gives $4k^2 = 2q^2$, so $q^2 = 2k^2$ and $q$ is even too.
Then $2 | gcd(p, q)$, contradicting $gcd(p, q) = 1$. #h(1fr) $square$

Machine-checked: `proofs/Physics/M0_1/Sqrt2Irrational.lean`.

= What confused me

Placeholder. Why "lowest terms" can be assumed without loss of generality:
it needs the fact that every fraction reduces, which is itself a well-ordering argument.

= What it connects to

Placeholder. The same argument shows $sqrt(p)$ is irrational for every prime $p$
(Mathlib's `Nat.Prime.irrational_sqrt`); it is the first use of "prime divides a
square ⇒ prime divides the base", which returns as Euclid's lemma in M0.2.
