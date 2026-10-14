# Data dictionary

| File | Rows | Columns | Row = one ... | Key | Notes |
|---|---|---|---|---|---|
| air_visit_data | 252,108 | air_store_id, visit_date, visitors | store-day | (air_store_id, visit_date), 0 duplicates | Target = visitors. 829 stores, 2016-01-01 to 2017-04-22. Coverage 85.1% inside each store's own span |
| air_reserve | 92,378 | air_store_id, visit_datetime, reserve_datetime, reserve_visitors | reservation record | No natural key (to verify) | Use reserve_datetime to avoid leakage. Must be aggregated to daily totals before joining |
| air_store_info | 829 | air_store_id, air_genre_name, air_area_name, latitude, longitude | Air restaurant | air_store_id | Restaurant type and location. No name column |
| hpg_reserve | 2,000,320 | hpg_store_id, visit_datetime, reserve_datetime, reserve_visitors | reservation record | No natural key (to verify) | Largest file: 121 MB on disk, 426 MB in pandas. Filter to mapped stores before joining |
| hpg_store_info | 4,690 | hpg_store_id, hpg_genre_name, hpg_area_name, latitude, longitude | HPG restaurant | hpg_store_id | Many more restaurants than Air |
| store_id_relation | 150 | air_store_id, hpg_store_id | Air-HPG restaurant pair | air_store_id | Only 150 of 829 Air stores have an HPG ID |
| date_info | 517 | calendar_date, day_of_week, holiday_flg | calendar day | calendar_date | Japan calendar with holiday flag, known in advance for future dates |
| sample_submission | 32,019 | id, visitors | test prediction (store, day) | id | id = air_store_id + "_" + date. 821 stores x 39 days, 2017-04-23 to 2017-05-31 |

## Key findings
- Missing rows: 44,171 store-days are missing inside the stores' own date spans. Coverage is 85.1% inside the span and only 63.6% over the full store x date grid, because many stores start late. Only 11 stores have no gaps, and 36 stores have more than 150.
- Missing means closed, mostly: 279 of 829 stores are missing one weekday more than 80% of the time (126 on Sunday, 82 on Monday). Missing rate is 28.6% on Sundays vs 5.6% on Fridays.
- Weekday pattern: Saturday is the busiest day (mean 26.3 visitors) and Monday the quietest (mean 17.2).
- Holiday effect: rows are missing 32.6% of the time on holidays vs 13.7% on normal days.
- Target: visitors is right-skewed (mean 21.0, median 17, max 877), so outliers need a look in EDA.
- Test set: 39 days, all 821 test stores have history in train, and 8 train stores are not in test.
- Decision: do not fill missing rows with 0, because a missing row can mean the restaurant was closed or that nothing was recorded.