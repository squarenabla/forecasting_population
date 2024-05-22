
import numpy as np
import pandas as pd
from scipy.ndimage import *

data = pd.read_csv('./data/train.csv')


# Gather statistics
detailed_mean_change = {}
detailed_age_bin_diffs = {}
for k in range(3):
    for age in range(6):

        if age not in detailed_age_bin_diffs:
            detailed_age_bin_diffs[age] = {}
        if age not in detailed_mean_change:
            detailed_mean_change[age] = {}

        for dist in range(21):

            if dist not in detailed_age_bin_diffs[age]:
                detailed_age_bin_diffs[age][dist] = {}
            if dist not in detailed_mean_change[age]:
                detailed_mean_change[age][dist] = {}

            for gender in [0, 1]:
                # Monthly change 
                deltas = []
                for i in range(10, -1, -1):

                    a = np.array(data.loc[(data.district_id==dist) & (data.gender_id==gender) & (data.age_bin_id==age) & (data.as_of_date_id == 117-0-i-12*k), 'count'])
                    b = np.array(data.loc[(data.district_id==dist) & (data.gender_id==gender) & (data.age_bin_id==age) & (data.as_of_date_id == 117-1-i-12*k), 'count'])
                    deltas.append((a - b))
                    
                if gender not in detailed_mean_change[age][dist]:
                    detailed_mean_change[age][dist][gender] = []
                    
                detailed_mean_change[age][dist][gender] += gaussian_filter1d(np.reshape(np.array(deltas), [-1]), 1.5, mode='nearest').tolist()
                
                # "Step"
                a = np.array(data.loc[(data.district_id==dist) & (data.gender_id==gender) & (data.age_bin_id==age) & (data.as_of_date_id == 117-12-12*k), 'count'])
                b = np.array(data.loc[(data.district_id==dist) & (data.gender_id==gender) & (data.age_bin_id==age) & (data.as_of_date_id == 117-11-12*k), 'count']) 
                
                diff = b - a - np.mean(gaussian_filter1d(np.reshape(np.array(deltas), [-1]), 1.5, mode='nearest').tolist())
               
                if gender not in detailed_age_bin_diffs[age][dist]:
                    detailed_age_bin_diffs[age][dist][gender] = []
                detailed_age_bin_diffs[age][dist][gender].append(diff/a)


test = pd.read_csv('./data/test.csv')
test['count'] = 0

# Generating submission.
#
# 118 - beginning of the year, we should predict the "step"
for age in range(6):
    for dist in range(21):
        for gender in [0, 1]:

            pred = np.mean(detailed_age_bin_diffs[age][dist][gender])
            predm = np.mean(np.reshape(np.array(detailed_mean_change[age][dist][gender]), [-1]))

            detailed_mean_change[age][dist][gender].append(predm)
            detailed_mean_change[age][dist][gender] = detailed_mean_change[age][dist][gender][1:]

            test.loc[(test.district_id==dist) & (test.gender_id==gender) & (test.age_bin_id==age) & (test.as_of_date_id == 118), 'count'] = \
                np.array(data.loc[(data.district_id==dist) & (data.gender_id==gender) & (data.age_bin_id==age) & (data.as_of_date_id == 117), 'count']) + predm + \
                np.array(data.loc[(data.district_id==dist) & (data.gender_id==gender) & (data.age_bin_id==age) & (data.as_of_date_id == 117), 'count']) * pred


# 119-129 - regular increase
for age in range(6):
    for dist in range(21):
        for gender in [0, 1]:
            
            predm = np.mean(np.reshape(np.array(detailed_mean_change[age][dist][gender]), [-1]))

            detailed_mean_change[age][dist][gender].append([predm])
            detailed_mean_change[age][dist][gender] = detailed_mean_change[age][dist][gender][1:]

            for ts in range(1, 12):
                test.loc[(test.district_id==dist) & (test.gender_id==gender) & (test.age_bin_id==age) & (test.as_of_date_id == 118 + ts), 'count'] = \
                    np.array(test.loc[(test.district_id==dist) & (test.gender_id==gender) & (test.age_bin_id==age) & (test.as_of_date_id == 118 + ts - 1), 'count']) + predm


# 130 - beginning of the year, we should predict the "step"
for age in range(6):
    for dist in range(21):
        for gender in [0, 1]:
            pred_ = np.mean(detailed_age_bin_diffs[age][dist][gender])
            detailed_age_bin_diffs[age][dist][gender].append([pred_])
            detailed_age_bin_diffs[age][dist][gender] = detailed_age_bin_diffs[age][dist][gender][1:]
            pred = np.mean(detailed_age_bin_diffs[age][dist][gender])

            predm = np.mean(np.reshape(np.array(detailed_mean_change[age][dist][gender]), [-1]))
            detailed_mean_change[age][dist][gender].append([predm])
            detailed_mean_change[age][dist][gender] = detailed_mean_change[age][dist][gender][1:]


            test.loc[(test.district_id==dist) & (test.gender_id==gender) & (test.age_bin_id==age) & (test.as_of_date_id == 130), 'count'] = \
                np.array(test.loc[(test.district_id==dist) & (test.gender_id==gender) & (test.age_bin_id==age) & (test.as_of_date_id == 129), 'count']) + predm + \
                np.array(test.loc[(test.district_id==dist) & (test.gender_id==gender) & (test.age_bin_id==age) & (test.as_of_date_id == 129), 'count']) * pred
            

sub = pd.read_csv('./data/sample_submission.csv', index_col='ID')
sub['count'] = 0

for i in range(sub.shape[0]):
    sub['count'].loc[i] = np.array(test['count'].loc[i])

sub.to_csv('last.csv')
