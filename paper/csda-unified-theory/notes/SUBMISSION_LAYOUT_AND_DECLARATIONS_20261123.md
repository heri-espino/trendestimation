# CSDA two-column layout and journal-disclosure handoff — 2026-11-23

## Scope
Editorial/layout-only continuation of PR #160. No theorem, derivation,
data value, figure generator, statistical algorithm, or benchmark input
was changed. Do not submit the manuscript to a journal as part of this
workflow; the user authorized a GitHub merge after verification, not a
publisher submission.

## User-reported problem and resolution
The user showed right/left-column text running into the margins.
The earlier verified PDF had 17 TeX overfull hbox messages. The CAS
template also emits an intrinsic, non-paragraph overfull-box message
during title/abstract construction; this is **not** evidence of body
text overflowing. A local source-only rehearsal with
`microtype`, `emergencystretch=2.5em`, and controlled paragraph
tolerances eliminated all prose `Overfull \\hbox ... in paragraph`
messages. `verify_layout.py` fails the authoritative Action if a
paragraph exceeds 0.5 pt. The existing `rotate_landscape_tables.py`
continues to enforce native landscape orientation on both algorithm
tables, and representative PDF pages must be inspected visually.

The code example uses LaTeX `listings` without shell escape, in a
bounded, breakable, two-column `vscodeLightPython` style inspired
by Visual Studio Code's Light+ colors: blue keywords, reddish
strings, brown callables, green comments and a light grey border.
Only the display formatting and optional wrapping of code changed;
the `select_lambda` and `fit` operations are unchanged.

## Responsible disclosures
Dedicated sections at the **end of the manuscript before references**:
1. Data and code availability (repository, specific synthetic/figure assets).
2. Funding (**unconfirmed**, do not invent 'none').
3. CRediT authorship contribution statement (**unconfirmed roles**).
4. Declaration of competing interests (**unconfirmed**, no declaration of 'none').
5. Ethics statement (the stated synthetic study involves no participants/animals).
6. Declaration of generative AI and AI-assisted technologies (ChatGPT,
   language, literature, LaTeX and code-presentation support).

The authors must review these declarations, verify any additional
research-related AI-assisted code generation and describe such
assistance under the computational methodology if appropriate,
confirm roles/funding/conflicts, and provide the journal's
**separate** competing-interest form if requested at submission.

The disclosure policy was checked on 2026-11-23 against:
- Elsevier AI journals policy:
  https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
  (name the tool and use; statement immediately before references;
  human authors must independently verify all output; distinguish
  editorial assistance from AI-assisted scientific methods).
- Elsevier Editorial Manager submission guide:
  https://www.elsevier.support/publishing/answer/author-guide-to-editorial-managers-new-submission-experience
  (manuscript and separate competing-interest declaration file
  mandatory; other declarations may depend on journal).
- Elsevier general author guide:
  https://www.elsevier.com/subject/next/guide-for-authors
  (data statements, CRediT, competing interests, funding).

The CSDA-specific final submission interface may impose additional
fields. Nothing in this pass implies a completed authorship or
institutional sign-off.

## Reproduction
Run the original numerical and editorial unit tests:
```bash
python paper/csda-unified-theory/verify_theory.py
python paper/csda-computational-costs/verify_theory.py
python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v
```
The existing dedicated CSDA workflow performs the Elsevier CAS
source-only compile, bibliography checks, figure reproduction,
landscape rotations, `python verify_layout.py main.log`, and
artifact/hash archival. Evaluate the compiled PDF visually, including
the Python listing page, both landscape tables and all disclosure pages.
Do not use the local rehearsal PDF (which may have a stand-in
bibliography) as the final source-of-truth build.

## Remaining pre-submission gates
- Confirm each author's CRediT roles, affiliation, funding and conflicts.
- Confirm the AI-use statement against authors' complete research workflow.
- Verify exact commit and repository access, publish an immutable archive if desired.
- Independently inspect the final compiled manuscript and complete the
  journal's competing-interest and funding fields.
- Author/coauthor approval, and explicit journal-submission authorization.
