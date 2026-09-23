# Evidence index

These files are observations, not marketing claims. Timestamps in JSON are UTC; work occurred on 2026-09-23 in Asia/Calcutta. Original reports can contain local file paths. Repository visibility is private.

| ID | Artifact | What it establishes / limit |
|---|---|---|
| EV-001 | source/Honors_Research_1st_Monitoring_Deck.pdf | Original proposal, not proof of implementation |
| EV-002 | ../data/labels.json and development/ fixtures | Seeded development expectations and hashes; not independent ground truth |
| EV-003 | ../output/test-results.xml | Saved software-test outcomes; latest snapshot may be refreshed after relevant code checks |
| EV-004 | ../output/baseline-development.json | 45 exact-rule comparisons and repeated scanner timing; no generalization claim |
| EV-005 | ../output/live-testbed.json | Four local TCP observations and two HTTP checks at recorded time |
| EV-006 | ../output/pipeline-demo.json | Rule candidate linked to explicit staging endpoint and provisional score |
| EV-007 | ../output/rag-smoke-initial-failures.json | Initial 1.5B schema failure summaries; earliest malformed response bodies were not saved |
| EV-008 | ../output/rag-smoke-ungrounded-candidates.json | Unsupported 1.5B model candidates despite schema-valid output |
| EV-009 | ../output/rag-smoke-3b-before-policy-guard.json | 3B unsupported trust-authentication claim before narrow guard |
| EV-010 | ../output/rag-smoke.json | Final three-case candidates, rejections and timing; tuned development data |
| EV-011 | ../output/vector-smoke.json | Actual vector index, source checks and one model audit |
| EV-012 | ../output/trivy-baseline.json | Per-fixture established-tool observations and exclusions; policy scope differs |
| EV-013 | ../output/integrated-demo.json | Full vector-RAG, explicit probe and priority path executed |
| EV-014 | ../output/environment.json | Historical dependency/image/model identities and hashes for files then present |
| EV-015 | ../output/RESEARCH_STATUS.md | Generated interpretation of the saved reports, not an additional experiment |
| EV-016 | ../output/test-results-initial-84.xml | Preserved original 84-test snapshot before three repository-check tests were added |

The historical environment snapshot is not a manifest of documentation added later. Git identifies the complete committed snapshot. Do not regenerate historical experiment output merely to refresh documentation dates.

## Evidence preservation

For a changed experiment, preserve the earlier report under a descriptive revision name or rely on an already committed version, then record the new run's date, command, inputs, software/model identities and changed conditions. Keep failures, exclusions and abstentions. Never claim a mock-based unit test is a live inference run. Derived summaries must identify their source reports.
