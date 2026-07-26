# Scenario Patterns

Patterns for the research tasks that come up most often. Read this when handling a composite task, or when unsure what a good result looks like for a task type.

Each pattern describes the goal shape, the key moves, the quality bar, and the common mistakes. None of them is a fixed procedure: compose the six disciplines from SKILL.md in whatever order the task demands, and treat these patterns as a description of what a strong result looks like, not as steps to execute.

## Contents

- [Single-focus tasks](#single-focus-tasks)
  - [Fact or claim check](#fact-or-claim-check)
  - [Version and changelog check](#version-and-changelog-check)
  - [Price and terms check](#price-and-terms-check)
  - [News and event timeline](#news-and-event-timeline)
  - [Documentation site coverage](#documentation-site-coverage)
  - [Person or organization background](#person-or-organization-background)
  - [Academic and technical literature](#academic-and-technical-literature)
- [Composite tasks](#composite-tasks)
  - [Multi-option comparison](#multi-option-comparison)
  - [Technology due diligence](#technology-due-diligence)
  - [Market or landscape scan](#market-or-landscape-scan)
  - [Research-backed writing](#research-backed-writing)
  - [Recurring monitoring brief](#recurring-monitoring-brief)

## Single-focus tasks

### Fact or claim check

- **Goal shape**: a verdict, true, false, partly true, or unverifiable, with the strongest evidence for it and a concrete date.
- **Key moves**: trace the claim to its origin; check the origin against primary sources; run one counter-search on the verdict before committing to it.
- **Quality bar**: the verdict distinguishes what is confirmed from what is inferred, and an unverifiable claim is called unverifiable rather than guessed.
- **Common mistakes**: verifying that many pages repeat the claim instead of verifying the claim; missing that the claim was once true but has since changed.

### Version and changelog check

- **Goal shape**: the exact current state, version number, release date, relevant changes, deprecations, with the official release channel as the source.
- **Key moves**: go straight to the project's releases page, changelog, or tags; confirm which release line the user is on if it matters; check whether "latest" means stable or pre-release.
- **Quality bar**: version numbers and dates are exact; breaking changes relevant to the user's situation are pulled out rather than left buried in the list.
- **Common mistakes**: citing a blog post about a release instead of the release itself; mixing stable and beta channels; missing that documentation lags the release.

### Price and terms check

- **Goal shape**: current figures from the official pricing page, with retrieval date, plan names, units, and the conditions that change the figure (region, billing period, tier limits).
- **Key moves**: read the official page, not a review site; note the retrieval date; check for regional or currency variants when relevant to the user.
- **Quality bar**: two-source rule applied, or the single official source labeled as such; every number carries its unit and conditions.
- **Common mistakes**: quoting third-party price roundups that have gone stale; missing usage limits or mandatory add-ons that change the real cost.

### News and event timeline

- **Goal shape**: an ordered sequence of dated events, each anchored to first-hand reporting or official statements, with rumor and confirmation kept distinct.
- **Key moves**: anchor each event to the date it happened, not the date an article appeared; prefer original reporting over syndication; mark items that are reported but unconfirmed.
- **Quality bar**: a reader can see what is established, what is claimed by one party, and what is speculation.
- **Common mistakes**: ordering by publication date; treating widespread syndication of one report as multiple confirmations.

### Documentation site coverage

- **Goal shape**: an inventory of the relevant pages, then accurate detail from the pages that matter, with an explicit statement of coverage.
- **Key moves**: map the site's structure first through its navigation, index, or sitemap; select pages by relevance rather than reading linearly; state whether the answer covers the full inventory or a sample.
- **Quality bar**: coverage claims match what was actually read; the site's own organization is reflected rather than guessed.
- **Common mistakes**: claiming completeness after keyword-searching into a handful of pages; missing that a site splits documentation across versions.

### Person or organization background

- **Goal shape**: verified facts with sources and dates, clearly separated from characterization and opinion.
- **Key moves**: prefer primary records, official biographies, filings, first-party statements; date every role or status, since these change; keep negative material to what sources actually establish.
- **Quality bar**: nothing stated about a real person or organization that the cited sources do not support; disputed characterizations attributed, not adopted.
- **Common mistakes**: merging people with similar names; presenting an outdated role as current; repeating characterizations as facts.

### Academic and technical literature

- **Goal shape**: the relevant papers or specifications, correctly summarized, with a distinction between established results and preliminary or contested ones.
- **Key moves**: locate the original paper rather than press coverage of it; check publication venue and date; when a result is load-bearing, look for replications, follow-ups, or published criticism.
- **Quality bar**: summaries match what the paper claims, at the strength it claims; preprints identified as preprints.
- **Common mistakes**: citing science journalism as if it were the paper; overstating a result the authors stated cautiously.

## Composite tasks

Composite tasks are compositions of the single-focus patterns above. The composition is stated for each; the discipline that matters most is keeping the parts aligned so they can be merged honestly.

### Multi-option comparison

- **Composition**: a per-option evidence pass (facts, versions, prices as needed) merged into one aligned matrix.
- **Key moves**: fix the comparison fields before researching so every option is measured against the same questions; collect evidence per option to comparable depth; where a field cannot be confirmed for one option, mark the gap instead of leaving the cell quietly uneven.
- **Quality bar**: the matrix is aligned, gaps are visible, and the recommendation, if one is asked for, follows from the matrix plus the user's stated criteria, not from general reputation.
- **Common mistakes**: comparing marketing pages against documentation; letting the best-documented option look like the best option.

### Technology due diligence

- **Composition**: documentation coverage, version and changelog check, community-health assessment, and a deliberate risk pass.
- **Key moves**: alongside the favorable evidence, run a dedicated counter-evidence pass, open issues, known limitations, migration-away stories, security history; check maintenance signals (release cadence, maintainer activity, issue response) rather than popularity signals alone.
- **Quality bar**: the risk section is researched as thoroughly as the capability section; every risk claim is dated, since project health changes quickly.
- **Common mistakes**: due diligence that only collects reasons to say yes; star counts standing in for health.

### Market or landscape scan

- **Composition**: breadth-first decomposition into segments or players, a bounded evidence pass per segment, then consolidation into one map.
- **Key moves**: define the scope boundary explicitly, what counts as in-market; bound the per-player depth so breadth is achievable; consolidate periodically so the picture stays coherent as sources accumulate.
- **Quality bar**: the scope statement lets the reader judge what a missing player means; per-player facts carry dates.
- **Common mistakes**: unbounded depth on the first few players and thin coverage of the rest; presenting the sample surveyed as the whole market.

### Research-backed writing

- **Composition**: depth-first evidence gathering, a full citation audit, then writing in the target form.
- **Key moves**: gather and consolidate evidence before drafting so the structure follows the findings; keep the citation audit separate from drafting, since fluent prose hides unsupported claims; match the final register and format to the destination document.
- **Quality bar**: every load-bearing claim in the final text survives the citation audit; the writing reads as one voice even though the evidence came from many places.
- **Common mistakes**: writing the frame first and backfilling evidence into it; citation density mistaken for citation quality.

### Recurring monitoring brief

- **Composition**: a time-boxed news and version pass over a fixed watchlist, compared against the previous brief.
- **Key moves**: restrict searching to the period since the last brief; compare against the previous state so the brief reports changes, not repeats; keep a consistent structure across briefs so differences stand out; say explicitly when nothing meaningful changed.
- **Quality bar**: a reader of the series sees deltas at a glance; absence of news is reported as such rather than padded.
- **Common mistakes**: re-reporting old items as new; padding a quiet period to look substantial.
