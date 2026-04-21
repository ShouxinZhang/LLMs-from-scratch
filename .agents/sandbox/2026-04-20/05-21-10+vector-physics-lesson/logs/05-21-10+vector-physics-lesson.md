# Task Log

- User request: use `zero-base-qa-tutor-zh`, start `sandbox-workmode`, explain ``What is a vector?'' and its theoretical applications in physics, use TeX, build a PDF, and write the document in English.
- Workspace: `.agents/sandbox/2026-04-20/05-21-10+vector-physics-lesson/`
- Actions:
  - Read the three relevant skill files.
  - Created an isolated sandbox directory with `output/`, `build/`, `logs/`, and `tmp/`.
  - Wrote an initial English LaTeX lesson using the zero-base QA structure.
  - Added a local build script that compiles with `latexmk -xelatex`.
  - Rewrote the lesson from scratch for a middle-school beginner after user feedback.
  - Added explicit boxed environments for `Problem`, `Intuition`, `Definition`, `Theorem`, `Solution`, and `Proof`.
  - Rewrote the exposition again around the user's own wording: velocity as `5 m/s` plus direction, coordinate-plane intuition, and a gentler textbook tone.
  - Added a TikZ figure showing a vector as the arrow from the origin to a point `(a,b)`.
  - Switched the geometry-style figures to `tkz-euclide` instead of hand-drawing every axis and marker.
  - Added several missing diagrams: coordinate picture, length/right-triangle picture, vector addition picture, velocity-direction picture, and force decomposition picture.
  - Rebuilt the PDF successfully and verified the generated file metadata.
