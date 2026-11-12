# Greek suggestion evaluation

This check uses 28 fictional Greek inputs to assess the website's condition-term suggestions. It does not check a person's eligibility or whether returned trials are relevant. The examples and expected terms are in [greek-search-cases.json](greek-search-cases.json). The file links to sources for the medical terms. A `null` expected value means the example should not produce a single condition suggestion. For example, the app should not drop a negative or extra medical detail and turn the remaining words into a search.

From `frontend/`, after installing dependencies:

```sh
npm run evaluate:greek
```

The check runs the actual search form in a simulated browser. It records the suggested term, whether an explicit selection is required before sending a search, whether a source link is present, and the term submitted after selection. Registry requests are simulated: no search is sent to ClinicalTrials.gov. It prints matched suggestions, expected refusals, missed suggestions, wrong terms, and unexpected suggestions. Misses are reported but do not fail the command. Wrong terms, unexpected suggestions, missing source links, bypassing selection, or sending a different term make the command fail.

The expected positive suggestions express what a future tool should be able to recognize. They do not mean the current app promises to recognize general sentences. A sentence with a negation, a different person, or additional details is a separate safety case where the current expectation is not to suggest a single condition. These choices need review with patients and clinicians.

## Results on 12 November 2026

- 7 of 15 examples with an expected English suggestion matched it. Eight were missed: punctuation, spelling out “two”, two short sentences, a hyphenated form of non-small-cell lung cancer, asthma, multiple sclerosis, and the broad term for diabetes.
- All five cases where no suggestion was expected produced none. No wrong English term or unconfirmed submission was observed in this set.

After implementing some of the missed examples, the same 20 development cases produced 15 of 15 expected suggestions and no suggestion in the five refusal cases. These cases were used to guide the change, so that result is not an independent test. We then added eight follow-up cases: two of six expected suggestions matched, four were missed, and both cases expecting no suggestion produced none. The misses included “Πάσχω από άσθμα”, an exclamation mark, and a different grammatical form of non-small-cell lung cancer. We did not change the implementation to fit the follow-up cases.

These are small development and follow-up sets, not independent benchmarks. The same developer who implemented the feature chose the follow-up examples, and many conditions overlap with the development cases. The examples are manually chosen, are not representative of real searches, and have not been reviewed by a clinician or patients. A matching term does not establish that a trial exists, that the registry will return it, or that a person can join. The existing [live registry evaluation](../../backend/evaluation/README.md) measures a different, limited question.
