# Problem framing

## Core questions

1. **Decision:** staff roster and ingredient ordering for each restaurant.
2. **Target:** `visitors`, the number of visitors per restaurant per day.
3. **Unit:** one restaurant, one day (`air_store_id` + `visit_date`).
4. **Horizon:** 39 days (2017-04-23 to 2017-05-31, as in `sample_submission`).
5. **Known at forecast time:**
   - past visitors of each restaurant
   - reservations already made (only rows with `reserve_datetime` before the forecast date)
   - the calendar, because weekdays and holidays are known in advance
6. **Metric:** RMSLE (the competition metric; it judges errors relative to size) and MAE (average error in visitors).
   **Validation:** the last 39 days of the training data (2017-03-15 to 2017-04-22), so the model is tested only on days it has not seen.

## Risks / open questions

- **Business risk:** if the forecast is too high, food is wasted and money is lost. If it is too low, food runs out, customers leave and ratings can drop. The two errors do not cost the same.
- **Missing rows:** a missing row can mean the restaurant was closed or that nothing was recorded, so missing rows must not be filled with 0.
- **Leakage:** a prediction for day D may only use information available before day D. This applies to rolling averages (use `shift`) and to reservations (use `reserve_datetime`).
- **Reservation duplicates:** some reservation rows share the same store, visit time and booking time. They look like separate bookings, so they are summed, not dropped.
- **HPG coverage:** only 150 of the 829 Air stores have an HPG ID, so HPG reservation data will help only some restaurants.
- **Outliers:** `visitors` is right-skewed (median 17, max 877), so extreme days need a look in EDA.

## File hypotheses

| File | What it contains | Columns I'd use | Why |
|---|---|---|---|
| `air_visit_data` | Daily visitors per Air restaurant | `air_store_id`, `visit_date`, `visitors` | `air_store_id` identifies the restaurant, `visvisitors` is my target |
| `air_reserve` | Reservations made through the Air system | `air_store_id`, `visit_datetime`, `reserve_datetime`, `reserve_visitors` | Shows how many people have already booked, and `reserve_datetime` helps avoid data leakage |
| `air_store_info` | Information about Air restaurants | `air_store_id`, `air_genre_name`, `air_area_name`, `latitude`, `longitude` | Restaurant type and location change demand (for example a ramen shop vs an izakaya) |
| `hpg_reserve` | Reservations made through the HPG website | `hpg_store_id`, `visit_datetime`, `reserve_datetime`, `reserve_visitors` | Extra booking signal, but it must be linked to Air stores first |
| `hpg_store_info` | Information about HPG restaurants | `hpg_store_id`, `hpg_genre_name`, `hpg_area_name` | Type and location of HPG restaurants |
| `store_id_relation` | Mapping between Air and HPG IDs | `air_store_id`, `hpg_store_id` | The bridge needed to join HPG data to Air stores |
| `date_info` | Calendar with weekday and holiday flag | `calendar_date`, `day_of_week`, `holiday_flg` | Weekday and holiday patterns are strong signals and known in advance |
| `sample_submission` | Required format for predictions | `id`, `visitors` | Defines the test set: 821 stores x 39 days |