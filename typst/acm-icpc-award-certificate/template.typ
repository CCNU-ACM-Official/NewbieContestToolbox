#let award-certificate(
  contest-title: "2025 CCNU Collegiate Programming Contest",
  contest-subtitle: "Modeled after classic ACM-ICPC award certificates",
  award-title: "Gold Medal",
  team-name: "Team Example",
  recipients: ("Alice", "Bob", "Carol"),
  citation: "for outstanding performance in the contest finals",
  rank-line: "Rank 1 of 148 teams",
  organizer: "School of Computer Science, Central China Normal University",
  host: "Central China Normal University",
  city-line: "Wuhan, China",
  date-line: "March 21, 2026",
  chair-name: "Contest Director",
  coach-name: "Chief Judge",
  logo-path: none,
) = {
  let paper = rgb("#fbf7ef")
  let border = rgb("#c39b4d")
  let accent = rgb("#8f1d2c")
  let ink = rgb("#30251b")
  let soft = rgb("#7d6751")

  set page(width: 297mm, height: 210mm, margin: 0mm)

  set text(font: ("Times New Roman", "Source Han Serif", "STSong", "SimSun", "Liberation Serif"), fill: ink, lang: "en")

  box(width: 100%, height: 100%, fill: paper, inset: 10mm, [
    #box(width: 100%, height: 100%, stroke: (paint: border, thickness: 1.6pt), inset: 5mm, [
      #box(width: 100%, height: 100%, stroke: (paint: border, thickness: 0.7pt), inset: (x: 12mm, y: 10mm), [
        #align(center)[
          #if logo-path != none [
            #image(logo-path, height: 18mm)
            #v(3mm)
          ]
          #text(size: 23pt, weight: "bold")[2025 华中师范大学菜鸟杯程序设计竞赛]
          #v(1mm)
          #text(size: 23pt, weight: "bold", tracking: 1.2pt, fill: accent)[获奖证书]
          #v(2.5mm)
          #text(size: 36pt, weight: "bold")[#team-name]
          #v(2.5mm)
          #text(size: 19pt, weight: "bold", fill: accent)[#award-title]
        ]
        #v(1fr)

        #align(center)[
          #text(size: 20pt, fill: soft)[华中师范大学ACM协会]
          #v(1.5mm)
          #linebreak()
          #text(size: 18pt, fill: soft)[#date-line]
        ]
      ])
    ])
  ])
}
