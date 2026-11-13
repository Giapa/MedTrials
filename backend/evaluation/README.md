# Search evaluation

This is a small starting set for checking search behavior. It is not a clinical evaluation.

## Examples and references

[cases.json](cases.json) contains ten fictional searches in Greek and English and four reference records selected by reading public ClinicalTrials.gov records. The records were checked on 11 November 2026: each mentions the named condition and lists a location in Greece. The reference links and the date each record was last updated are in the file.

A reference record is a potentially relevant result for a condition search, not proof that anyone can join. Some reference studies are completed. All cases search without the optional recruitment filter. One reference per condition was selected for this initial check; many other studies may also be relevant.

The examples were not reviewed by a clinician. They are a small, hand-selected set, and some records had already been seen during development. Paired searches share the same references, so cases are not independent. Greek inputs are exploratory: this backend check sends them directly to the registry and does not use the website's Greek term suggestions. There are no cases for ranking all relevant studies, deciding whether someone is eligible, explaining rules, privacy, or checking whether an answer is medically correct.

## Run

From `backend/`, with dependencies installed and an internet connection:

```sh
uv run python -m backend.evaluation --max-pages 3 --output evaluation/my-results.json
```

The command uses the app's search endpoint and live ClinicalTrials.gov data. It sends the fictional terms to ClinicalTrials.gov. If you add examples, never use real patient details: queries are sent to the registry and included in any saved report.

For each reference, the command checks the ID, title, last update date, and whether a Greek location is still listed. If any of these change, the affected cases are marked `reference_changed` and excluded until a person reviews the record. This check cannot detect every change or replace a clinical review. If the source or the app is unavailable or returns malformed data, the cases are marked `error`, not missed.

For a valid search, `found` means the selected reference ID appears in the pages checked; `missed` means it does not. The command checks one page by default; `--max-pages` can be set from 1 to 10. It stops early when it finds the reference or the registry has no more pages. Each page contains up to ten registry records. `more_results` indicates that the registry had more records after the last page checked. The report also records the first-page outcome separately. If a later page fails before the target is found, the case is an error rather than a miss.

The target hit rate divides `found` by `found + missed` and excludes errors and changed references. It is **not** overall recall, precision, or a measure of eligibility. A miss can mean the chosen record was ranked beyond the checked pages, even if other useful records were returned.

This command evaluates ClinicalTrials.gov only. It does not evaluate the separate European CTIS search or the Greek suggestion step in the website. See the European evaluation below and the [Greek suggestion evaluation](../../frontend/evaluation/README.md).

The report is printed and optionally saved as JSON, including the case-file hash and UTC time. The command exits with status 1 if any cases have errors or changed references; it exits with status 0 for a completed measurement even when records are missed. Reports should be reviewed rather than used as an automatic safety approval.

## First observations

The first two runs below used the same case file and search code at Git commit `8c7fb0de1cbf19b1386fc9d114eef45384850ce6`. Search results and registry records can change over time.

- [First run](baseline-2026-11-11.json), 11 November 2026 at 19:46 Athens time: 0 found, 6 missed, 4 errors. The first version of the report did not record HTTP status codes.
- [Second run](recheck-2026-11-11.json), 11 November 2026 at 19:47 Athens time: 0 found, 8 missed, 2 errors. The two sentence-style searches returned HTTP 502 from the app. Both had succeeded when retried individually before this run; the cause had not yet been identified.

In the second run, each of the four short English condition searches returned ten records and reported that more were available, but did not show the selected reference in those ten. Each of the four short Greek searches returned no records. The two sentence-style searches could not be scored because of the errors. These observations do not tell us whether the English searches returned other relevant studies, or whether the selected references would appear later.

After adding pagination, a [three-page run](pagination-2026-11-11.json) on 11 November 2026 at 19:56 Athens time found two references, missed two, and had six errors. The breast-cancer reference appeared on page three, and the type-2-diabetes reference on page two. The two completed Greek searches returned no records. One lung-cancer search failed on its second page, and five other searches failed on their first page. The cause had not yet been identified. This incomplete, small run does not establish overall search quality or reliability.

## Rate-limit investigation

On 12 November, rerunning the same evaluation reproduced the errors. The app's connection received HTTP 429 responses, meaning it was being rate limited, and the app converted them into generic HTTP 502 errors. In a separate check, the eleventh request in a burst received 429, while twelve requests spaced one second apart succeeded. The observed 429 response did not include a `Retry-After` header. This evidence does not establish whether the limit was imposed by ClinicalTrials.gov or a gateway between the app and the registry, or what the limit will be in another environment.

The app now makes at most one automatic retry after a 429. When no retry time is supplied, it waits ten seconds. When a valid retry time is supplied, it respects it if it is at most ten seconds; for longer or invalid values it returns a busy response without an automatic retry. Persistent rate limits are shown to users as a busy connection, and earlier pages remain visible. This is bounded error handling, not a guarantee against rate limiting.

After this change, the [three-page run](rate-limit-2026-11-12.json) on 12 November 2026 at 13:20 Athens time found three references, missed seven, and had no errors. The breast-cancer reference appeared on page three; the diabetes and scleroderma references appeared on page two. The remaining cases included Greek searches and sentence-style searches. A single small run cannot prove that the errors are eliminated or that results are clinically suitable.

## European search evaluation

[eu-cases.json](eu-cases.json) contains five fictional English searches and five public CTIS records. Each reference was checked on 12 November 2026: its title and condition match the values in the file, and Greece is listed among the trial's countries. A listed country does not mean a Greek site is currently recruiting. Four references are selected targets; one record has a different lung-cancer subtype and is marked as a known mismatch for the small-cell query. The references do not determine whether a person can join.

From `backend/`, with dependencies and internet access:

```sh
uv run python -m backend.eu_evaluation --max-pages 2 --output evaluation/my-eu-results.json
```

The command checks the current title, condition and Greece listing of each reference, then uses the app's European search endpoint. It checks up to the chosen number of pages, even after finding the target, to look for the specific labelled mismatch. The report includes the returned IDs, first-page target result, pages checked, whether more pages remain, and any labelled mismatches seen. If a reference changes or a request fails, the affected case is excluded from the target hit rate. A failure on a later page is an error, even if the target appeared earlier. The command exits with status 1 on errors or changed references, and 0 for a completed measurement even when a target is missed or a known mismatch appears.

On 12 November 2026, the [two-page run](eu-baseline-2026-11-12.json) found four of five selected targets, all on the first page. The full-sentence search `I have type 2 diabetes` returned no results. The `small cell lung cancer` search returned the selected small-cell target, but also showed the labelled non-small-cell record on the first page. These are different named subtypes; the record must be checked rather than assumed to fit a person's situation. No other results were reviewed for mismatch, so the report cannot establish how many results are relevant or irrelevant.

The website now shows a limited caution for the exact `small cell lung cancer` search and flags some results that explicitly mention `non-small cell` in their displayed title or condition. The backend evaluation still reports the mismatch because the app keeps the record visible. The evaluation does not measure the warning or detect all mismatches; its result should not be interpreted as proof that unflagged records match.

This is a small development set, not an independent benchmark. Some references were found while building or inspecting the search; two cases use the same diabetes reference. The examples have not been reviewed by a clinician and do not measure eligibility, full recall, overall precision, translation quality, or the Greek website interaction. The raw English query is sent to CTIS through the app and saved in the report. Do not add real patient details. Registry contents, ordering and availability can change; a missing target may be beyond the pages checked.

## Checking quoted evidence

The separate [quote examples](quote-cases.json) use a public CTIS record that lists Greece. To check them against the current record:

```sh
uv run python -m backend.evidence_check
```

The command checks the trial number and source link, then looks for each exact quote in the specified objective, inclusion criterion or exclusion criterion and language. Criterion `index` starts at zero. It fetches the record through the app's CTIS lookup, which requires Greece to be listed. It reports `quote_found`, `quote_not_found`, `field_unavailable`, or `source_error`. A missing field, a changed record, or a connection error is not evidence that a claim is false. The command exits with status 1 when any quote cannot be checked or found. This example intentionally contains an invented quote, so a status of 1 is expected when the source is available.

The [13 November run](quote-baseline-2026-11-13.json) found the Greek and English objective excerpts and an inclusion excerpt; it did not find the invented quote. The inclusion excerpt accompanies a deliberately misleading claim that every adult can join. The quote is real, but the record has additional inclusion and exclusion criteria. **A found quote does not establish that its claim is true, complete, safe, or medically correct.** This check must not be used on its own to approve or display generated explanations.

The examples are manually written and have not been reviewed by a clinician. The check does not evaluate paraphrases, omitted criteria, interpretation, eligibility, or the source's accuracy. It currently covers CTIS records only and relies on the portal's undocumented data endpoint. Registry text can change, so a previously matching quote can stop matching. The input and printed report contain the supplied claims and quotes; only trial numbers are sent to the app's CTIS lookup. The report is not saved unless `--output` is supplied. Do not put real patient details in example files or saved reports.
