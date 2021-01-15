# Milestone-3---Noice-Team

## Description of the pipline
The pilpine consists of three stages which are extract, transform, and load.
extract: here we fetch the 20 tweets for finland and Togo and add them to the tweets collected so far and the return of this function is the 2 arrayes and each array represints the tweets a countries.
transform: here we take as input the 2 arrayes from the function extract and apply sentiment to tweets collected so far and output the average of them.
load: here we take as input the average of the sentiment of the two countries so far and write them in a CSV file for every day.
We set the schedule_interval to @daily to make the pipline to be runned once every day and set the start and end date to make it run for 4 days and we set chatchup to true.
