# Verification Reference

How to decide what to trust, how hard to check, and how to make citations hold up. Read this when an answer depends on contested, volatile, or high-stakes facts.

## Contents

- [Source hierarchy](#source-hierarchy)
- [Freshness rules](#freshness-rules)
- [How much verification a claim needs](#how-much-verification-a-claim-needs)
- [Counter-evidence technique](#counter-evidence-technique)
- [Resolving conflicting sources](#resolving-conflicting-sources)
- [Citation audit checklist](#citation-audit-checklist)
- [Failure modes to avoid](#failure-modes-to-avoid)

## Source hierarchy

Prefer sources in this order, and let a lower-ranked source add context but never silently override a higher-ranked one:

1. Official documentation, standards bodies, direct product pages, and primary datasets.
2. Release notes, changelogs, source repositories, and maintainers' direct statements.
3. Government records, regulatory filings, incident reports, and company disclosures.
4. Reporting by outlets that name their sources and show their work.
5. Specialist analysis, community posts, and forum threads.

Rank by relationship to the fact, not by presentation. The deciding question is always: how does this author know? A personal blog by the maintainer of a library outranks a polished news aggregator repeating a rumor about it. Aggregators, republishers, and search-optimized content farms often rank highly in results while adding nothing; trace every important claim to whoever first made it, and cite that origin.

## Freshness rules

- Distinguish the date something happened from the date an article was published, and prefer the former when they differ.
- Check whether a page shows both a published date and an updated date; documentation pages are frequently updated in place.
- For software questions, confirm which version a statement applies to. Mixing statements about different versions is one of the most common research errors.
- When the user asks about "now", record the retrieval date of each key fact and include it in the answer where it matters.
- Treat undated pages with extra suspicion for time-sensitive claims; an undated page cannot support a "current" claim on its own.

## How much verification a claim needs

Match the depth of checking to the cost of being wrong:

- **One strong primary source suffices** for stable, uncontested facts: what a product is, what an API parameter does, what a document says.
- **Two independent sources are required** for volatile or high-stakes facts. Independent means they did not copy from each other; two articles repeating the same press release count as one source. Categories that always need two: prices and contract terms, version support and end-of-life status, legal and regulatory status, personnel and organizational changes, security advisories, statistics used to support a decision, and anything the user will act on with real consequences.
- **Mark it when the bar is not met.** If only one source exists for a claim in the two-source category, keep the claim but label it single-source. Readers can weigh a labeled claim; they cannot weigh an invisible gap.

## Counter-evidence technique

Queries inherit the bias of their phrasing: searching "why X is better than Y" surfaces pages agreeing that X is better. After forming a conclusion, run at least one search specifically shaped to find disconfirming evidence, for example the negated claim, the strongest rival claim, or "problems with", "criticism of", "migration away from" phrasings. Three outcomes are all useful: the counter-search finds nothing substantial, which strengthens the conclusion; it finds a real objection, which improves the answer; or it reveals the question is genuinely contested, which the answer must then say.

Apply the same technique to premises the user supplied. A request built on a shaky premise deserves a correction, delivered plainly, before any research built on top of it.

## Resolving conflicting sources

When sources disagree, do not average them and do not silently pick one. Work through four dimensions:

1. **Primacy**: which source is closest to the fact itself?
2. **Time**: which statement is newer, and did the fact plausibly change in between?
3. **Interest**: does either source benefit from its version being believed?
4. **Verifiability**: which source shows evidence a third party could check?

If the conflict survives this analysis, it is a real conflict; present both versions with dates and provenance, state which one you weight more and why, and let the reader see the disagreement. A conflict the reader can see is information; a conflict resolved invisibly is a gamble taken on their behalf.

## Citation audit checklist

Run this on the draft answer, claim by claim, before delivering:

- Every contested or load-bearing claim points to a specific source that was actually opened and read, not merely seen in a search snippet.
- Each cited source really contains the statement attributed to it, at the strength attributed. A source that says "may reduce" does not support "reduces".
- Quotations are verbatim and attributed to the right author.
- Links point to the exact page, not the site's front page, and were reachable when checked.
- Secondary reports citing an original are cited as secondary, or replaced with the original.
- Single-source claims in the two-source category carry their label.

## Failure modes to avoid

Each of these is a recurring, documented way research answers go wrong:

- Answering from snippets without opening the page behind them.
- Treating a well-designed aggregator or content farm as a primary source.
- Mixing facts about different versions, editions, or dates of the same subject.
- Quoting an outdated summary when current official documentation exists.
- Adopting the user's framing as a finding instead of testing it.
- Resolving source conflicts silently instead of surfacing them.
- Using relative time words in the answer without concrete dates behind them.
- Citing a page for a claim it does not actually make.
- Presenting an answer with confident wording that the underlying evidence does not support.
