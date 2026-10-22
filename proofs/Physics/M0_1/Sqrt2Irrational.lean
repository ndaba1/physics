module

public import Mathlib

/-!
# M0.1 — √2 is irrational

Derivation of the day for M0.1.d1. Two routes:

* `sqrt2_irrational` uses Mathlib's general lemma: the square root of a prime is irrational.
* `sqrt2_irrational'` cites Mathlib's named result directly, as a cross-check.
-/

public section

namespace Physics.M0_1

/-- `√2` is irrational, because `2` is prime. -/
theorem sqrt2_irrational : Irrational (Real.sqrt 2) := by
  have h : Nat.Prime 2 := Nat.prime_two
  simpa using h.irrational_sqrt

/-- The same statement, via Mathlib's named lemma. -/
theorem sqrt2_irrational' : Irrational (Real.sqrt 2) :=
  irrational_sqrt_two

/-- No rational number squares to `2`. -/
theorem no_rat_sq_eq_two (q : ℚ) : q ^ 2 ≠ 2 := by
  intro hq
  apply sqrt2_irrational
  refine ⟨|q|, ?_⟩
  rw [Rat.cast_abs, ← Real.sqrt_sq_eq_abs]
  congr 1
  exact_mod_cast hq

end Physics.M0_1

end
