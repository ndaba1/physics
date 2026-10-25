module

public import Mathlib

/-!
# M0.1 — There are infinitely many primes

Euclid's theorem in two shapes: "above every `n` there is a prime" and
"the set of primes is infinite".
-/

public section

namespace Physics.M0_1

/-- For every `n` there is a prime `p ≥ n`. -/
theorem exists_prime_ge (n : ℕ) : ∃ p, n ≤ p ∧ p.Prime :=
  Nat.exists_infinite_primes n

/-- The set of primes is infinite. -/
theorem primes_infinite : {p : ℕ | p.Prime}.Infinite :=
  Nat.infinite_setOfPred_prime

/-- Euclid's construction made explicit: the minimal prime factor of `n! + 1`
is prime and exceeds `n`. -/
theorem euclid (n : ℕ) : ∃ p, n < p ∧ p.Prime := by
  refine ⟨(n.factorial + 1).minFac, ?_, Nat.minFac_prime ?_⟩
  · by_contra h
    push Not at h
    have hp : (n.factorial + 1).minFac.Prime :=
      Nat.minFac_prime (by have := Nat.factorial_pos n; omega)
    have hdvd : (n.factorial + 1).minFac ∣ n.factorial :=
      Nat.dvd_factorial hp.pos h
    have : (n.factorial + 1).minFac ∣ 1 :=
      (Nat.dvd_add_right hdvd).mp (Nat.minFac_dvd _)
    exact hp.one_lt.ne' (Nat.dvd_one.mp this)
  · have := Nat.factorial_pos n
    omega

end Physics.M0_1

end
