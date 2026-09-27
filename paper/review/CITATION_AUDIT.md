# Citation and scope check

Inline ARS citation-compliance phase; NOT an independent or exhaustive audit.
IEEE numeric bibliography. Seven cited entries; no orphan keys.

| Key | Evidence inspected | Permitted use |
|---|---|---|
| birrell1984 | Primary paper read earlier in this task; ACM TOCS 2(1), 39–59, 1984 | Established RPC failure semantics |
| aws | Authoritative Builders' Library article read earlier | Caller-provided idempotency keys under service contract |
| temporal | Official Activity Definition sections on idempotence, read earlier | Lost completion can cause retry; external side effects need idempotence |
| otel | Official Traces documentation, read earlier | Spans/context represent and correlate operations |
| toxiproxy | Official README, read earlier | Configurable TCP fault injection; no incapability assertion |
| rsm2019 | Microsoft author page; arXiv 1902.09502v3 introduction; Dagstuhl published record | Atomic runtime-managed processing and stronger guarantees within its model |
| filibuster | Official project overview at filibuster.cloud | Generates fault-injected test variations; overview only |

RSM published DOI verified at https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ECOOP.2019.18.
Publisher record establishes 2019, volume 134, 18:1–18:29 and eight authors.
The Microsoft BibTeX has an extra comma in an author entry; corrected using
Dagstuhl. An arXiv HTML rendering date is not treated as publication year.
A candidate ECOOP article 16 was a different title and was discarded before citation.
USENIX candidate URLs returned 403; no paper title/venue was inferred from them.
The Filibuster overview refers to SoCC 2021; this draft cites the overview,
not an unverified guessed OSDI bibliographic entry.

No systematic search, retraction-screen certificate or novelty proof is claimed.
The two academic references support background/positioning; official tool docs
support only documented responsibilities. No comparative performance is claimed.
Birrell DOI not inserted because the publisher endpoint was inaccessible in
this pass; primary PDF bibliographic metadata remains the verified citation.
