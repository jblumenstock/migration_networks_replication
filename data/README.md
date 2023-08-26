# Input data required for replication

This folder lists all the input data and output data for each figure and table in the paper. 

Note that all the files have a header row except for the following three files:
- The file `0801_call.txt` doesn't have a header because it is the raw file of call records. Each row has a format of `user_1|user_2`, meaning user_1 made a call to user_2.
- The file `0801_mobility.txt` doesn't have a header because it is the raw file of mobility. Each row has a format of `user_id|date|time|tower_id`.
- The file `0801_modal_district.txt` doesn't have a header because it is an intermediate file of migration detection. Each row has a format of `userid_month_date_days    district`.
