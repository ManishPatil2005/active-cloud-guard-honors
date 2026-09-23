# Source and claim audit

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
