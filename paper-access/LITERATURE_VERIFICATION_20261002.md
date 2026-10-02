# Bounded literature verification

External review proposed Yu et al., ACM Computing Surveys2024,160 studies.
Crossref DOI10.1145/3732777 instead records TOSEM35(1),1--42, published
2025-12-12. Deposited abstract reports142 studies across six AI-system layers.
Title and eight author names were inspected. ACM landing page returned403;
full text not inspected. Citation supports only the abstract-level survey scope.
Source: https://api.crossref.org/works/10.1145/3732777
Year/issue should be reconciled against publisher full text before submission;
no claim that the erroneous review reference was correct.

Temporal Activity Definition was read from official docs: Activities should be
idempotent; completed effects can exist before completion is recorded. This
does not imply a Temporal wrapper is impossible or requires replacing ComfyUI.
https://docs.temporal.io/activity-definition

AWS transactional outbox guidance was read: database/message dual writes,
atomic intent and duplicate-message/consumer-idempotency considerations. It does
not automatically provide generator-side deduplication or unknown-job recovery.
https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

No empirical Temporal/outbox/idempotent-service comparison exists in our study.
The new related-work paragraphs map responsibilities, not inferiority.
