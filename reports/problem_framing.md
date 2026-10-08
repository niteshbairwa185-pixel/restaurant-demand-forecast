# Problem framing

1. Decision: staff roster and ingredient ordering
2. Target: how many visitors will come
3. Unit: one restaurant, one day (`air_store_id` + `visit_date`)
4. Horizon: next one week
5. What is known at the time of forecasting: how many people have already booked, how many visitors came in previous days, and the calendar
6. Metric: keep some data separate and check the model on that first

## Risks / questions on my mind

- If our prediction is wrong, it could cause losses or hurt the restaurant's rating because there may be too little food or too much food.