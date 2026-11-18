# Ethics & Data Collection Protocol

## Sources / উৎস

Approved primary source: **consented survey** (paper form + online form) where
respondents agree in writing to research use. Approved secondary source:
public web forums/community threads where posting is public by design.

**Not approved without legal review:** private/closed Facebook groups
(membership-restricted content; scraping violates platform ToS). Public
groups may be used only if (a) posts are public, (b) quotes are anonymized,
and (c) institutional guidance permits; otherwise paraphrase items instead
of verbatim quotes.

## Anonymization / নাম নিষ্কাশন

Remove before storage:

1. Names, phone numbers, addresses, village/union identifiers, ID numbers.
2. Details that can re-identify a person alongside symptoms (rare condition +
   named place + date). Coarsen or drop.
3. Personal names inside quotes — replace with role words.

Store only: question text (paraphrased or consented verbatim), domain, risk
level, collection source type, collection date. A re-identification check by
a second person is required before an item enters `data/gold/`; record the
check in `data/raw/DATA_PROVENANCE.md`.

## IRB / ethical review

- Seek institutional review board (IRB)/ethics committee approval **before**
  distributing the survey; attach the survey instrument and consent text.
- Consent text must state: purpose, anonymization, voluntary participation,
  right to withdraw, and that questions will be published as a benchmark
  dataset.

## Responsible publication

- Do not publish verbatim questions that could stigmatize an identifiable
  respondent; prefer paraphrased items.
- When publishing unsafe LLM outputs as examples, add a clear warning that
  they are **not medical or agricultural advice**.
- Programmatic API evaluation must comply with each vendor's terms; do not
  redistribute vendor outputs wholesale beyond what analysis requires.

## Licensing

- Code: choose a permissive license (e.g., MIT) before release.
- Dataset: CC BY 4.0 recommended **after** confirming all items pass the
  anonymization check.
