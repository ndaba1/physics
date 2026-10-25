"""Builds curriculum.json from hand-transcribed data (source: theoretical-physics-master-curriculum.md).
Run: python3 -I build.py OUT_PATH
"""
import json, sys

# ---------- canonical URLs ----------
OCW = "https://ocw.mit.edu/courses/"
U_ = {
    "hammack": "https://richardhammack.github.io/BookOfProof/",
    "shoup": "https://shoup.net/ntb/",
    "boneh": "https://www.coursera.org/learn/crypto",
    "cryptopals": "https://cryptopals.com/",
    "18.06": OCW + "18-06-linear-algebra-spring-2010/",
    "axler": "https://linear.axler.net/",
    "vmls": "https://web.stanford.edu/~boyd/vmls/",
    "18.01": OCW + "18-01-single-variable-calculus-fall-2006/",
    "lebl": "https://www.jirka.org/ra/",
    "18.02": OCW + "18-02-multivariable-calculus-fall-2007/",
    "nearing": "https://www.physics.miami.edu/~nearing/mathmethods/",
    "feyn1": "https://www.feynmanlectures.caltech.edu/I_toc.html",
    "feyn2": "https://www.feynmanlectures.caltech.edu/II_toc.html",
    "18.03": OCW + "18-03-differential-equations-spring-2010/",
    "stat110": "https://projects.iq.harvard.edu/stat110",
    "6.041": OCW + "6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/",
    "cvx": "https://web.stanford.edu/~boyd/cvxbook/",
    "ee364a": "https://web.stanford.edu/class/ee364a/",
    "ee261": "https://see.stanford.edu/Course/EE261",
    "18.04": OCW + "18-04-complex-variables-with-applications-spring-2018/",
    "mackay": "https://www.inference.org.uk/mackay/itila/",
    "ijepa": "https://arxiv.org/abs/2301.08243",
    "shifrin": "http://alpha.math.uga.edu/~shifrin/ShifrinDiffGeo.pdf",
    "carroll": "https://arxiv.org/abs/gr-qc/9712019",
    "8.01": OCW + "8-01sc-classical-mechanics-fall-2016/",
    "osp1": "https://openstax.org/details/books/university-physics-volume-1",
    "osp2": "https://openstax.org/details/books/university-physics-volume-2",
    "8.033": OCW + "8-033-relativity-fall-2006/",
    "tm": "https://theoreticalminimum.com/",
    "8.02": OCW + "8-02-physics-ii-electricity-and-magnetism-spring-2007/",
    "8.03": OCW + "8-03sc-physics-iii-vibrations-and-waves-fall-2016/",
    "8.04": OCW + "8-04-quantum-physics-i-spring-2016/",
    "8.05": OCW + "8-05-quantum-physics-ii-fall-2013/",
    "8.044": OCW + "8-044-statistical-physics-i-spring-2013/",
    "8.06": OCW + "8-06-quantum-physics-iii-spring-2018/",
    "8.962": OCW + "8-962-general-relativity-spring-2020/",
    "8.334": OCW + "8-334-statistical-mechanics-ii-statistical-physics-of-fields-spring-2014/",
    "srednicki": "https://web.physics.ucsb.edu/~mark/qft.html",
    "preskill": "https://www.preskill.caltech.edu/ph229/",
    "pirsa": "https://pirsa.org/",
    "bilal": "https://arxiv.org/abs/hep-th/0101055",
    "townsend": "https://arxiv.org/abs/gr-qc/9707012",
}
TONG = "https://davidtong.org/teaching/"
for k, slug in {
    "tong-vc": "vector-calculus", "tong-cd": "classical-dynamics", "tong-dr": "dynamics-and-relativity",
    "tong-em": "electromagnetism", "tong-qm": "quantum-mechanics", "tong-sp": "statistical-physics",
    "tong-ss": "solid-state-physics", "tong-pp": "particle-physics", "tong-cosmo": "cosmology",
    "tong-qft": "quantum-field-theory", "tong-gauge": "gauge-theory", "tong-sft": "statistical-field-theory",
    "tong-string": "string-theory",
}.items():
    U_[k] = TONG + slug + "/"

LINES = {"PROG", "3D", "ML", "CRYPTO", "PHYS"}


def C(title, free=True, note=None, url=None):
    r = {"title": title}
    if url:
        r["url"] = U_[url]
    r["free"] = free
    if note:
        r["note"] = note
    return r


def B(lines, text, inferred=False):
    ls = lines.split()
    assert all(l in LINES for l in ls), lines
    r = {"line": ls[0], "lines": ls, "text": text}
    if inferred:
        r["lineInferred"] = True
    return r


def U(title, inp, problems, d=(), b=()):
    return (title, inp, problems, list(d), list(b))


MODULES = []


def M(mid, title, weeks, *, story=(), core=(), derive=(), build=(), exam=None, original=(),
      units=(), prereqs=(), kind="notebook", tags=("physics",), notes=None, checkpoint=None,
      weeksNote=None):
    stage = int(mid[1])
    order = int(mid.split(".")[1])
    pass_mark = 70 if stage == 0 else 65
    m = {
        "id": mid, "stageId": f"S{stage}", "order": order, "title": title,
        "weeks": weeks, "prereqs": list(prereqs), "deliverableKind": kind, "tags": list(tags),
        "story": list(story), "core": list(core),
        "derive": [{"id": f"{mid}.d{i+1}", "text": t} for i, t in enumerate(derive)],
        "build": [dict({"id": f"{mid}.b{i+1}"}, **x) for i, x in enumerate(build)],
    }
    if exam is None:
        m["exam"] = {"text": "No exam listed in the source document", "passMark": pass_mark, "listed": False}
    else:
        m["exam"] = {"text": exam, "passMark": pass_mark}
    m["original"] = list(original)
    if weeksNote:
        m["weeksNote"] = weeksNote
    if notes:
        m["notes"] = list(notes)
    if checkpoint:
        m["checkpoint"] = checkpoint
    m["units"] = [
        {"week": i + 1, "title": t, "input": inp, "problems": pr,
         "deriveIds": [f"{mid}.d{n}" for n in d], "buildIds": [f"{mid}.b{n}" for n in b]}
        for i, (t, inp, pr, d, b) in enumerate(units)
    ]
    MODULES.append(m)
    return m

# =====================================================================
# STAGE 0
# =====================================================================
M("M0.1", "Proof, logic, mathematical writing", 2, kind="lean", tags=["math"],
  story=["Dunham, Journey Through Genius Ch. 1–3 (Hippocrates, Euclid)"],
  core=[C("Hammack, Book of Proof", note="Free PDF. All of it, with exercises.", url="hammack")],
  derive=["√2 irrational", "Infinitely many primes",
          "Induction proofs of loop invariants for 3 algorithms you've written"],
  build=[B("PROG", "Property-based tests (Hypothesis) encoding proved invariants — proof and test are the same object")],
  exam="Hammack chapter tests, self-graded",
  units=[
    U("Logic, sets, direct proof, contrapositive, contradiction", "Hammack Ch. 1–7",
      "Hammack Ch. 1–7 exercises, odd numbers", d=[1, 2]),
    U("Sets, disproof, induction, relations, functions, cardinality", "Hammack Ch. 8–14",
      "Hammack Ch. 8–14 exercises, odd numbers; exam: Hammack chapter tests, self-graded", d=[3], b=[1]),
  ])

M("M0.2", "Number theory & the math of cryptography", 3, kind="lean", tags=["math", "crypto"],
  prereqs=["M0.1"],
  story=["Singh, The Code Book", "Levy, Crypto"],
  core=[C("Shoup, A Computational Introduction to Number Theory and Algebra", note="Ch. 1–8", url="shoup"),
        C("Boneh, Cryptography I (Stanford/Coursera)", note="Free audit", url="boneh"),
        C("Cryptopals", note="Sets 1–3", url="cryptopals")],
  derive=["Euclid/Bézout", "Fermat's little theorem & Euler's theorem", "Why RSA decrypts",
          "Why DH is safe if discrete log is hard", "Elliptic-curve group law", "Why Miller–Rabin works"],
  build=[B("CRYPTO", "RSA (keygen/encrypt/sign) with a note on every attack you're vulnerable to"),
         B("CRYPTO", "DH over a prime field"),
         B("CRYPTO", "EC point addition + scalar mult + ECDH"),
         B("CRYPTO", "AES from spec (GF(2⁸) arithmetic — you'll meet this field again in M0.11)"),
         B("CRYPTO", "Cryptopals sets 1–3")],
  exam="Boneh problem sets; Cambridge IA Numbers & Sets paper",
  original=["Diffie–Hellman 1976 (short)", "RSA 1977 (short)"],
  notes=["Then it's a hobby. Returns at Stage 4 for Shor and lattice crypto."],
  units=[
    U("Integers, congruences, computing with large integers", "Shoup Ch. 1–3; Boneh Cryptography I weeks 1–2",
      "Shoup Ch. 1–3 exercises; Cryptopals set 1", d=[1, 2]),
    U("Euclid's algorithm, primes, abelian groups; RSA and DH", "Shoup Ch. 4–6; Boneh weeks 3–4",
      "Shoup Ch. 4–6 exercises; Boneh problem sets weeks 1–4; Cryptopals set 2", d=[3, 4], b=[1, 2]),
    U("Rings, probability; elliptic curves and AES", "Shoup Ch. 7–8; Boneh weeks 5–6",
      "Shoup Ch. 7–8 exercises; remaining Boneh problem sets; Cryptopals set 3; exam: Cambridge IA Numbers & Sets paper, timed",
      d=[5, 6], b=[3, 4, 5]),
  ])

M("M0.3", "Linear algebra, deeply", 5, kind="lean", tags=["math"], prereqs=["M0.2"],
  story=["Crowe, A History of Vector Analysis (Hamilton's quaternions vs Gibbs/Heaviside — the fight that decided how you write 3D code)",
         "3Blue1Brown, Essence of Linear Algebra (once, for pictures)"],
  core=[C("MIT 18.06 (Strang, OCW)", note="All lectures + psets", url="18.06"),
        C("Axler, Linear Algebra Done Right 4th ed.", note="Free, open access", url="axler"),
        C("Boyd & Vandenberghe, Intro to Applied Linear Algebra", note="For least squares", url="vmls")],
  derive=["Gram–Schmidt → QR", "Spectral theorem (symmetric)", "SVD existence",
          "Least squares by normal equations and projection", "Eigenvalues of a rotation are e^{±iθ}",
          "Change of basis", "The 4×4 perspective projection matrix from first principles",
          "Why quaternions represent rotations and why q and −q are the same rotation (this is the SU(2)→SO(3) double cover, i.e. spin)"],
  build=[B("3D", "Software rasterizer from scratch (follow ssloy tinyrenderer, free): model→world→camera→clip→screen, z-buffer, Phong. <1000 lines."),
         B("3D", "Quaternion lib + slerp"),
         B("3D", "Animated camera path exported to video"),
         B("3D", "Gimbal-lock blog post"),
         B("ML", "PCA from scratch"),
         B("ML", "SVD image compression with a slider"),
         B("ML", "PageRank as an eigenvector"),
         B("PHYS", "Normal modes of N coupled oscillators, animated")],
  exam="18.06 final ≥ 70%",
  original=["Hamilton's 1843 quaternion letter"],
  units=[
    U("Elimination, matrices, vector spaces, the four subspaces", "18.06 lectures 1–10; Axler Ch. 1–3",
      "18.06 psets for lectures 1–10; Axler Ch. 1–3 exercises (selected)", d=[6]),
    U("Orthogonality, projections, least squares, QR", "18.06 lectures 11–17; Axler Ch. 6; Boyd & Vandenberghe Ch. 12–13",
      "18.06 psets for lectures 11–17; Boyd & Vandenberghe Ch. 12 exercises", d=[1, 4]),
    U("Determinants, eigenvalues, rotations, projection matrices", "18.06 lectures 18–24; Axler Ch. 5",
      "18.06 psets for lectures 18–24; Axler Ch. 5 exercises (selected)", d=[5, 7], b=[1]),
    U("Symmetric matrices, the spectral theorem, SVD", "18.06 lectures 25–29; Axler Ch. 7",
      "18.06 psets for lectures 25–29; Axler Ch. 7 exercises (selected)", d=[2, 3], b=[5, 6, 7]),
    U("Linear transformations, quaternions, review", "18.06 lectures 30–34; Hamilton's 1843 letter",
      "18.06 remaining psets; exam: 18.06 final, timed, closed-book (≥ 70%)", d=[8], b=[2, 3, 4, 8]),
  ])

M("M0.4", "Single-variable calculus & analysis foundations", 4, kind="lean", tags=["math"], prereqs=["M0.3"],
  story=["Strogatz, Infinite Powers (whole book)", "Bardi, The Calculus Wars (optional)"],
  core=[C("MIT 18.01 (OCW)", note="For technique", url="18.01"),
        C("Spivak, Calculus", free=False, note="For rigor, pick one of Spivak / Abbott / Lebl"),
        C("Abbott, Understanding Analysis", free=False, note="For rigor, pick one of Spivak / Abbott / Lebl"),
        C("Lebl, Basic Analysis", note="For rigor, pick one of Spivak / Abbott / Lebl", url="lebl")],
  derive=["FTC from Riemann sums", "Taylor's theorem with remainder", "Quadratic convergence of Newton's method",
          "Five ε-δ proofs until boring"],
  build=[B("ML", "Reverse-mode autodiff engine (Karpathy, Neural Networks: Zero to Hero, free) — chain rule as algorithm; train a tiny MLP"),
         B("3D", "Bézier/B-splines: derive de Casteljau"),
         B("3D", "Arc-length reparametrization for constant-speed animation"),
         B("3D", "Easing curves"),
         B("PROG", "Adaptive integrators"),
         B("PROG", "Newton–Raphson sphere-tracing an SDF shader (Inigo Quilez articles, free)")],
  exam="18.01 final",
  original=["Newton, Principia Book I §1–2", "Archimedes, The Method"],
  units=[
    U("Limits, continuity, ε-δ; differentiation", "18.01 Unit 1 (differentiation); Lebl Ch. 1–3 (or your chosen rigor text)",
      "18.01 Unit 1 psets; Lebl Ch. 1–3 exercises (selected)", d=[4]),
    U("Applications of differentiation; Newton's method", "18.01 Unit 2; Lebl Ch. 4",
      "18.01 Unit 2 psets; Lebl Ch. 4 exercises (selected)", d=[3], b=[1]),
    U("Integration and the FTC", "18.01 Units 3–4 (integration, techniques); Lebl Ch. 5",
      "18.01 Units 3–4 psets; Lebl Ch. 5 exercises (selected)", d=[1], b=[5, 6]),
    U("Series and Taylor's theorem; curves", "18.01 Unit 5 (exploring the infinite); Lebl Ch. 6",
      "18.01 Unit 5 psets; exam: 18.01 final, timed, closed-book", d=[2], b=[2, 3, 4]),
  ])

M("M0.5", "Multivariable & vector calculus", 4, tags=["math"], prereqs=["M0.4"],
  story=["Crowe again (div/grad/curl were built for Maxwell)", "Feynman Vol. II Ch. 1–3 (free)"],
  core=[C("MIT 18.02 (OCW)", url="18.02"),
        C("Tong, Vector Calculus", url="tong-vc"),
        C("Nearing, Mathematical Tools for Physics", note="Ch. 8–9, 13", url="nearing")],
  derive=["Gradient = steepest ascent (Cauchy–Schwarz)", "Jacobian & change of variables",
          "Green/Stokes/Gauss (prove on rectangles, argue general)", "Lagrange multipliers geometrically",
          "Hessian & second-derivative test"],
  build=[B("ML", "Gradient descent on 2D landscapes; saddles; conditioning"),
         B("3D", "Normal maps from height fields"),
         B("3D", "Curl flow-field visualizations"),
         B("3D", "Perlin/simplex noise + gradient (procedural textures)"),
         B("PHYS", "Numerical Gauss's law for a point charge through arbitrary meshes")],
  exam="18.02 final; Cambridge IA Vector Calculus paper",
  units=[
    U("Vectors, matrices, partial derivatives, the gradient", "18.02 lectures 1–12; Feynman Vol. II Ch. 1–3",
      "18.02 psets for lectures 1–12", d=[1, 5]),
    U("Constrained optimization, double integrals, Jacobians", "18.02 lectures 13–20; Tong Vector Calculus: curves, surfaces and volumes",
      "18.02 psets for lectures 13–20; Tong Vector Calculus example sheet 1", d=[2, 4], b=[1]),
    U("Line integrals, grad/div/curl, Green's theorem", "18.02 lectures 21–26; Tong Vector Calculus: grad, div and curl; Nearing Ch. 8–9",
      "18.02 psets for lectures 21–26; Tong Vector Calculus example sheet 2", d=[3], b=[2, 3]),
    U("Surface integrals, Stokes and Gauss", "18.02 lectures 27–35; Tong Vector Calculus: the integral theorems; Nearing Ch. 13",
      "18.02 remaining psets; Tong example sheet 3; exam: 18.02 final + Cambridge IA Vector Calculus paper, timed", b=[4, 5]),
  ])

M("M0.6", "ODEs & dynamical systems", 4, tags=["math"], prereqs=["M0.5"],
  story=["Gleick, Chaos"],
  core=[C("MIT 18.03 (OCW)", url="18.03"),
        C("Strogatz, Nonlinear Dynamics and Chaos", free=False, note="Essential"),
        C("Strogatz, Cornell lectures", note="Free, YouTube")],
  derive=["Picard existence (sketch)", "Linear systems via eigenvalues", "Phase-plane classification", "Linearization",
          "Logistic-map period doubling", "Why RK4 is 4th order (Taylor-match it)"],
  build=[B("3D", "Small physics engine: Verlet, springs (Shiffman, Nature of Code, free)"),
         B("3D", "Small physics engine: constraints, cloth"),
         B("3D", "Small physics engine: rigid bodies with quaternions + angular momentum → Blender/Three.js"),
         B("PHYS", "Double pendulum"),
         B("PHYS", "Lorenz attractor short film"),
         B("PHYS", "Poincaré sections"),
         B("ML", "Neural ODE (a ResNet is an Euler step — derive, then train one)")],
  exam="18.03 final",
  original=["Lorenz 1963"],
  units=[
    U("First-order ODEs, existence, flows on the line", "18.03 lectures 1–8; Strogatz Ch. 1–3",
      "18.03 psets for lectures 1–8; Strogatz Ch. 2–3 exercises (selected)", d=[1, 6]),
    U("Second-order linear ODEs and linear systems", "18.03 lectures 9–19; Strogatz Ch. 5",
      "18.03 psets for lectures 9–19; Strogatz Ch. 5 exercises (selected)", d=[2], b=[1]),
    U("Fourier/Laplace methods; the phase plane and linearization", "18.03 lectures 20–26; Strogatz Ch. 6–7",
      "18.03 psets for lectures 20–26; Strogatz Ch. 6–7 exercises (selected)", d=[3, 4], b=[2, 3, 4]),
    U("Nonlinear systems, chaos, the Lorenz equations", "18.03 lectures 27–33; Strogatz Ch. 8–10; Lorenz 1963",
      "18.03 remaining psets; Strogatz Ch. 9–10 exercises (selected); exam: 18.03 final, timed", d=[5], b=[5, 6, 7]),
  ])

M("M0.7", "Probability & statistics", 5, tags=["math", "ml"], prereqs=["M0.6"],
  story=["Bernstein, Against the Gods", "Mlodinow, The Drunkard's Walk", "McGrayne, The Theory That Would Not Die"],
  core=[C("Blitzstein, Stat 110 (Harvard)", note="Free lectures + free textbook", url="stat110"),
        C("MIT 6.041 (OCW)", note="Alternative to Stat 110", url="6.041"),
        C("Wasserman, All of Statistics", free=False, note="The ML person's stats book")],
  derive=["Bayes", "Weak LLN via Chebyshev", "CLT via MGFs", "MLE = min cross-entropy",
          "Gaussian is max-entropy at fixed variance (stat-mech bridge)", "Metropolis rule satisfies detailed balance"],
  build=[B("3D", "Monte Carlo path tracer (Shirley, Ray Tracing in One Weekend, free)"),
         B("3D", "Path tracer, continued (Physically Based Rendering 4th ed., free at pbr-book.org): importance sampling, Russian roulette, variance vs samples. Rendering is Monte Carlo integration."),
         B("ML", "Bayesian linear regression"),
         B("ML", "Metropolis–Hastings sampler"),
         B("ML", "VI toy with the ELBO derived"),
         B("PHYS", "Random walk → diffusion equation (this is the Ising code of Stage 2)")],
  exam="Stat 110 final (solutions free); 6.041 final",
  original=["Bayes 1763", "Laplace, Philosophical Essay on Probabilities"],
  units=[
    U("Counting, conditional probability, Bayes", "Stat 110 lectures 1–7; Blitzstein & Hwang Ch. 1–2",
      "Stat 110 homework + strategic practice for Ch. 1–2", d=[1]),
    U("Random variables, expectation, continuous distributions", "Stat 110 lectures 8–15; Blitzstein & Hwang Ch. 3–5",
      "Stat 110 homework for Ch. 3–5", d=[5]),
    U("Moments, MGFs, joint distributions, transformations", "Stat 110 lectures 16–23; Blitzstein & Hwang Ch. 6–8",
      "Stat 110 homework for Ch. 6–8", d=[3], b=[1]),
    U("Conditional expectation, inequalities, limit theorems; MLE", "Stat 110 lectures 24–30; Blitzstein & Hwang Ch. 9–10; Wasserman Ch. 9 (parametric inference)",
      "Stat 110 homework for Ch. 9–10; Wasserman Ch. 9 exercises (selected)", d=[2, 4], b=[2, 3]),
    U("Markov chains and MCMC", "Stat 110 lectures 31–35; Blitzstein & Hwang Ch. 11–12",
      "Stat 110 homework for Ch. 11–12; exam: Stat 110 final, timed (then 6.041 final)", d=[6], b=[4, 5, 6]),
  ])

M("M0.8", "Optimization & calculus of variations", 3, tags=["math", "ml"], prereqs=["M0.6"],
  story=["Coopersmith, The Lazy Universe", "The 1696 brachistochrone challenge (MacTutor)"],
  core=[C("Boyd & Vandenberghe, Convex Optimization", note="Ch. 1–5, 9–11", url="cvx"),
        C("Stanford EE364a lectures", url="ee364a"),
        C("Tong, Classical Dynamics Ch. 1", note="For variations", url="tong-cd"),
        C("Gelfand & Fomin", free=False, note="Dover; alternative to Tong for variations")],
  derive=["Convex ⇒ local = global", "GD convergence for L-smooth convex",
          "Adam from first principles, then read the paper", "KKT", "Euler–Lagrange from δS = 0", "Brachistochrone",
          "Geodesics on a sphere (seed of GR)"],
  build=[B("ML", "Optimizer zoo (SGD/momentum/Nesterov/Adam/L-BFGS) on Rosenbrock + a small net"),
         B("3D", "Inverse kinematics for a rig via Jacobian transpose"),
         B("3D", "Constrained ragdoll"),
         B("PHYS", "Fermat's principle solver in a varying refractive index — Snell falls out (lensing preview)")],
  exam="EE364a homeworks; Cambridge IB Variational Principles paper",
  units=[
    U("Convex sets, convex functions, convex problems", "Boyd & Vandenberghe Ch. 1–4; EE364a lectures on the same",
      "EE364a homeworks covering Ch. 2–4", d=[1]),
    U("Duality, KKT, unconstrained minimization", "Boyd & Vandenberghe Ch. 5, 9; EE364a lectures on duality and descent methods",
      "EE364a homeworks covering Ch. 5, 9", d=[2, 3, 4], b=[1]),
    U("Constrained minimization; the calculus of variations", "Boyd & Vandenberghe Ch. 10–11; Tong Classical Dynamics Ch. 1 (or Gelfand & Fomin)",
      "EE364a homeworks covering Ch. 10–11; Tong Classical Dynamics example sheet 1; exam: Cambridge IB Variational Principles paper, timed",
      d=[5, 6, 7], b=[2, 3, 4]),
  ])

M("M0.9", "Fourier analysis & signal processing", 3, tags=["math"], prereqs=["M0.6"],
  story=["Strogatz Ch. 10", "Fourier's intro to Théorie analytique de la chaleur", "Cooley–Tukey story"],
  core=[C("Osgood, Stanford EE261", note="Free lectures + free notes", url="ee261"),
        C("Nearing, Mathematical Tools for Physics", note="Ch. 5, 15", url="nearing")],
  derive=["Series coefficients by orthogonality", "Transform pairs (Gaussian↔Gaussian, box↔sinc)", "Convolution theorem",
          "Sampling theorem", "Uncertainty principle as a theorem about Fourier pairs", "DFT & FFT recursion"],
  build=[B("PROG", "FFT from scratch, benchmarked"),
         B("3D", "JPEG-style DCT compressor with quality slider"),
         B("3D", "Spectrograms"),
         B("3D", "Convolution video effects in frequency space"),
         B("3D", "Tiny denoiser"),
         B("ML", "Conv layer = Fourier multiplication"),
         B("ML", "Sinusoidal positional encodings as Fourier features"),
         B("PHYS", "Heat & wave equations by series"),
         B("PHYS", "Wave packets & dispersion")],
  exam="EE261 psets; MIT 8.03 final (partial)",
  original=["Shannon 1949 sampling paper"],
  units=[
    U("Fourier series", "EE261 lectures 1–10 and the Fourier-series notes; Nearing Ch. 5",
      "EE261 psets for lectures 1–10", d=[1, 2], b=[8]),
    U("Fourier transform, convolution, uncertainty", "EE261 lectures 11–20 and notes; Nearing Ch. 15",
      "EE261 psets for lectures 11–20", d=[3, 5], b=[6, 7, 9]),
    U("Sampling, the DFT and the FFT", "EE261 lectures 21–30 and notes; Shannon 1949",
      "EE261 remaining psets; exam: MIT 8.03 final (Fourier parts), timed", d=[4, 6], b=[1, 2, 3, 4, 5]),
  ])

M("M0.10", "Complex analysis", 3, tags=["math"], prereqs=["M0.6"],
  story=["Nahin, An Imaginary Tale"],
  core=[C("Needham, Visual Complex Analysis", free=False, note="For a visual/film brain, the book"),
        C("Nearing, Mathematical Tools for Physics", note="Ch. 14; free alternative", url="nearing"),
        C("MIT 18.04 (OCW)", note="Free alternative", url="18.04")],
  derive=["Cauchy–Riemann", "Cauchy's theorem & formula", "Residue theorem", "∫dx/(1+x²) and ∫sinx/x by contours",
          "Euler's formula three ways", "Why conformal maps preserve angles"],
  build=[B("3D", "Domain-coloring renderer"),
         B("3D", "Animated Möbius transformations on the Riemann sphere"),
         B("3D", "Joukowski airfoil"),
         B("PHYS", "2D potential flow & electrostatics via conformal maps"),
         B("PHYS", "Kramers–Kronig numerically (causality ↔ analyticity, returns in QFT)")],
  exam="Cambridge IB Complex Methods paper",
  units=[
    U("Complex numbers, functions as maps, analyticity", "Needham Ch. 1–2, 4–5 (or Nearing Ch. 14 first half + 18.04 opening lectures)",
      "Needham Ch. 1–2, 4–5 exercises (or 18.04 early psets)", d=[1, 5, 6], b=[1]),
    U("Möbius maps, winding numbers, Cauchy's theorem and formula", "Needham Ch. 3, 7–9 (or 18.04 integration lectures)",
      "Needham Ch. 3, 7–9 exercises (or 18.04 middle psets)", d=[2, 3], b=[2]),
    U("Residues, contour integrals, flows and harmonic functions", "Needham Ch. 10–12 (or 18.04 residue and conformal-map lectures)",
      "18.04 remaining psets; exam: Cambridge IB Complex Methods paper, timed", d=[4], b=[3, 4, 5]),
  ])

M("M0.11", "Groups, symmetry, abstract algebra", 4, kind="lean", tags=["math"], prereqs=["M0.3"],
  story=["Livio, The Equation That Couldn't Be Solved", "Stewart, Why Beauty Is Truth",
         "Neuenschwander, Emmy Noether's Wonderful Theorem"],
  core=[C("Pinter, A Book of Abstract Algebra", free=False, note="$15, Dover"),
        C("Judson, Abstract Algebra", note="Free alternative to Pinter"),
        C("Zee, Group Theory in a Nutshell", free=False, note="Later, at Stage 3")],
  derive=["Lagrange's theorem", "Cube symmetry group", "SO(2)≅U(1)",
          "SO(3), SU(2) and the 2:1 map (revisit quaternions — now you know what they are)",
          "Why SO(3) irreps are labeled ℓ = 0,1,2,…", "Noether's theorem for a 1D Lagrangian"],
  build=[B("3D", "Platonic solids + rotation-group animation"),
         B("3D", "17 wallpaper-group tiling generator"),
         B("ML", "Read Geometric Deep Learning (Bronstein et al., free arXiv)"),
         B("ML", "Rotation-equivariant CNN on a toy task — symmetry in physics = equivariance in ML"),
         B("PHYS", "Angular-momentum ladder operators from SU(2) commutators"),
         B("CRYPTO", "Revisit EC (it's a group) and AES (GF(2⁸) is a field)")],
  exam="Cambridge IA Groups paper",
  original=["Galois' last letter", "Noether 1918"],
  units=[
    U("Operations, groups, subgroups, permutations", "Pinter Ch. 1–8 (or Judson equivalent)",
      "Pinter Ch. 2–8 exercises (selected)", d=[2]),
    U("Isomorphism, cyclic groups, cosets, Lagrange", "Pinter Ch. 9–13",
      "Pinter Ch. 9–13 exercises (selected)", d=[1, 3], b=[1]),
    U("Homomorphisms, quotients; SO(3), SU(2) and their representations", "Pinter Ch. 14–16; your M0.3 quaternion notes",
      "Pinter Ch. 14–16 exercises (selected)", d=[4, 5], b=[2, 5]),
    U("Rings and fields; symmetry in physics and ML", "Pinter Ch. 17–24 (skim 25–30); Bronstein et al., Geometric Deep Learning",
      "Pinter Ch. 17–22 exercises (selected); exam: Cambridge IA Groups paper, timed", d=[6], b=[3, 4, 6]),
  ])

M("M0.12", "Information theory, inference & the energy-based-model bridge", 4, tags=["math", "ml"], prereqs=["M0.7"],
  story=["Gleick, The Information", "Soni & Goodman, A Mind at Play", "The 2024 physics Nobel (Hopfield, Hinton)"],
  core=[C("MacKay, Information Theory, Inference, and Learning Algorithms", note="Free PDF + free Cambridge lectures — written for exactly your profile", url="mackay"),
        C("Cover & Thomas", free=False, note="Supplement: Ch. 1–5"),
        C("LeCun et al., \"A Tutorial on Energy-Based Learning\" (2006)", note="Supplement"),
        C("LeCun, \"A Path Towards Autonomous Machine Intelligence\" (2022, OpenReview)", note="Supplement — the JEPA paper"),
        C("Assran et al., I-JEPA (arXiv 2301.08243)", note="Supplement", url="ijepa")],
  derive=["Entropy, KL, mutual information", "Source coding theorem (sketch)", "BSC capacity",
          "Boltzmann distribution as max-entropy at fixed mean energy → softmax is Boltzmann, cross-entropy is free energy",
          "Partition function & why it's intractable", "Contrastive divergence", "ELBO",
          "Why JEPA avoids pixel-space reconstruction (in your own words after LeCun 2022)"],
  build=[B("PROG", "Huffman + arithmetic coders"),
         B("PROG", "Entropy of English"),
         B("PROG", "A Hamming/LDPC decoder"),
         B("ML", "Hopfield network (energy landscape animated in 3D — film side)"),
         B("ML", "Boltzmann machine (CD)"),
         B("ML", "Small energy-based model on 2D toy data"),
         B("ML", "Minimal joint-embedding SSL (VICReg-style)"),
         B("ML", "JEPA-style latent predictor on a small image set. Small, finished, documented.")],
  exam="MacKay's ★ and ★★ exercises",
  original=["Shannon 1948 (read all of it)", "Hopfield 1982"],
  notes=["The module that points at your ML project.",
         "Returns: Stage 2 (partition function for spins), Stage 4 (RG ↔ deep learning)."],
  units=[
    U("Entropy, inference, source coding", "MacKay Ch. 1–6 + matching lectures; Cover & Thomas Ch. 1–2",
      "MacKay ★/★★ exercises in Ch. 1–6", d=[1, 2]),
    U("Noisy channels and error-correcting codes", "MacKay Ch. 8–11, 47 + matching lectures; Cover & Thomas Ch. 3–5",
      "MacKay ★/★★ exercises in Ch. 8–11", d=[3], b=[1, 2, 3]),
    U("Boltzmann distribution, Monte Carlo, variational methods, energy-based learning", "MacKay Ch. 29, 31, 33; LeCun et al. 2006",
      "MacKay ★/★★ exercises in Ch. 29, 31, 33", d=[4, 5, 7], b=[4, 5]),
    U("Hopfield, Boltzmann machines, JEPA", "MacKay Ch. 42–43; LeCun 2022; Assran et al. I-JEPA",
      "MacKay ★/★★ exercises in Ch. 42–43; exam: MacKay's ★ and ★★ exercises, timed sitting", d=[6, 8], b=[6, 7, 8]),
  ])

M("M0.13", "Differential geometry of curves & surfaces", 3, tags=["math"], prereqs=["M0.5"],
  story=["Riemann's 1854 lecture \"On the Hypotheses which lie at the Bases of Geometry\" (free, ~20 pp — Einstein's framework in embryo)",
         "MacTutor on Gauss"],
  core=[C("Shifrin, Differential Geometry: Curves and Surfaces", note="Free, UGA", url="shifrin"),
        C("Needham, Visual Differential Geometry and Forms", free=False, note="Optional, extraordinary"),
        C("do Carmo", free=False, note="Standard")],
  derive=["Frenet–Serret", "First & second fundamental forms",
          "Gaussian curvature from the metric alone (Theorema Egregium — what makes GR possible)",
          "Geodesic equation variationally", "Gauss–Bonnet verified on sphere & torus"],
  build=[B("3D", "Curvature-shaded mesh renderer (Blender Python)"),
         B("3D", "Geodesics on a mesh"),
         B("3D", "Subdivision surfaces with limit-surface math"),
         B("PHYS", "Parallel transport on a sphere (holonomy = solid angle — a baby gauge field)"),
         B("PHYS", "Christoffel symbols in SymPy for the 2-sphere and Poincaré disk")],
  exam="Shifrin psets; Cambridge II Differential Geometry paper (parts)",
  units=[
    U("Curves: curvature, torsion, Frenet frame", "Shifrin Ch. 1", "Shifrin Ch. 1 exercises", d=[1]),
    U("Surfaces: fundamental forms, curvature, Theorema Egregium", "Shifrin Ch. 2",
      "Shifrin Ch. 2 exercises", d=[2, 3], b=[1]),
    U("Geodesics, holonomy, Gauss–Bonnet", "Shifrin Ch. 3; Riemann 1854",
      "Shifrin Ch. 3 exercises; exam: Cambridge II Differential Geometry paper (relevant parts), timed", d=[4, 5], b=[2, 3, 4, 5]),
  ])

M("M0.14", "Tensors & multilinear algebra", 2, tags=["math"], prereqs=["M0.13"],
  story=["Einstein's 1912 plea to Grossmann (Pais, Subtle is the Lord)"],
  core=[C("Tong, Vector Calculus", note="Cartesian tensors", url="tong-vc"),
        C("Carroll, GR lecture notes (arXiv gr-qc/9712019)", note="Ch. 1–2", url="carroll"),
        C("Nearing, Mathematical Tools for Physics", note="Ch. 12", url="nearing")],
  derive=["Co/contravariant transformation laws", "Metric raises/lowers",
          "ML \"tensor\" (array) vs physics tensor (multilinear map) and when they coincide",
          "Levi-Civita and the cross product as an antisymmetric rank-2 tensor"],
  build=[B("PROG", "einsum from scratch with broadcasting"),
         B("ML", "Extend M0.4 autograd to rank-n tensors"),
         B("PHYS", "SymPy index-gymnastics checker")],
  exam="Carroll Ch. 1–2 exercises",
  units=[
    U("Cartesian tensors, Levi-Civita", "Tong Vector Calculus: tensors chapter; Nearing Ch. 12",
      "Tong Vector Calculus tensor example sheet; Nearing Ch. 12 problems (selected)", d=[3, 4], b=[1]),
    U("Co/contravariance and the metric", "Carroll notes Ch. 1–2",
      "exam: Carroll Ch. 1–2 exercises, timed and self-graded", d=[1, 2], b=[2, 3]),
  ])

M("M0.15", "Numerical methods & scientific computing", 3, tags=["math", "computing"], prereqs=["M0.6"],
  weeksNote="3 wk focused, then ongoing",
  story=["Dyson, Turing's Cathedral"],
  core=[C("Trefethen & Bau, Numerical Linear Algebra", free=False),
        C("Landau, Páez & Bordeianu, Computational Physics", note="Free web edition"),
        C("Newman, Computational Physics", free=False)],
  derive=["FP error bounds", "Conditioning vs stability", "Why elimination needs pivoting", "Power-iteration convergence",
          "Stability regions of Euler/RK/symplectic (why your engine explodes)", "CFL condition"],
  build=[B("PROG PHYS", "Numerical toolbox v2: LU/QR/SVD"),
         B("PROG PHYS", "Numerical toolbox v2: Lanczos"),
         B("PROG PHYS", "Numerical toolbox v2: FFT"),
         B("PROG PHYS", "Numerical toolbox v2: symplectic integrators"),
         B("PROG PHYS", "Numerical toolbox v2: finite-difference solver for heat/wave/Schrödinger"),
         B("ML", "GPU versions of two toolbox routines (CuPy or Triton)")],
  exam="The toolbox is the exam",
  units=[
    U("Floating point, conditioning, stability, LU and QR", "Trefethen & Bau Lectures 1–23",
      "Trefethen & Bau exercises from Lectures 12–23 (selected)", d=[1, 2, 3], b=[1]),
    U("Eigenvalue algorithms and iterative methods", "Trefethen & Bau Lectures 24–28, 32–36",
      "Trefethen & Bau exercises from Lectures 24–36 (selected)", d=[4], b=[2, 3]),
    U("ODE and PDE integrators", "Newman Ch. 8–9 (or Landau, Páez & Bordeianu ODE/PDE chapters)",
      "Newman Ch. 8–9 exercises (selected); exam: the toolbox passes its own test suite", d=[5, 6], b=[4, 5, 6]),
  ])

# =====================================================================
# STAGE 1 (5 wk each)
# =====================================================================
M("M1.1", "Classical mechanics I", 5, prereqs=["M0.15", "M0.12"],
  core=[C("MIT 8.01 (OCW)", url="8.01"),
        C("Feynman Lectures Vol. I", note="Ch. 1–20", url="feyn1"),
        C("OpenStax, University Physics Vol. 1", note="For extra problems", url="osp1")],
  build=[B("PHYS", "Projectile with drag"),
         B("PHYS", "Orbits under 1/r² — verify Kepler numerically")],
  exam="8.01 final",
  units=[
    U("Kinematics in one and two dimensions", "8.01 weeks 1–2; Feynman Vol. I Ch. 1–8",
      "8.01 problem sets for weeks 1–2; OpenStax Vol. 1 Ch. 2–4 problems (selected)"),
    U("Newton's laws, forces, circular motion", "8.01 weeks 3–4; Feynman Vol. I Ch. 9–12",
      "8.01 problem sets for weeks 3–4; OpenStax Vol. 1 Ch. 5–6 problems (selected)", b=[1]),
    U("Energy, momentum, collisions", "8.01 weeks 5–8; Feynman Vol. I Ch. 13–14",
      "8.01 problem sets for weeks 5–8; OpenStax Vol. 1 Ch. 7–9 problems (selected)"),
    U("Rotation and angular momentum", "8.01 weeks 9–12; Feynman Vol. I Ch. 18–20",
      "8.01 problem sets for weeks 9–12; OpenStax Vol. 1 Ch. 10–11 problems (selected)"),
    U("Gravitation, orbits, oscillations", "8.01 weeks 13–14; Feynman Vol. I Ch. 7, 15–17",
      "8.01 remaining problem sets; OpenStax Vol. 1 Ch. 13–15 problems (selected); exam: 8.01 final, timed, closed-book", b=[2]),
  ])

M("M1.2", "Special relativity", 5, prereqs=["M1.1"],
  core=[C("Tong, Dynamics & Relativity", note="Ch. 7", url="tong-dr"),
        C("MIT 8.033 (OCW)", url="8.033"),
        C("Susskind, Theoretical Minimum: Special Relativity", url="tm")],
  build=[B("PHYS 3D", "Lorentz-boost event sets"),
         B("PHYS 3D", "Programmatic spacetime diagrams"),
         B("PHYS 3D", "Twin paradox with accelerated frames — animated")],
  exam="8.033 midterm",
  original=["Einstein 1905, \"On the Electrodynamics of Moving Bodies\" (free at fourmilab.ch). Read after the module — it's short and you'll follow all of it."],
  checkpoint="Re-read your 2021 paper. Rewrite its central claim with 4-vectors and the Lorentz group. Check whether \"time flows at c, relative velocity c − v\" yields γ = 1/√(1−v²/c²) without the λ fudge factor. Write up the answer either way. Killing your own idea rigorously is the most physicist thing you can do.",
  units=[
    U("Postulates and Lorentz transformations", "Tong D&R Ch. 7 (Lorentz transformations); 8.033 opening lectures; Susskind SR lectures 1–2",
      "8.033 first problem set; Tong D&R Ch. 7 examples"),
    U("Time dilation, length contraction, spacetime diagrams", "Tong D&R Ch. 7 (kinematics); 8.033 lectures on kinematics",
      "8.033 second problem set", b=[1, 2]),
    U("Four-vectors and the Lorentz group", "Tong D&R Ch. 7 (four-vectors); 8.033 lectures on four-vectors; Susskind SR lectures 3–4",
      "8.033 third problem set"),
    U("Relativistic dynamics, collisions, accelerated frames", "Tong D&R Ch. 7 (relativistic particles); 8.033 lectures on dynamics",
      "8.033 fourth problem set", b=[3]),
    U("Review; the 2021-paper checkpoint", "Your 2021 paper; Einstein 1905 (after the exam)",
      "Personal checkpoint write-up; exam: 8.033 midterm, timed"),
  ])

M("M1.3", "Electricity & magnetism I", 5, prereqs=["M1.2"],
  core=[C("MIT 8.02 (OCW)", url="8.02"),
        C("Feynman Lectures Vol. II", note="Ch. 1–15", url="feyn2")],
  build=[B("PHYS", "Laplace by relaxation"),
         B("PHYS", "Field plots of charge configurations")],
  exam="8.02 final",
  original=["Maxwell 1865, \"A Dynamical Theory of the Electromagnetic Field\" (free)"],
  units=[
    U("Electric fields and Gauss's law", "8.02 lectures on charge, fields, Gauss's law; Feynman Vol. II Ch. 1–5",
      "8.02 problem sets for these lectures", b=[2]),
    U("Potential, conductors, capacitors, dielectrics", "8.02 lectures on potential and capacitance; Feynman Vol. II Ch. 6–12",
      "8.02 problem sets for these lectures", b=[1]),
    U("Current, circuits, magnetic fields", "8.02 lectures on current, DC circuits, magnetostatics; Feynman Vol. II Ch. 13–14",
      "8.02 problem sets for these lectures"),
    U("Induction and the vector potential", "8.02 lectures on Faraday's law and inductance; Feynman Vol. II Ch. 15",
      "8.02 problem sets for these lectures"),
    U("Maxwell's equations and EM waves", "8.02 lectures on displacement current and EM waves",
      "8.02 remaining problem sets; exam: 8.02 final, timed, closed-book"),
  ])

M("M1.4", "Waves & vibrations", 5, prereqs=["M1.3"],
  core=[C("MIT 8.03 (Yen-Jie Lee, OCW)", url="8.03")],
  build=[B("PHYS 3D", "Coupled oscillators → normal modes → continuum string"),
         B("PHYS 3D", "Wave-optics simulator: diffraction & interference rendered (film line)")],
  exam="8.03 final",
  units=[
    U("Free, damped and driven oscillators", "8.03 lectures 1–4", "8.03 psets 1–2"),
    U("Coupled oscillators and normal modes", "8.03 lectures 5–8", "8.03 psets 3–4", b=[1]),
    U("Waves on strings and the continuum limit", "8.03 lectures 9–13", "8.03 psets 5–6"),
    U("EM waves, dispersion, wave packets", "8.03 lectures 14–18", "8.03 psets 7–8"),
    U("Interference and diffraction", "8.03 lectures 19–23", "8.03 psets 9–10; exam: 8.03 final, timed", b=[2]),
  ])

M("M1.5", "Intro thermodynamics", 5, prereqs=["M1.4"],
  core=[C("OpenStax, University Physics Vol. 2", note="Ch. 1–4", url="osp2"),
        C("Feynman Lectures Vol. I", note="Ch. 39–46", url="feyn1")],
  build=[B("PHYS", "Hard-sphere molecular dynamics; watch Maxwell–Boltzmann emerge")],
  exam=None,
  units=[
    U("Temperature, heat, kinetic theory of gases", "OpenStax Vol. 2 Ch. 1–2; Feynman Vol. I Ch. 39–40",
      "OpenStax Vol. 2 Ch. 1–2 problems (selected)"),
    U("The first law", "OpenStax Vol. 2 Ch. 3; Feynman Vol. I Ch. 41–42",
      "OpenStax Vol. 2 Ch. 3 problems (selected)", b=[1]),
    U("The second law, entropy, heat engines", "OpenStax Vol. 2 Ch. 4; Feynman Vol. I Ch. 44",
      "OpenStax Vol. 2 Ch. 4 problems (selected)"),
    U("Diffusion, ratchets, laws of thermodynamics in depth", "Feynman Vol. I Ch. 43, 45–46",
      "Remaining OpenStax Vol. 2 Ch. 1–4 problems; a home-experiment lab report (C3)"),
    U("Review and Stage 1 consolidation", "Your notebook: re-derive one result from each Stage 1 module",
      "Mixed review problems; exam: none listed for this module — attempt a Cambridge NST IA Physics paper (Milestone M1)"),
  ])

# =====================================================================
# STAGE 2 (6 wk each)
# =====================================================================
M("M2.1", "Classical mechanics II — Lagrangian & Hamiltonian", 6, prereqs=["M1.5"],
  core=[C("Tong, Classical Dynamics", url="tong-cd"),
        C("Taylor, Classical Mechanics", free=False, note="Ch. 6–13, best problems"),
        C("Susskind, Theoretical Minimum: Classical Mechanics", note="Free alternative to Taylor", url="tm")],
  build=[B("PHYS", "Double pendulum chaos"),
         B("PHYS", "Liouville's theorem via phase-space ensembles")],
  exam="Cambridge IB Classical Dynamics paper; MIT 8.223",
  units=[
    U("Calculus of variations and Lagrange's equations", "Tong Classical Dynamics Ch. 1–2 (first half); Taylor Ch. 6–7",
      "Taylor Ch. 6–7 problems (selected); Tong Classical Dynamics example sheet 1"),
    U("Symmetries, Noether, central forces", "Tong Classical Dynamics Ch. 2 (rest); Taylor Ch. 8",
      "Taylor Ch. 8 problems (selected); Tong example sheet 2"),
    U("Non-inertial frames and rigid bodies", "Tong Classical Dynamics Ch. 3; Taylor Ch. 9–10",
      "Taylor Ch. 9–10 problems (selected); Tong example sheet 3"),
    U("Small oscillations and nonlinear dynamics", "Taylor Ch. 11–12",
      "Taylor Ch. 11–12 problems (selected)", b=[1]),
    U("Hamilton's equations, phase space, Liouville", "Tong Classical Dynamics Ch. 4 (first half); Taylor Ch. 13",
      "Taylor Ch. 13 problems (selected); Tong example sheet 4", b=[2]),
    U("Poisson brackets, canonical transformations; review", "Tong Classical Dynamics Ch. 4 (rest)",
      "MIT 8.223 problem sets; exam: Cambridge IB Classical Dynamics paper, timed"),
  ])

M("M2.2", "Electrodynamics", 6, prereqs=["M2.1"],
  core=[C("Griffiths, Introduction to Electrodynamics", free=False, note="Ch. 1–12. Buy it; no free equivalent matches the problems"),
        C("Tong, Electromagnetism", note="Free alternative, with Feynman Vol. II", url="tong-em"),
        C("Feynman Lectures Vol. II", url="feyn2")],
  build=[B("PHYS", "FDTD EM wave hitting a dielectric"),
         B("PHYS", "Radiation from an accelerating charge")],
  exam="MIT 8.07 finals",
  units=[
    U("Vector analysis and electrostatics", "Griffiths Ch. 1–2", "Griffiths Ch. 1–2 problems (selected)"),
    U("Potentials; electric fields in matter", "Griffiths Ch. 3–4", "Griffiths Ch. 3–4 problems (selected)"),
    U("Magnetostatics; magnetic fields in matter", "Griffiths Ch. 5–6", "Griffiths Ch. 5–6 problems (selected)"),
    U("Electrodynamics and conservation laws", "Griffiths Ch. 7–8", "Griffiths Ch. 7–8 problems (selected)"),
    U("EM waves; potentials and fields", "Griffiths Ch. 9–10", "Griffiths Ch. 9–10 problems (selected)", b=[1]),
    U("Radiation; electrodynamics and relativity", "Griffiths Ch. 11–12",
      "Griffiths Ch. 11–12 problems (selected); exam: MIT 8.07 final, timed", b=[2]),
  ])

M("M2.3", "Quantum mechanics I", 6, prereqs=["M2.2"],
  core=[C("MIT 8.04 (Zwiebach/Adams, OCW)", url="8.04"),
        C("Griffiths, Introduction to Quantum Mechanics", free=False, note="Ch. 1–4"),
        C("Tong, Quantum Mechanics", note="Free alternative to Griffiths", url="tong-qm")],
  build=[B("PHYS 3D", "Time-dependent Schrödinger via split-operator"),
         B("PHYS 3D", "Tunneling"),
         B("PHYS 3D", "Wavepacket scattering films")],
  exam="8.04 final",
  units=[
    U("The wavefunction and its interpretation", "8.04 opening lectures; Griffiths Ch. 1",
      "Griffiths Ch. 1 problems (selected); 8.04 psets for these lectures"),
    U("Stationary states: infinite well, harmonic oscillator", "Griffiths Ch. 2 (first half); 8.04 matching lectures",
      "Griffiths Ch. 2 problems, first half (selected); 8.04 psets", b=[1]),
    U("Free particle, delta and finite wells, 1D scattering", "Griffiths Ch. 2 (second half); 8.04 matching lectures",
      "Griffiths Ch. 2 problems, second half (selected); 8.04 psets", b=[2]),
    U("Formalism: Hilbert space, observables, uncertainty", "Griffiths Ch. 3; Tong QM Ch. 1 (just-in-time math)",
      "Griffiths Ch. 3 problems (selected); 8.04 psets"),
    U("QM in three dimensions: angular momentum, hydrogen", "Griffiths Ch. 4 (first half); 8.04 matching lectures",
      "Griffiths Ch. 4 problems, first half (selected); 8.04 psets", b=[3]),
    U("Spin; review", "Griffiths Ch. 4 (rest)",
      "Griffiths Ch. 4 problems, second half (selected); exam: 8.04 final, timed"),
  ])

M("M2.4", "Quantum mechanics II", 6, prereqs=["M2.3"],
  core=[C("MIT 8.05 (Zwiebach)", url="8.05"),
        C("Griffiths, Introduction to Quantum Mechanics", free=False, note="Ch. 5–11")],
  build=[B("PHYS", "Hydrogen radial equation diagonalized"),
         B("PHYS", "Zeeman splitting"),
         B("PHYS", "Spin-½ in a B field")],
  exam="8.05 final",
  units=[
    U("Vector spaces, operators, Dirac notation", "8.05 lectures on linear algebra and Dirac notation",
      "8.05 psets for these lectures"),
    U("Spin-½ and two-state systems", "8.05 lectures on spin and two-state systems",
      "8.05 psets for these lectures", b=[3]),
    U("Coherent states; identical particles", "8.05 lectures on the harmonic oscillator and coherent states; Griffiths Ch. 5",
      "8.05 psets; Griffiths Ch. 5 problems (selected)"),
    U("Angular momentum and its addition; time-independent perturbation theory", "8.05 angular-momentum lectures; Griffiths Ch. 6 (perturbation theory)",
      "8.05 psets; Griffiths perturbation-theory problems (selected)", b=[1]),
    U("Fine structure, Zeeman effect; variational principle and WKB", "Griffiths Ch. 7–8 (variational, WKB)",
      "Griffiths Ch. 7–8 problems (selected)", b=[2]),
    U("Time-dependent perturbation theory and scattering", "Griffiths Ch. 9–11",
      "Griffiths Ch. 9–11 problems (selected); exam: 8.05 final, timed"),
  ])

M("M2.5", "Statistical mechanics", 6, tags=["physics", "ml"], prereqs=["M2.4"],
  core=[C("Tong, Statistical Physics", url="tong-sp"),
        C("MIT 8.044 (OCW)", url="8.044")],
  build=[B("PHYS ML", "2D Ising model, Metropolis Monte Carlo"),
         B("PHYS ML", "Find T_c"),
         B("PHYS ML", "Measure critical exponents"),
         B("PHYS ML", "Animate the phase transition (film line)"),
         B("PHYS ML", "Essay: the Ising sampler is a Boltzmann machine — connect to M0.12")],
  exam="8.044 final; Cambridge IB Thermodynamics paper",
  units=[
    U("Microcanonical and canonical ensembles", "Tong Statistical Physics: fundamentals; 8.044 lectures on ensembles",
      "Tong Statistical Physics example sheet 1; 8.044 psets"),
    U("Classical gases", "Tong Statistical Physics: classical gases",
      "Tong example sheet 2; 8.044 psets"),
    U("Quantum gases", "Tong Statistical Physics: quantum gases",
      "Tong example sheet 3; 8.044 psets", b=[1]),
    U("Classical thermodynamics", "Tong Statistical Physics: classical thermodynamics; 8.044 thermodynamics lectures",
      "Tong example sheet 4; Cambridge IB Thermodynamics past questions", b=[2]),
    U("Phase transitions and the Ising model", "Tong Statistical Physics: phase transitions",
      "Tong example sheet 5", b=[3, 4]),
    U("Ising ↔ Boltzmann machine; review", "MacKay Ch. 31 and 43 (revisit from M0.12)",
      "8.044 review problems; exam: 8.044 final + Cambridge IB Thermodynamics paper, timed", b=[5]),
  ])

M("M2.6", "Math methods II", 6, tags=["math", "physics"], prereqs=["M2.5"],
  core=[C("Nearing, Mathematical Tools for Physics", note="Ch. 8–17 (Green's functions, PDEs, intro group theory)", url="nearing"),
        C("Tong, Methods-adjacent notes")],
  build=[B("PHYS", "Green's function of the Poisson equation numerically")],
  exam="Cambridge IB Methods paper",
  units=[
    U("Multivariable and vector calculus revisited; PDEs", "Nearing Ch. 8–10", "Nearing Ch. 8–10 problems (selected)"),
    U("Numerical analysis; tensors", "Nearing Ch. 11–12", "Nearing Ch. 11–12 problems (selected)"),
    U("Vector calculus II; complex variables", "Nearing Ch. 13–14", "Nearing Ch. 13–14 problems (selected)"),
    U("Fourier analysis", "Nearing Ch. 15", "Nearing Ch. 15 problems (selected)"),
    U("Calculus of variations; densities and distributions; Green's functions", "Nearing Ch. 16–17",
      "Nearing Ch. 16–17 problems (selected)", b=[1]),
    U("Review: Cambridge IB Methods", "Cambridge IB Methods past papers",
      "IB Methods past questions; a Physics GRE practice test (Milestone M2); exam: Cambridge IB Methods paper, timed"),
  ])

# =====================================================================
# STAGE 3 (6 wk each)
# =====================================================================
M("M3.1", "Quantum mechanics III", 6, prereqs=["M2.6"],
  core=[C("MIT 8.06 (Zwiebach)", url="8.06"),
        C("Sakurai & Napolitano, Modern Quantum Mechanics", free=False, note="Ch. 1–5")],
  build=[B("PHYS", "Perturbation theory vs exact numerically"),
         B("PHYS", "Scattering phase shifts")],
  exam="8.06 final",
  units=[
    U("Fundamental concepts", "Sakurai Ch. 1", "Sakurai Ch. 1 problems (selected)"),
    U("Quantum dynamics and path integrals", "Sakurai Ch. 2", "Sakurai Ch. 2 problems (selected)"),
    U("Theory of angular momentum", "Sakurai Ch. 3", "Sakurai Ch. 3 problems (selected)"),
    U("Symmetry in quantum mechanics", "Sakurai Ch. 4; 8.06 perturbation-theory lectures",
      "Sakurai Ch. 4 problems (selected); 8.06 psets", b=[1]),
    U("Approximation methods: perturbation theory, WKB, adiabatic", "Sakurai Ch. 5; 8.06 matching lectures",
      "Sakurai Ch. 5 problems (selected); 8.06 psets"),
    U("Scattering", "8.06 scattering lectures",
      "8.06 remaining psets; exam: 8.06 final, timed", b=[2]),
  ])

M("M3.2", "General relativity I", 6, prereqs=["M3.1"],
  core=[C("Carroll, GR lecture notes (arXiv gr-qc/9712019)", note="Ch. 1–5", url="carroll"),
        C("MIT 8.962 (Scott Hughes, OCW)", note="Full video", url="8.962"),
        C("Susskind, Theoretical Minimum: General Relativity", url="tm")],
  build=[B("PHYS 3D", "Geodesics in Schwarzschild"),
         B("PHYS 3D", "Perihelion precession"),
         B("PHYS 3D", "Black-hole ray tracer reproducing the Interstellar paper — the film line's capstone")],
  exam="8.962 final",
  units=[
    U("Special relativity and flat spacetime", "Carroll Ch. 1; 8.962 opening lectures", "Carroll Ch. 1 exercises; 8.962 psets"),
    U("Manifolds", "Carroll Ch. 2; 8.962 matching lectures", "Carroll Ch. 2 exercises; 8.962 psets"),
    U("Curvature", "Carroll Ch. 3; 8.962 matching lectures", "Carroll Ch. 3 exercises; 8.962 psets"),
    U("Gravitation and Einstein's equation", "Carroll Ch. 4; 8.962 matching lectures", "Carroll Ch. 4 exercises; 8.962 psets"),
    U("The Schwarzschild solution", "Carroll Ch. 5; 8.962 matching lectures",
      "Carroll Ch. 5 exercises; 8.962 psets", b=[1, 2]),
    U("Black holes and ray tracing; review", "8.962 black-hole lectures; James et al., Interstellar paper (arXiv 1502.03808)",
      "8.962 remaining psets; exam: 8.962 final, timed", b=[3]),
  ])

M("M3.3", "Solid state / condensed matter", 6, prereqs=["M3.2"],
  core=[C("Tong, Solid State", url="tong-ss"),
        C("Steve Simon, Oxford solid-state lectures", note="Free, YouTube")],
  build=[B("PHYS", "Tight-binding band structure of graphene")],
  exam="Oxford Part B Condensed Matter paper",
  units=[
    U("Particles in a box; free electrons", "Tong Solid State: opening chapter; Simon's matching lectures", "Tong Solid State example sheet 1"),
    U("Lattices and reciprocal space", "Tong Solid State: lattices; Simon's matching lectures", "Tong example sheet 2"),
    U("Band structure and tight binding", "Tong Solid State: band structure; Simon's matching lectures", "Tong example sheet 3", b=[1]),
    U("Electron dynamics in solids", "Tong Solid State: electron dynamics; Simon's matching lectures", "Tong example sheet 4"),
    U("Phonons", "Tong Solid State: phonons; Simon's matching lectures", "Tong example sheet 5"),
    U("Magnetism; review", "Tong Solid State: remaining chapters",
      "Oxford Part B Condensed Matter past questions; exam: Oxford Part B Condensed Matter paper, timed"),
  ])

M("M3.4", "Particle & nuclear physics (survey)", 6, prereqs=["M3.3"],
  core=[C("Tong, Particle Physics", url="tong-pp"),
        C("Griffiths, Introduction to Elementary Particles", free=False, note="Alternative to Tong")],
  build=[B("PHYS", "CERN Open Data: reconstruct the Z peak from dimuon events")],
  exam=None,
  units=[
    U("Particles, dynamics, relativistic kinematics", "Griffiths EP Ch. 1–3 (or Tong Particle Physics opening sections)", "Griffiths EP Ch. 3 problems (selected)"),
    U("Symmetries and bound states", "Griffiths EP Ch. 4–5", "Griffiths EP Ch. 4–5 problems (selected)"),
    U("Feynman calculus and QED", "Griffiths EP Ch. 6–7", "Griffiths EP Ch. 6–7 problems (selected)"),
    U("Quarks, hadrons, QCD", "Griffiths EP Ch. 8–9", "Griffiths EP Ch. 8–9 problems (selected)", b=[1]),
    U("Weak interactions and gauge theories", "Griffiths EP Ch. 10–11", "Griffiths EP Ch. 10–11 problems (selected)"),
    U("Neutrinos, nuclear physics; review", "Griffiths EP Ch. 12; Tong Particle Physics nuclear sections",
      "Mixed review problems; exam: none listed for this module — self-set a timed paper from Griffiths EP problems"),
  ])

M("M3.5", "Astrophysics & cosmology", 6, prereqs=["M3.4"],
  core=[C("Tong, Cosmology", url="tong-cosmo"),
        C("Susskind, Theoretical Minimum: Cosmology", url="tm"),
        C("Ryden, Introduction to Cosmology", free=False, note="Optional")],
  build=[B("PHYS", "Friedmann equations"),
         B("PHYS", "Fit supernova data for Ω_Λ"),
         B("PHYS", "CMB power spectrum from Planck data")],
  exam="Cambridge II Cosmology paper",
  units=[
    U("The expanding universe", "Tong Cosmology: expanding universe; Ryden Ch. 1–3; Hubble 1929", "Tong Cosmology example sheet 1"),
    U("Cosmic dynamics and the Friedmann equations", "Tong Cosmology: Friedmann equations; Ryden Ch. 4–5", "Tong example sheet 2", b=[1]),
    U("Measuring cosmological parameters", "Ryden Ch. 6; Susskind Cosmology matching lectures", "Ryden Ch. 6 problems (selected)", b=[2]),
    U("Dark matter and the CMB", "Tong Cosmology: the hot universe; Ryden Ch. 7–8; Penzias–Wilson 1965", "Tong example sheet 3"),
    U("Nucleosynthesis and inflation", "Ryden Ch. 9–10; Tong Cosmology matching sections", "Ryden Ch. 9–10 problems (selected)", b=[3]),
    U("Structure formation; review", "Tong Cosmology: structure formation; Ryden Ch. 11–12",
      "Tong example sheet 4; exam: Cambridge II Cosmology paper, timed"),
  ])

M("M3.6", "Computational physics (formal)", 6, tags=["physics", "computing"], prereqs=["M3.5"],
  core=[C("Landau, Páez & Bordeianu, Computational Physics", note="Free web edition"),
        C("Newman, Computational Physics", free=False, note="Alternative")],
  build=[B("PHYS PROG", "Spectral methods — level up the toolbox", inferred=True),
         B("PHYS PROG", "Variational methods — level up the toolbox", inferred=True),
         B("PHYS PROG", "Finite element — level up the toolbox", inferred=True)],
  exam=None,
  units=[
    U("Integrals, derivatives, linear and nonlinear equations", "Newman Ch. 5–6 (or Landau/Páez/Bordeianu equivalents)", "Newman Ch. 5–6 exercises (selected)"),
    U("Fourier transforms and spectral methods", "Newman Ch. 7 and the spectral-methods section of Ch. 9", "Newman Ch. 7 exercises (selected)", b=[1]),
    U("ODEs and PDEs", "Newman Ch. 8–9", "Newman Ch. 8–9 exercises (selected)"),
    U("Random processes and Monte Carlo", "Newman Ch. 10", "Newman Ch. 10 exercises (selected)"),
    U("Variational methods", "Landau/Páez/Bordeianu chapters on variational and eigenvalue methods", "Variational-method problems from Landau/Páez/Bordeianu (selected)", b=[2]),
    U("Finite elements; review", "Landau/Páez/Bordeianu finite-element chapter",
      "Finite-element problems (selected); exam: none listed for this module — the toolbox upgrade is the check; sit a published PhD qualifying exam (Milestone M3)", b=[3]),
  ])

# =====================================================================
# STAGE 4 (7 wk each)
# =====================================================================
M("M4.1", "Quantum field theory I", 7, prereqs=["M3.6"],
  core=[C("Tong, QFT", url="tong-qft"),
        C("PSI QFT I (PIRSA)", url="pirsa"),
        C("Srednicki, QFT (free draft, author's site)", note="Ch. 1–30", url="srednicki"),
        C("Peskin & Schroeder", free=False, note="Part I; the lingua franca")],
  build=[B("PHYS 3D", "Lattice φ⁴ in 2D by Monte Carlo"),
         B("PHYS 3D", "Measure the mass gap"),
         B("PHYS 3D", "Visualize field configurations")],
  exam="Cambridge Part III QFT paper",
  units=[
    U("Classical field theory, Lorentz invariance", "Tong QFT Ch. 1; Srednicki Ch. 1–2; PSI QFT I opening lectures", "Tong QFT example sheet 1"),
    U("Canonical quantization of free fields", "Tong QFT Ch. 2; Srednicki Ch. 3–4; Peskin & Schroeder Ch. 2", "Tong example sheet 1 (rest); Peskin & Schroeder Ch. 2 problems"),
    U("Interacting fields, LSZ, Feynman diagrams", "Tong QFT Ch. 3; Srednicki Ch. 5, 9–10; Peskin & Schroeder Ch. 4", "Tong example sheet 2; Peskin & Schroeder Ch. 4 problems", b=[1]),
    U("Path integrals, propagators, cross sections", "Srednicki Ch. 6–8, 11–12; PSI QFT I matching lectures", "Srednicki problems for Ch. 6–12 (selected)", b=[2]),
    U("The Dirac equation and the Dirac field", "Tong QFT Ch. 4–5; Peskin & Schroeder Ch. 3", "Tong example sheet 3; Peskin & Schroeder Ch. 3 problems"),
    U("QED; loops and renormalization", "Tong QFT Ch. 6; Peskin & Schroeder Ch. 5; Srednicki Ch. 14–20", "Tong example sheet 4; Peskin & Schroeder Ch. 5 problems", b=[3]),
    U("Renormalization group and symmetries; review", "Srednicki Ch. 21–30; PSI QFT I closing lectures",
      "Part III QFT past papers; exam: Cambridge Part III QFT paper, timed"),
  ])

M("M4.2", "Quantum field theory II", 7, prereqs=["M4.1"],
  core=[C("Tong, Gauge Theory", url="tong-gauge"),
        C("Peskin & Schroeder", free=False, note="Parts II–III"),
        C("Schwartz", free=False, note="Optional")],
  build=[B("PHYS", "Tree-level cross section symbolically (SymPy/FeynCalc) vs PDG")],
  exam="Part III Advanced QFT / Standard Model papers",
  units=[
    U("Systematics of renormalization", "Peskin & Schroeder Ch. 10", "Peskin & Schroeder Ch. 10 problems"),
    U("Renormalization and symmetry; the renormalization group", "Peskin & Schroeder Ch. 11–12", "Peskin & Schroeder Ch. 11–12 problems"),
    U("Non-abelian gauge theory", "Peskin & Schroeder Ch. 15–16; Tong Gauge Theory: Yang–Mills", "Peskin & Schroeder Ch. 15–16 problems"),
    U("QCD", "Peskin & Schroeder Ch. 17–18", "Peskin & Schroeder Ch. 17 problems", b=[1]),
    U("Anomalies", "Peskin & Schroeder Ch. 19; Tong Gauge Theory: anomalies", "Peskin & Schroeder Ch. 19 problems"),
    U("Spontaneously broken gauge theories", "Peskin & Schroeder Ch. 20–21", "Peskin & Schroeder Ch. 20–21 problems"),
    U("The Standard Model; review", "Tong Gauge Theory remaining chapters; Schwartz Standard Model chapters (optional)",
      "Part III Advanced QFT / Standard Model past papers; exam: Part III Advanced QFT or Standard Model paper, timed"),
  ])

M("M4.3", "General relativity II", 7, prereqs=["M4.2"],
  core=[C("Wald", free=False, note="The standard"),
        C("Carroll, Spacetime and Geometry (full book)", free=False, note="Alternative to Wald"),
        C("PSI GR lectures (PIRSA)", url="pirsa")],
  build=[B("PHYS", "Evolve a simple spacetime numerically (1+1D spherically symmetric scalar collapse)")],
  exam="Part III GR paper",
  units=[
    U("Manifolds, tensor fields, curvature", "Wald Ch. 1–3; PSI GR opening lectures", "Wald Ch. 2–3 problems"),
    U("Einstein's equation", "Wald Ch. 4", "Wald Ch. 4 problems"),
    U("Cosmology and the Schwarzschild solution", "Wald Ch. 5–6", "Wald Ch. 5–6 problems"),
    U("Stationary axisymmetric spacetimes; Kerr", "Wald Ch. 7 (or Carroll Ch. 6)", "Wald Ch. 7 problems"),
    U("Causal structure and singularities", "Wald Ch. 8–9", "Wald Ch. 8–9 problems"),
    U("The initial value formulation", "Wald Ch. 10", "Wald Ch. 10 problems", b=[1]),
    U("Asymptotic flatness, charged and rotating black holes; review", "Wald Ch. 11–12; PSI GR closing lectures",
      "Part III GR past papers; exam: Part III GR paper, timed"),
  ])

M("M4.4", "Statistical field theory & RG", 7, tags=["physics", "ml"], prereqs=["M4.3"],
  core=[C("Tong, Statistical Field Theory", url="tong-sft"),
        C("Kardar, MIT 8.334 (OCW)", note="Video", url="8.334")],
  build=[B("PHYS ML", "Real-space RG on Ising"),
         B("PHYS ML", "Compute ν vs your Stage 2 Monte Carlo"),
         B("PHYS ML", "Animate RG flow"),
         B("PHYS ML", "Write the RG ↔ deep learning essay — the ML line's capstone")],
  exam="Part III Statistical Field Theory paper",
  units=[
    U("Phase transitions and Landau theory", "Tong SFT opening chapter; 8.334 opening lectures", "Tong SFT example sheet 1"),
    U("Fluctuations and Landau–Ginzburg", "Tong SFT: Landau–Ginzburg; 8.334 matching lectures", "Tong example sheet 2; 8.334 psets"),
    U("Scaling hypothesis", "8.334 scaling lectures; Tong SFT matching sections", "8.334 psets"),
    U("Perturbative RG and the ε-expansion", "Tong SFT: the renormalisation group; 8.334 matching lectures", "Tong example sheet 3; 8.334 psets"),
    U("Position-space RG", "8.334 position-space RG lectures", "8.334 psets", b=[1, 2]),
    U("Continuous symmetries, the XY model, Kosterlitz–Thouless", "Tong SFT closing chapters; 8.334 matching lectures", "Tong example sheet 4", b=[3]),
    U("RG ↔ deep learning; review", "Mehta & Schwab 2014 (arXiv)",
      "Part III SFT past papers; exam: Part III Statistical Field Theory paper, timed", b=[4]),
  ])

M("M4.5", "Quantum information", 7, tags=["physics", "crypto"], prereqs=["M4.4"],
  core=[C("Preskill, Ph219 notes", url="preskill"),
        C("PSI quantum information course (PIRSA)", url="pirsa")],
  build=[B("PHYS CRYPTO", "Small quantum-circuit simulator"),
         B("PHYS CRYPTO", "Shor for n=15"),
         B("PHYS CRYPTO", "Bell violation numerically"),
         B("PHYS CRYPTO", "A toy lattice-based (Kyber-style) scheme — crypto line closed")],
  exam=None,
  units=[
    U("Introduction; states and ensembles", "Preskill Ch. 1–2", "Preskill Ch. 2 problems"),
    U("Measurement and evolution", "Preskill Ch. 3", "Preskill Ch. 3 problems"),
    U("Quantum entanglement", "Preskill Ch. 4; Bell 1964", "Preskill Ch. 4 problems", b=[3]),
    U("Classical and quantum circuits", "Preskill Ch. 5", "Preskill Ch. 5 problems", b=[1]),
    U("Quantum algorithms", "Preskill Ch. 6; Shor 1994", "Preskill Ch. 6 problems", b=[2]),
    U("Quantum error correction", "Preskill Ch. 7", "Preskill Ch. 7 problems"),
    U("Quantum Shannon theory; lattice crypto", "Preskill Ch. 10; PSI course closing lectures",
      "Preskill Ch. 10 problems; exam: none listed for this module — self-set a timed paper from Preskill problems", b=[4]),
  ])

M("M4.6", "Advanced math", 7, tags=["math", "physics"], prereqs=["M4.5"],
  core=[C("Nakahara, Geometry, Topology and Physics", free=False),
        C("Lie groups (Tong-adjacent notes)")],
  exam="Part III Symmetries, Fields & Particles paper",
  units=[
    U("Mathematical preliminaries and homology", "Nakahara Ch. 2–3", "Nakahara Ch. 2–3 problems"),
    U("Homotopy groups", "Nakahara Ch. 4", "Nakahara Ch. 4 problems"),
    U("Manifolds and de Rham cohomology", "Nakahara Ch. 5–6", "Nakahara Ch. 5–6 problems"),
    U("Riemannian geometry", "Nakahara Ch. 7", "Nakahara Ch. 7 problems"),
    U("Lie groups and Lie algebras", "Lie groups (Tong-adjacent notes)", "Exercises from the Lie-group notes"),
    U("Fibre bundles and connections", "Nakahara Ch. 9–10", "Nakahara Ch. 9–10 problems"),
    U("Characteristic classes; review", "Nakahara Ch. 11",
      "Part III Symmetries, Fields & Particles past papers; exam: Part III Symmetries, Fields & Particles paper, timed"),
  ])

M("M4.7", "Electives (pick 2–3)", 7, prereqs=["M4.6"],
  core=[C("Tong, String Theory", url="tong-string"),
        C("Bilal, Supersymmetry (arXiv)", url="bilal"),
        C("Baumann, Cosmology", note="Free, Cambridge"),
        C("Townsend, Black Holes (arXiv)", url="townsend"),
        C("AdS/CFT via TASI lectures (arXiv)")],
  exam=None,
  notes=["Pick 2–3 electives."],
  units=[
    U("Elective A, part 1", "First third of your first elective", "Problems from the elective's notes"),
    U("Elective A, part 2", "Second third of your first elective", "Problems from the elective's notes"),
    U("Elective A, part 3", "Final third of your first elective", "Problems from the elective's notes"),
    U("Elective B, part 1", "First third of your second elective", "Problems from the elective's notes"),
    U("Elective B, part 2", "Second third of your second elective", "Problems from the elective's notes"),
    U("Elective B, part 3", "Final third of your second elective", "Problems from the elective's notes"),
    U("Optional third elective, or start the thesis-scale project", "Third elective (optional) or the M4 capstone reading",
      "Problems from the elective's notes; exam: none listed for this module — Milestone M4 asks for two Part III papers at merit level"),
  ])

# =====================================================================
# Part A
# =====================================================================
RULES = [
    "Problems are the course. Videos and reading prepare you for problems. A module is done when the problem sets are done. Three lectures ahead of your last problem set → stop, go back.",
    "Every module ends with a timed, closed-book exam from a real university. Pass = 65% (70% for math, you have more hours). Fail → redo weak topics, sit a different paper. This rule is what makes the whole thing real.",
    "Every stage ends with a capstone in a public repo. That repo is your transcript.",
    "Every overlap project (3D, ML, crypto) is a lab attached to a physics or math module, finishable in 1–3 weekends. No engines, no frameworks. Small, finished, shipped.",
    "Crypto is one module, then a hobby. ML and 3D get more room because they share math with the spine.",
    "Story before, original paper after. Read the history before each module (motivation); read one original paper after it (proof you can follow it).",
    "Research notebook from day one. Derivations, confusions, open questions. One derivation per day, even on bad days.",
    "Don't jump ahead. The most common self-study death is watching QFT/GR lectures with undergrad math. The fun stuff is Stage 3+. The ticket is Stages 0–2.",
    "Two-week rule. Miss two weeks → don't restart the module. Re-derive one thing from the notebook, do one problem. Re-entry is the whole game.",
    "Never end a session without knowing the next problem. \"Do 4.7\" survives a bad week; \"continue chapter 4\" doesn't.",
]

S0_IDS = [f"M0.{i}" for i in range(1, 16)]


def stage_ids(n):
    return [m["id"] for m in MODULES if m["stageId"] == f"S{n}"]


MILESTONES = [
    ("M0.a", "Foundations + crypto", "Hammack done; RSA/ECC/AES repo; Cryptopals set 3", ["M0.1", "M0.2"], None),
    ("M0.b", "Linear algebra + calculus", "18.06 & 18.01 finals ≥ 70%; software rasterizer; autodiff engine", ["M0.3", "M0.4"], None),
    ("M0.c", "Multivariable + ODEs", "18.02 & 18.03 finals; physics engine; Lorenz short film", ["M0.5", "M0.6"], None),
    ("M0.d", "Probability + optimization + Fourier", "Stat 110 final; path tracer; Adam derived by hand; FFT; video compressor", ["M0.7", "M0.8", "M0.9"], None),
    ("M0.e", "Complex + groups", "Cambridge IB Complex Methods & IA Groups papers; domain-coloring films; equivariant CNN", ["M0.10", "M0.11"], None),
    ("M0.f", "Info theory/EBM + geometry + tensors + numerics", "MacKay ★★ exercises; Hopfield→Boltzmann→JEPA sequence; curvature renderer; numerical toolbox v2", ["M0.12", "M0.13", "M0.14", "M0.15"], None),
    ("M0", "Ready for physics", "All above public + 15 \"what I learned\" essays", S0_IDS,
     "All builds public + 15 short \"what I learned\" essays. Audit against 't Hooft's list through \"Classical Mechanics.\""),
    ("M1", "First year", "8.01/8.02/8.03 finals; 3 lab reports; N-body capstone; 2021 paper rewritten with 4-vectors", stage_ids(1),
     "8.01/8.02/8.03 finals; attempt a Cambridge NST IA Physics paper; 3 lab reports; capstone: N-body gravity simulator (Barnes–Hut or direct) with a writeup on energy conservation vs integrator; 2021-paper rewrite."),
    ("M2", "Physics-degree level", "Physics GRE practice ≥ 700 (800 = mastery); 8.04/8.05/8.07/8.044 finals; Ising paper in LaTeX", stage_ids(2),
     "Physics GRE practice test ≥ 700 (800 = mastery); 8.04/8.05/8.07/8.044 finals; capstone: Ising project as a proper paper (LaTeX — learn it now; abstract, figures, references). Your first publication-shaped object."),
    ("M3", "Grad-school ready", "A published PhD qualifying exam passed; black-hole ray tracer (Interstellar paper) or GW detection capstone; 't Hooft audit", stage_ids(3),
     "Pass a published PhD qualifying exam (Columbia, Princeton publish solutions); capstone: the black-hole ray tracer, or matched-filter detection of GW150914 from GWOSC data recovering its parameters, or reproduce a figure from a recent arXiv paper with a report; 't Hooft audit through \"QFT.\""),
    ("M4", "Master's", "Two Cambridge Part III papers at merit; thesis-scale project (30–60 pp) public", stage_ids(4),
     "Two Part III papers at what you honestly judge merit level (typically QFT + GR or QFT + SFT); capstone: a master's-thesis-scale project (30–60 pp, LaTeX) — a numerical study of a known model with one small novel twist, or a review with your own derivations. Post to arXiv (needs endorsement — see C6) or GitHub + ResearchGate."),
    ("M5", "Researcher", "arXiv submission, or admission to a funded programme, or an active collaboration", [],
     "Stage 5 — research apprenticeship (B5): converts M4 into a position or an independent research life. Research taste: by Stage 3, pick a question, not a field."),
]

STAGES = [
    dict(id="S0", number=0, title="Expanded mathematics spine", durationMonths="8–11",
         intro="Modules in dependency order; M0.7–M0.10 can overlap.",
         storyShelf=["Strogatz, Infinite Powers — read it in week one; it's the \"why\" of this entire stage"]),
    dict(id="S1", number=1, title="Core physics I (first year)", durationMonths="5–7",
         storyShelf=["Weinberg, To Explain the World", "Galileo, Dialogues (public domain, funny)",
                     "Forbes & Mahon, Faraday, Maxwell, and the Electromagnetic Field",
                     "Pais, Subtle is the Lord (technical Einstein bio) or Isaacson, Einstein (popular)",
                     "Video: Feynman, The Character of Physical Law (free, YouTube) — all seven"],
         practicals=["Three home experiments written up as lab reports (see C3)"]),
    dict(id="S2", number=2, title="Core physics II (second year)", durationMonths="7–9",
         intro="This is where math and physics fuse, and where most self-learners quit. Plan for it.",
         storyShelf=["Coopersmith, The Lazy Universe (action principles)", "Feynman Vol. II Ch. 19 (least action, free)",
                     "Lindley, Boltzmann's Atom", "Cercignani, Ludwig Boltzmann",
                     "Kumar, Quantum (Bohr–Einstein debate — best QM history)", "Baggott, The Quantum Story",
                     "Lindley, Uncertainty", "Farmelo, The Strangest Man (Dirac — read at end of stage)"],
         originals=["van der Waerden (ed.), Sources of Quantum Mechanics (Dover: Heisenberg 1925, Born–Jordan, Dirac 1925)",
                    "Schrödinger 1926 (free translations)", "Noether 1918"],
         justInTimeMath=["Hilbert spaces & Hermitian operators (Tong QM Ch. 1; Axler revisited) — ML kernel methods/RKHS are Hilbert-space methods"]),
    dict(id="S3", number=3, title="Advanced undergraduate", durationMonths="7–9",
         storyShelf=["Ferreira, The Perfect Theory (a century of GR)", "Thorne, Black Holes and Time Warps",
                     "Einstein, Relativity: The Special and General Theory (free, public domain, written for the public)",
                     "Crease & Mann, The Second Creation (building the Standard Model)", "Close, The Infinity Puzzle",
                     "Singh, Big Bang", "Weinberg, The First Three Minutes",
                     "Film side: James, von Tunzelmann, Franklin & Thorne, \"Gravitational Lensing by Spinning Black Holes… in the Movie Interstellar\" (arXiv 1502.03808)"],
         originals=["Einstein 1915/16 field-equation papers", "Yang–Mills 1954", "Hubble 1929", "Penzias–Wilson 1965 (one page)"],
         justInTimeMath=["Manifolds, forms, Lie derivatives, connections (Carroll Ch. 2–3; Needham VDGF; Baez & Muniain, Gauge Fields, Knots and Gravity $)",
                         "Lie algebras & reps of SU(2), SU(3), Lorentz group (Zee, Group Theory in a Nutshell $; Tong) — ML equivariant nets over Lie groups"]),
    dict(id="S4", number=4, title="Master's level (Cambridge Part III / Perimeter PSI)", durationMonths="9–14",
         intro="You now watch actual master's courses (PIRSA has every PSI lecture, free) and sit actual master's exams (Part III past papers, free).",
         storyShelf=["Feynman, QED: The Strange Theory of Light and Matter", "Schweber, QED and the Men Who Made It (technical history)",
                     "Gleick, Genius", "Kaiser, Drawing Theories Apart (how Feynman diagrams spread)",
                     "Hossenfelder, Lost in Math (the critics — read all three so you enter with eyes open)",
                     "Smolin, The Trouble with Physics (the critics)", "Woit, Not Even Wrong (the critics)"],
         originals=["Dirac 1928", "Feynman 1949", "Bell 1964 (one of the great short papers)", "Shor 1994"],
         justInTimeMath=["Functional integrals, Grassmann variables, distributions (Tong QFT; Srednicki)",
                         "Renormalization group (Kardar 8.334; Tong SFT)",
                         "ML: Score-based/diffusion models are Langevin dynamics (Song et al. 2021); RG ↔ deep learning (Mehta & Schwab 2014, arXiv) — a live frontier sitting exactly on your two interests"]),
]


def weeks(n):
    return sum(m["weeks"] for m in MODULES if m["stageId"] == f"S{n}")


NOTES = [
    "Stage 0 weeks come from the \"(N wk)\" in each module heading (M0.15 is \"3 wk focused, then ongoing\" → 3). Stage 0 total: %d weeks; the 8–11 month range assumes M0.7–M0.10 overlap." % weeks(0),
    "Stage 1 (5–7 months, 5 modules): midpoint ~6 months ≈ 26 weeks → 5 weeks per module, %d weeks total." % weeks(1),
    "Stage 2 (7–9 months, 6 modules): midpoint ~8 months ≈ 35 weeks → 6 weeks per module, %d weeks total." % weeks(2),
    "Stage 3 (7–9 months, 6 modules): midpoint ~8 months ≈ 35 weeks → 6 weeks per module, %d weeks total." % weeks(3),
    "Stage 4 (9–14 months, 7 modules incl. electives): midpoint ~11.5 months ≈ 50 weeks → 7 weeks per module, %d weeks total; M4.7 covers 2 electives at 3 weeks each plus an optional third / thesis start." % weeks(4),
    "Stage 1–4 modules have no Derive lists in the source, so their derive arrays are empty; the derivation of the day for those modules comes from the week's input.",
    "Modules with no exam in the source (M1.5, M3.4, M3.6, M4.5, M4.7) carry exam.listed = false; their last unit names the nearest stand-in (milestone paper or self-set paper).",
    "Builds tagged with several lines (e.g. PHYS + 3D) list all tags in 'lines'; 'line' is the first tag. M3.6 builds have no tag in the source and are tagged PHYS/PROG (lineInferred).",
    "Unit week splits, chapter/lecture ranges per week and problem-set assignments are inferred from the Core resources; the source does not give them.",
    "Stage 5 (research apprenticeship) has no modules and is represented only by milestone M5.",
]


def build():
    stages = []
    for s in STAGES:
        s = dict(s)
        s["modules"] = [m for m in MODULES if m["stageId"] == s["id"]]
        stages.append(s)
    return {
        "version": 1,
        "source": "theoretical-physics-master-curriculum.md",
        "weeklyHoursTarget": 20,
        "dailyMinutesTarget": 180,
        "minimumDay": {"derivations": 1, "problems": 1, "log": True},
        "notes": NOTES,
        "rules": RULES,
        "milestones": [dict({"id": i, "title": t, "proof": p, "moduleIds": ids}, **({"detail": d} if d else {}))
                       for i, t, p, ids, d in MILESTONES],
        "stages": stages,
    }


if __name__ == "__main__":
    out = sys.argv[1]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(), f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", out)
