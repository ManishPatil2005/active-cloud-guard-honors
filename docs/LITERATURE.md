# Source and claim audit

## 11 October 2026 - Closest-work expansion (QA-024/M1-003)

Targeted primary-source search, not a systematic review or demonstrated novelty. Queries: `site.arxiv.org cloud misconfiguration retrieval augmented generation security infrastructure as code` and `site.arxiv.org infrastructure as code misconfiguration large language models detection evaluation`. Included container misconfiguration repair, active cloud validation and layered IaC security validation; generation-only/agent red-teaming records are contextual, not equivalent detector baselines. Search-result metrics are not accepted evidence. No datasets/code downloaded, installed or executed; implementation/replication licenses remain unreviewed.

| Primary paper / access level | Relevant prior contribution | Consequence for Active Cloud Guard |
|---|---|---|
| [LLMSecConfig, Ye/Le/Babar, arXiv2502.02009v1](https://arxiv.org/html/2502.02009v1), abstract/method/data-availability sections | Checkov-guided Kubernetes repair with scanner output, policy source and documentation context; iterative scanner validation; links a Figshare package | Combining static analysis, LLMs and RAG is prior work, not our novelty. Repair endpoint differs from investigation prioritization; compare common detection scope separately, not repair rates against our recall |
| [Alert or Noise?, Dikshant/Verma, arXiv2508.12584v1](https://arxiv.org/html/2508.12584v1), methodology/classification inspected | Active AWS behavioral verification, TP/FP/inconclusive outcomes; excludes inconclusive probes from precision/recall | Active validation is prior work. Retain our full unknown/abstention denominator and compare matched supported claims; cannot treat TCP refusal as disproving every finding or transfer headline results |
| [TerraProbe, Alsaid/Nebolisa/Abbas, arXiv2606.26590v1](https://arxiv.org/html/2606.26590v1), abstract/oracle/corpus/provenance/replication sections | Layered scanner/structure/plan/comparison validation, track separation, hashes and human adjudication; first-pass repair and no cloud apply | Layered evidence/provenance alone is not an established new contribution. Independent replication and comparable units still required; do not introduce Terraform repair or cloud credentials into our scope |

Additional primary abstract checks: [Shaw, Compared to What?, arXiv2608.28021v2](https://arxiv.org/abs/2608.28021) emphasizes size matching and prompt-class confounding in generated-IaC comparisons; not a runtime detector baseline. [Yang et al., arXiv2606.31227v1](https://arxiv.org/abs/2606.31227) has title **Securing the AI Agent: A Unified Framework for Multi-Layer Agent Red Teaming** and describes AI-Infra-Guard; record that exact title rather than treating the framework name as the paper title. Both abstract-level only, no reproduced claims. SSRN5271734 again returned an internal error and IEEE10965635 yielded no usable methods; access failures remain pending, not completed full-text reviews. Earlier September audit below is historical.

Candidate contribution, explicitly an inference/hypothesis: measure whether scoped runtime evidence improves investigation prioritization beyond static plus retrieval/verification under independent labels, complete abstention accounting and qualified capture lineage, at acceptable cost. This preserves existing architecture and does not assert first-of-kind or performance. Required falsification: matched static-only/retrieval/verification/runtime ablations, grouped held-out data, calibration on training/validation only, false negatives and unknowns retained, independent human review and comparable measured acquisition/model overhead. No current independent dataset or real-data fitting approval satisfies those conditions. A negative effect is a valid research outcome. Closest baseline implementation/version/license review and broader full-text coverage still remain open.

Checked 23 September 2026. Verification levels describe evidence actually accessed; existence of a paper does not validate its methods.

| Reference in deck | Evidence checked | Disposition |
|---|---|---|
| Goyal & Chaturvedi, Detecting Cloud Misconfigurations with RAG and Intelligent Agents | Primary SSRN abstract confirms authors/title; publisher search result lists J. Electrical Systems 20-11s (2024), 2558-2570. SSRN gives date written 19 January 2025. Publisher download returned a verification challenge. | Title is abbreviated in deck; include subtitle 'A Natural Language Understanding Approach'. Resolve 2024/2025 bibliographic discrepancy before thesis submission. Full-text SARGE methods and DOI resolution not independently verified here. |
| Dikshant & Verma, arXiv:2508.12584 | arXiv abstract and full HTML accessed. | Related active validation work exists. The 'later performance venue publication' in the deck remains unverified; cite the arXiv version. |
| Bajracharya, Kubernetes threat detection | Publisher endpoint returned HTTP 403. | Full-text methods and performance remain unverified in this audit; do not use its metrics as validated targets. |
| Yang et al., arXiv:2606.31227 | Primary arXiv abstract accessed. | Related AI-infrastructure security framework exists, but its agent/MCP scope differs from this OSS configuration testbed. No evidence of this project's novelty follows from that difference alone. |

Sources: [Goyal and Chaturvedi manuscript record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5271734); [publisher endpoint](https://journal.esrgroups.org/jes/article/download/7882/5370/14426); [active validation abstract](https://arxiv.org/abs/2508.12584); [active validation full text](https://arxiv.org/html/2508.12584v1); [Kubernetes article endpoint](https://ijsrcseit.com/home/article/view/CSEIT2612318); [AI-Infra-Guard abstract](https://arxiv.org/abs/2606.31227).

## Important check on the active-validation result

The paper reports roughly 93% fewer false positives in AWS experiments. This is a prior-work claim, not transferable performance. Table 3's alert rows sum to 3,500; its FP counts sum to 2,940 before and 180 after, giving 93.8776% reduction. Its first two row percentages differ slightly from direct arithmetic. Table 4 lists TP=360, FP=180, TN=2960 and recall=.911 but no FN; these counts cannot be reconciled directly with 3,500 total cases and that recall. The method also excludes inconclusive probes from precision/recall. These issues warrant reproduction and clarification rather than treating the headline number as a project guarantee.

## Knowledge-base design

knowledge/sources.json contains nine short, author-written summaries tied to official documentation URLs and review dates. They are not copied CIS benchmark text, a comprehensive NVD snapshot, or a full security corpus. Licensing and source revision checks are required before expanding the corpus. Source membership checks are implemented; automatic entailment verification is not.

Lexical retrieval is the first reproducible comparison baseline. The implemented Chroma index uses local nomic-embed-text embeddings; the collection identity includes both the source hash and embedding-model digest. Functional source retrieval checks are recorded separately from model results. ChromaDB itself is not proof of semantic retrieval quality. [Chroma documentation](https://docs.trychroma.com/docs/embeddings/embedding-functions) and [Ollama embeddings API](https://docs.ollama.com/api/embed) guided the integration.

## Literature work still requiring human research

Expand the search beyond the four deck references, record queries/inclusion/exclusion decisions, read full primary papers, inspect repositories and licenses, and independently reproduce the closest baseline. Professor review should judge the contribution using the eventual empirical comparison, not the system's name or component count.
