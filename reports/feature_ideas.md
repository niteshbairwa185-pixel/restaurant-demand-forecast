# Feature ideas from EDA

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
| Same-weekday history anchored at the forecast start (for example the average of the last 4 same weekdays before the forecast date, and lag 7 and lag 14 only where available) | Autocorrelation of daily average visitors is 0.77 at lag 7 and 0.69 at lag 14. A 39-day horizon means plain lag_7 is not known for most test days |