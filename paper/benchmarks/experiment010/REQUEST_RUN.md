# Experiment010 explicit university-runner request 002

Trigger: rerun bounded smoke and pilot on PCAG103A-08 using the
corrected experimental MLE score normalization. This MUST produce a
new immutable results branch with a new GitHub run ID. The original
run #41586066141 remains unchanged and is marked pre-correction.

Protocol: paper/benchmarks/experiment010/README.md.
Fix/audit: notes/experiment010_mle_normalization_audit.md.
Prerequisites: corrected score parity and determinant regression tests;
no university VM environment installation.

This request launches the bounded smoke (30 method-case attempts) and
pilot (60 method-case attempts), NOT the entire feasible 50,400-case
tensor. Further independent shards are needed. Do not treat timings
from different source SHAs as directly interchangeable without the
normalization and numerical-certificate audit.
