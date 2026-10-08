# Problem framing

1. Decision: staff roster and ingredient ordering
2. Target: how many visitors will come
3. Unit: one restaurant, one day (`air_store_id` + `visit_date`)
4. Horizon: next one week
5. What is known at the time of forecasting: how many people have already booked, how many visitors came in previous days, and the calendar
6. Metric: keep some data separate and check the model on that first

## Risks / questions on my mind

- If our prediction is wrong, it could cause losses or hurt the restaurant's rating because there may be too little food or too much food.


| File                | What it contains                                     | Columns I'd use                                          | Why                                                                 |
| ------------------- | ---------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------- |
| `air_visit_data`    | Daily visitors per Air restaurant                    | `visitors`, `visit_date`                                 | `visitors` is my target                                             |
| `air_reserve`       | Reservations made through the Air reservation system | `visit_datetime`, `reserve_datetime`, `reserve_visitors` | Tells us how many people have already reserved and when they booked |
| `air_store_info`    | Information about Air restaurants                    | `air_store_id`, `air_genre_name`, `air_area_name`        | Tells us the restaurant type and location                           |
| `hpg_reserve`       | Reservations made through the HPG reservation system | `visit_datetime`, `reserve_datetime`, `reserve_visitors` | Tells us how many people have already reserved through HPG          |
| `hpg_store_info`    | Information about HPG restaurants                    | `hpg_store_id`, `hpg_genre_name`, `hpg_area_name`        | Tells us the restaurant type and location                           |
| `store_id_relation` | Relationship between Air and HPG restaurants         | `air_store_id`, `hpg_store_id`                           | Connects the Air and HPG restaurant IDs                             |
| `date_info`         | Date and holiday information                         | `calendar_date`, `holiday_flg`                           | Tells us about weekdays and holidays                                |
| `sample_submission` | Format required for submitting predictions           | `id`, `visitors`                                         | Shows us the format our predictions need to follow                  |
