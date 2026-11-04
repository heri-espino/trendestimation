# Experiment005 AI-agent handoff

Read \`paper/benchmarks/experiment005/README.md\` first, then
\`notes/experiment004_s_accuracy_and_computation.md\` and the
two CSDA paper folders. This experiment is **independent** and must
not mutate existing paper tables or older measurements.

- Branch: \`experiment005/joint-accuracy-runtime\`
- Main implementation: \`run_joint.py\`.
- Reused Experiment004 functions: \`run_pilot.truth/noise\`,
  \`verify_stable_solvers.observations\`,
  \`verify_bic_precision.precise_dual_banded\`.
- Existing backend criterion implementation:
  \`paper/benchmarks/full_s_backend_criteria.py\`.
- Existing fit implementation:
  \`src/trendestimation/solvers.py\`.

Time the exact returned fit, then compare against the independent
85-digit fixed-input reference. Scores are evaluated by the actual
backend and validated after timing; do not borrow reference scores for
timed method rankings. Analytic endpoints are separately marked.
Avoid mixing a restricted-BIC winner with unrestricted BIC.

Do not claim that equal S grid and log-lambda grid are comparable
statistical candidate sets. Do not identify any backend as fastest
unless every eligible candidate and selected fit is numerically
admissible. Manual full preset is deferred until the pilot has been
reviewed. Do not run jobs on PCAG103A-08 implicitly. Retain
all raw outputs, scripts, logs, manifests and figures in the branch.
