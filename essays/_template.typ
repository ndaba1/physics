// Essay template. Copy to essays/<ModuleDir>/<slug>.typ, e.g. essays/M0_1/what-i-learned.typ,
// and import it:  #import "../_template.typ": essay
// Four sections, always: claim, derivation, what confused me, what it connects to.

#let essay(title: "", module: "", date: none, body) = {
  set document(title: title, author: "Victor Ndaba")
  set page(paper: "a4", margin: 2.2cm, numbering: "1")
  set text(size: 11pt)
  set par(justify: true)
  set heading(numbering: "1.")
  set math.equation(numbering: "(1)")

  align(center)[
    #text(size: 16pt, weight: "bold")[#title] \
    #text(fill: luma(90))[#module#if date != none [ · #date.display("[year]-[month]-[day]")]]
  ]
  v(1em)
  body
}
