# Feature ideas from EDA (to build in Week 4)

| Idea | Evidence |
|---|---|
| Weekday | Saturday ratio 1.27 vs Monday 0.80 |
| Holiday flag | Weekday holidays run 15% to 47% above a normal same-weekday |
| Golden Week window and days to the nearest holiday | holiday_flg missed unflagged days (2 May +0.16, 6 May -0.12) |
| Store's usual closed weekday | 279 stores are missing one weekday more than 80% of the time |
| Store level (own recent average) | Store means range from 1.2 to 115.5 |
| Genre and prefecture | Median store mean from 10.9 to 28.0 across genres; Tokyo-to has 444 of 829 stores |
| History length (cold start) | Some stores have very few rows |
| Reservations known before the forecast date | Use reserve_datetime to avoid leakage |