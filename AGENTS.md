# Repository working agreement

This is Active Cloud Guard, an Honors research prototype. The user explicitly requires strict documentation and preservation of the existing architecture. The supplied web-product workflow is a documentation reference, not a request to migrate stacks.

Before a change, read `docs/INDEX.md`, `docs/MEMORY.md`, `TASKS.md`, `RULES.md`, and the documents relevant to the task. Inspect actual code and evidence; documentation is not proof that a command passed.

For each substantive change:

1. Identify the task and acceptance criteria. Keep scope within the user's request.
2. Preserve Python, Docker Compose, Ollama, Chroma and the existing research boundaries unless the user authorizes an architecture change.
3. Implement and run relevant checks. Record exact commands, outcomes and limitations.
4. Update `docs/WORK_LOG.md`, `docs/MEMORY.md`, `TASKS.md` and `CHANGELOG.md` in the same commit. Update architecture, test plan and security documents when their content changes.
5. Add an incident entry for a failure worth preserving. Record symptom, evidence, cause confidence, fix, verification and remaining limits. Record material decisions in `docs/DECISIONS.md`.
6. Preserve negative experimental results. Never replace historical evidence while claiming it is unchanged, invent executions, backdate work or call development data an independent benchmark.
7. Before committing, run the repository documentation/publication checker and inspect staged files. Never stage credentials, environments, model weights or generated vector databases.
8. Commit coherent changes with descriptive messages when the user's scope authorizes version-control work. Push only to the intended remote, and verify the remote commit afterward. Do not rewrite shared history to hide failures.

Evidence levels: **implemented**, **unit-tested**, **live-observed**, **independently evaluated** are different. A model candidate is not a verified vulnerability. A rejected candidate is an abstention, not a clean verdict.

No autonomous future monitoring or scheduled changes are implied by this file. Apply this maintenance contract whenever work is performed in this repository.
