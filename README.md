
## Overview

This is a solution for the [Forecasting population of Vilnius](https://www.kaggle.com/competitions/forecasting-population-of-vilnius/data)
challenge. In this competition we were asked to predict Vilnius population for different age groups, sex groups, and districts.
Please, check the competition page for more details. 


## Download the data

To run the code locally, you'll need the competition dataset.
You can download it manually or use [kaggle api](https://www.kaggle.com/docs/api):

    kaggle competitions download -c forecasting-population-of-vilnius -p ./data
    unzip ./data/*.zip -d ./data/    

## Data analysis

Before running any algorithm, we analyzed the training data. In the graph below, you can see aggregated population vs date for each age id.
You can check `visualization.ipynb` file for the visualization script. <br>
We concluded, every time step correspond to a month and the jumps each year reflect that some people move from one age group to another.
We also see, that within the year (between jumps) the population is linear.
In the test dataset we have to predict population for 13 timestamp for all groups. That means we need to predict a jump in the 1st test timestamp `as_of_date_id=118`, a line for `as_of_date_id=119:129` , and a final jump for `as_of_date_id=130`.

![img.png](imgs/img.png)

## Solution 

#### Gathering statistics in train
We look at the previous N years and calculate differences between months x_{i} - x_{i-1}. 
Then we apply a gaussian filter to smooth differences and put them to the corresponding accumulator. 
Accomplishing that we calculate "step" scales for every first month of the year:

`step_scale = (x_{i-1} - x_{i} - smoothed(x_{i-1 ... i-10})) / x{i-1}`, 
where `i` corresponds to the first month of the current year and `i-1` to the last month of the year before. 

#### Predicting the first month `as_of_date_id=118`: <br>
We take the last `count` of the last year and add a step size. The step size we compute as follows: again, we take the last `count` of the last year and multiply it by a scale. 
The scale in its turn is an average scale over past year steps. This results in the formula:

    scale = mean(train_step_scales)
    test[118] = train[117]  + train[117] * scale + average_monthly_increase 

We update accumulators accordingly.

#### Predicting following months `as_of_date_id=119:129`: <br>
Then, iterating we add averaged smoothed differences of the previous months to get next month prediction. We also update accumulators accordingly.

#### Predicting the first month `as_of_date_id=130`: <br>
And for the last "step", the beginning of the next year, we're doing the same as for the first, but calculating the "step" size relative to the last month of the predicted year.

Used algorithms: 
* gaussian filter
* mean value of the array

You can check `synthetic_with_fixed_steps.py` for more details regarding the implementation.

## Results

The graphs below show the aggregated predicted values ('--') vs date for each age group as well as train count (plain). <br>

The prediction scored 47.548 on the public part of the test set.

![img_1.png](imgs/img_1.png)