# Search evaluation

This is a small starting set for checking search behavior. It is not a clinical evaluation.

## Examples and references

[cases.json](cases.json) contains ten fictional searches in Greek and English and four reference records selected by reading public ClinicalTrials.gov records. The records were checked on 11 November 2026: each mentions the named condition and lists a location in Greece. The reference links and the date each record was last updated are in the file.

A reference record is a potentially relevant result for a condition search, not proof that anyone can join. Some reference studies are completed. All cases search without the optional recruitment filter. One reference per condition was selected for this initial check; many other studies may also be relevant.

The examples were not reviewed by a clinician. They are a small, hand-selected set, and some records had already been seen during development. Paired searches share the same references, so cases are not independent. Greek inputs are exploratory because the current interface asks people to search in English. There are no cases for ranking all relevant studies, deciding whether someone is eligible, explaining rules, privacy, or checking whether an answer is medically correct.

## Run

From `backend/`, with dependencies installed and an internet connection:

```sh
uv run python -m backend.evaluation --output evaluation/my-results.json
```

The command uses the app's search endpoint and live ClinicalTrials.gov data. It sends the fictional terms to ClinicalTrials.gov. If you add examples, never use real patient details: queries are sent to the registry and included in any saved report.

For each reference, the command checks the ID, title, last update date, and whether a Greek location is still listed. If any of these change, the affected cases are marked `reference_changed` and excluded until a person reviews the record. This check cannot detect every change or replace a clinical review. If the source or the app is unavailable or returns malformed data, the cases are marked `error`, not missed.

For a valid search, `found` means the selected reference ID appears among the results shown by the app; `missed` means it does not. `more_results` comes from the registry and indicates that additional records were available beyond the first page. The target hit rate divides `found` by `found + missed` and excludes errors and changed references. It is **not** overall recall, precision, or a measure of eligibility. A miss can mean the chosen record was ranked after the first ten, even if other useful records were returned. The app does not currently provide a way to view later results.

The report is printed and optionally saved as JSON, including the case-file hash and UTC time. The command exits with status 1 if any cases have errors or changed references; it exits with status 0 for a completed measurement even when records are missed. Reports should be reviewed rather than used as an automatic safety approval.

## First observations

Both runs below used the same case file and search code at Git commit `8c7fb0de1cbf19b1386fc9d114eef45384850ce6`. Search results and registry records can change over time.

- [First run](baseline-2026-11-11.json), 11 November 2026 at 19:46 Athens time: 0 found, 6 missed, 4 errors. The first version of the report did not record HTTP status codes.
- [Second run](recheck-2026-11-11.json), 11 November 2026 at 19:47 Athens time: 0 found, 8 missed, 2 errors. The two sentence-style searches returned HTTP 502 from the app. Both had succeeded when retried individually before this run; the cause of the intermittent errors is not known.

In the second run, each of the four short English condition searches returned ten records and reported that more were available, but did not show the selected reference in those ten. Each of the four short Greek searches returned no records. The two sentence-style searches could not be scored because of the errors. These observations do not tell us whether the English searches returned other relevant studies, or whether the selected references would appear later.
