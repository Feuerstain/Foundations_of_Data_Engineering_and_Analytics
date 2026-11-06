# DevHire Europe — synthetic technology job advertisements (datasheet)

The dataset `synthetic_tech_jobs_2025_2026.csv` (available on OLAT) has 2,400 rows,
exactly 1,200 for each of 2025 and 2026. The 2026 rows describe exactly the advertisements
visible on the Sheet 3 website. Use the canonical data for Sheet 4 after comparing
your own crawl with those rows.

All advertisements and employers are fictional. These data support an exercise
in acquisition, validation, and exploratory analysis; they are not observations
of actual vacancies, required experience, or salaries offered by employers.

## Reading the CSV

The file is UTF-8, comma-separated, with a header and LF line endings. Fields
containing commas are quoted using standard CSV quoting. Empty cells mean
missing/not disclosed, **not zero**. Booleans are lowercase `true` and `false`.
Dates use ISO `YYYY-MM-DD`. Do not split CSV rows manually on commas.

| Field | Type | Meaning |
| --- | --- | --- |
| `job_id` | string | Unique synthetic ID, e.g. `DH26-0001`; unrelated to any survey respondent ID. |
| `survey_year` | integer | Source survey year, either 2025 or 2026. This identifies independent cross-sectional snapshots. |
| `title` | string | Generated job title. |
| `role_family` | category | `full-stack`, `backend`, `frontend`, `application-development`, `data-ai`, `platform-operations`, or `architecture-management`. |
| `seniority` | ordered category | `junior` (0–2 required years), `mid` (3–5), `senior` (6–10), or `lead` (11–20). Generated deterministically from required experience. |
| `company_name` | string | Fictional employer; repeated names refer to the same generated company profile. |
| `company_size` | category | Fictional employer headcount band; generated independently, not a numeric measurement. |
| `industry` | category | Fictional employer sector from a fixed template list. |
| `country` | category | Source respondent's country, repurposed as fictional job location. Both years use the same fixed 20-country 2025 euro-area list. |
| `city` | string, nullable | A randomly assigned real city in that country; 5% of locations are undisclosed. It is not a survey respondent's city. |
| `work_mode` | category | `remote`, `hybrid`, `onsite`, or `flexible`. `flexible` preserves the survey's “Your choice” response rather than treating it as hybrid. |
| `salary_min_eur` | integer, nullable | Generated lower bound of annual gross compensation in EUR, including bonuses and perks; not base salary. |
| `salary_max_eur` | integer, nullable | Generated upper bound in the same units. Both bounds are missing together for 15% of advertisements. |
| `required_experience_years` | integer | Generated requirement in years, in 0–20; not the original professional experience measurement. |
| `technologies` | string list | Semicolon-separated distinct tags. These combine a sampled subset of source programming languages, databases, and web frameworks; the number of tags is about a quarter of the respondent's reported tags, bounded to 2–8 (a single tag only if the respondent reported just one). Documented role defaults fill completely missing source tags. |
| `posted_at` | ISO date | Fictional publication date between August 26 and October 25 of the source year. |
| `salary_disclosed` | boolean | Whether the advertisement displays both salary bounds. False implies both bounds are missing. |

There are **17 columns**; the shared contract is defined by the field names above.
JSON used inside the website represents `technologies` as an array, missing values
as `null`, and booleans as native JSON booleans. Descriptive website prose is
generated separately and is not required in the CSV.

## Derived variables for the exercises

- `salary_midpoint_eur = (salary_min_eur + salary_max_eur) / 2` only when both
  bounds are available. This is a generated range midpoint, not a measured salary.
- `technology_count` is the number of nonempty semicolon-separated tags.
- `log_salary` is the natural logarithm of a positive salary midpoint. State your
  logarithm convention when interpreting axes or comparing plots.
- Derive missingness indicators before dropping rows. State the sample size used
  for every analysis; complete-case salary analysis excludes 180 rows per year.

For crawl validation, compare unique IDs first, then normalize CSV booleans,
numbers, missing values, and technology tag order before comparing field values.
Keep the two years separate when validating the 2026 crawl.

## Source, harmonization, and generation

Source: **Stack Overflow Developer Survey, Stack Exchange Inc.**, official
[2025](https://github.com/StackExchange/Survey/tree/9dd5c163b7ec09ce5503f711c37a99dbd80ff3c7/packages/archive/2025)
and [2026](https://github.com/StackExchange/Survey/tree/9dd5c163b7ec09ce5503f711c37a99dbd80ff3c7/packages/archive/2026)
archives. The data were generated with a fixed random seed (`dea-jobs-v2`).

Cross-year mappings: `DevType` → `Role`, `RemoteWork` → `WorkSetting`,
`CompTotal` → `Compensation`, `LanguageHaveWorkedWith` →
`LanguagesHaveWorkedWith`, `DatabaseHaveWorkedWith` → `DatabasesHaveWorkedWith`,
and `WebframeHaveWorkedWith` → `WebFrameworkHaveWorkedWith`.

Eligibility requires a supported role, a recognized work setting, a fixed-list
euro-area country, day-to-day currency EUR, numeric total annual compensation in
€10,000–€300,000, and professional work experience in 0–50 years. Other respondents
are excluded. Role mappings merge related categories into the seven families.
The generator samples without replacement, reserves 80 rows per role family,
and assigns remaining places proportionally to remaining eligible counts using
largest remainders. This deliberately reweights smaller role groups for teaching.

Required experience is `round(0.5 × WorkExp)` plus jitter from `[-1, 0, 0, 1]`,
clamped to 0–20. Seniority follows the thresholds in the table. Source annual
compensation is multiplied by a uniform factor in 0.94–1.06, rounded to €1,000,
and given a symmetric range with half-width of 6–14% (at least €2,000), also rounded
to €1,000. Exactly 180 salary ranges per year are suppressed by seeded weighted
sampling: the chance of withholding a salary rises with seniority (relative
weights: junior 0.5, mid 0.8, senior 1.2, lead 1.8). Exactly 60 cities per year are suppressed uniformly at random,
independently. Suppressed salary values are not in the CSV.

Company, company size, industry, city, title, descriptions, benefits, and dates
are fictional. Source employer-size answers do not determine generated company
profiles. Technology requirements are fictional selections of tools reported by
survey respondents; a person's reported tool use is not evidence of employer
demand for those tools. No row-level respondent identifiers or linkage are released.

## Interpretation boundaries

- These surveys are voluntary community samples, not representative samples of
  European developers or employers. See the [2025 methodology](https://survey.stackoverflow.co/2025/methodology)
  and [2026 methodology](https://survey.stackoverflow.co/2026/methodology).
- Both survey years ask about total compensation, not the base salary used in the
  earlier IT salary exercise. Values are nominal EUR; there is no inflation or
  purchasing-power adjustment.
- Role labels and question wording evolved. Harmonization does not establish full
  measurement equivalence. The two surveys do not follow the same people.
- Generated seniority is a function of generated experience. Their relationship
  is a construction rule, not an independent empirical discovery.
- Salary ranges, experience requirements, employer details, disclosure, and dates
  are generator decisions. City-level or benefit-level market claims are invalid.
- Year differences can arise from source sample composition, filtering, role
  reweighting, sampling, and perturbation; they do not establish changes in the
  real vacancy market or a causal effect of country, role, work mode, or technology.
- Tail and normality claims need evidence and qualifications. Do not interpret a
  few outliers or a fitted density plot as proof of a particular population law.

## License and attribution

Contains information adapted from **Stack Overflow Developer Survey, Stack
Exchange Inc.**, [2025 and 2026 official archives](https://github.com/StackExchange/Survey/tree/main/packages/archive),
made available under the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Individual source contents are available under the
[Database Contents License (DbCL) 1.0](https://opendatacommons.org/licenses/dbcl/1-0/).

The adapted DevHire Europe database is made available under the ODbL 1.0, and any
rights in its individual contents under the DbCL 1.0. Preserve this attribution and
the license notices when sharing the dataset or adaptations. All companies and
advertisements are fictional teaching material, provided as-is without any warranty
of accuracy, fitness for a particular purpose, or representativeness.
