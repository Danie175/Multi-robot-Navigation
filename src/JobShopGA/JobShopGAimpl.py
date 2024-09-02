import random
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.stats import rankdata
from job import Job
from machine import Machine
from operation import Operation
from chromosome import Chromosome
import time
import os
from datetime import datetime
from amr import AMR
import json

import traceback
import inspect



'''
Parameters are HERE
'''
m = 4
n = 3  
num_amrs = 2
N = 350
pc = 0.7
pm = 0.5
pswap = 0.5
pinv = 0.5
T = 100

activate_termination = 0
enable_travel_time = 0
display_convergence = 0
display_schedule = 0
create_txt_file = 0
update_json_file = 1


converged_at = 0
'''
INSTANCE DATA FOR JOB SHOP
'''

# Pinedo book first example
machine_data = [0,1,2,3, 1,0,3,2, 0,1,3,2]
ptime_data = [10,8,4,0, 4,3,5,6, 4,7,3,0]

#Pinedo Book second example
# machine_data = [0,1,2,3, 0,1,3,2, 2,0,1,3]
# ptime_data = [9,8,4,0, 5,6,3,0, 10,4,9,0]


# machine_data = [0,1,2,3,4, 1,0,3,2,4, 0,1,3,2,4, 1,3,4,2,3]
# ptime_data = [10,8,4,0,2, 4,3,5,6,3, 4,7,3,0,0, 0,2,4,5,3]

# E. Taillard Benchmark first instance 15*15

# seed_value = 398197754
# random.seed(seed_value) 
# machine_data = [6, 12, 4, 7, 3, 2, 10, 11, 8, 14, 9, 13, 5, 0, 1, 4, 5, 7, 14, 13, 8, 11, 9, 6, 10, 0, 3, 12, 1, 2, 1, 8, 9, 12, 6, 11, 13, 5, 0, 2, 7, 10, 4, 3, 14, 5, 2, 9, 6, 10, 0, 13, 4, 7, 14, 11, 8, 12, 1, 3, 7, 8, 6, 10, 4, 9, 2, 14, 12, 5, 1, 13, 11, 0, 3, 5, 3, 12, 13, 11, 4, 14, 7, 2, 1, 10, 0, 9, 6, 8, 12, 3, 7, 8, 14, 6, 1, 11, 4, 5, 2, 10, 0, 13, 9, 11, 5, 0, 7, 12, 13, 14, 1, 2, 8, 4, 3, 9, 6, 10, 10, 11, 6, 14, 0, 1, 2, 5, 12, 4, 8, 7, 9, 13, 3, 6, 11, 9, 2, 8, 0, 13, 3, 10, 7, 1, 12, 14, 4, 5, 4, 7, 13, 0, 5, 12, 6, 8, 14, 10, 3, 1, 11, 9, 2, 2, 14, 0, 12, 6, 10, 7, 5, 8, 9, 13, 1, 3, 11, 4, 5, 8, 10, 2, 3, 6, 9, 0, 13, 4, 1, 11, 12, 7, 14, 8, 14, 4, 13, 5, 6, 9, 1, 12, 7, 11, 10, 3, 2, 0, 10, 8, 12, 6, 4, 1, 13, 14, 11, 0, 7, 3, 2, 9, 5]

# ptime_data = [94, 66, 10, 53, 26, 15, 65, 82, 10, 27, 93, 92, 96, 70, 83, 74, 31, 88, 51, 57, 78, 8, 7, 91, 79, 18, 51, 18, 99, 33, 4, 82, 40, 86, 50, 54, 21, 6, 54, 68, 82, 20, 39, 35, 68, 73, 23, 30, 30, 53, 94, 58, 93, 32, 91, 30, 56, 27, 92, 9, 78, 23, 21, 60, 36, 29, 95, 99, 79, 76, 93, 42, 52, 42, 96, 29, 61, 88, 70, 16, 31, 65, 83, 78, 26, 50, 87, 62, 14, 30, 18, 75, 20, 4, 91, 68, 19, 54, 85, 73, 43, 24, 37, 87, 66, 32, 52, 9, 49, 61, 35, 99, 62, 6, 62, 7, 80, 3, 57, 7, 85, 30, 96, 91, 13, 87, 82, 83, 78, 56, 85, 8, 66, 88, 15, 5, 59, 30, 60, 41, 17, 66, 89, 78, 88, 69, 45, 82, 6, 13, 90, 27, 1, 8, 91, 80, 89, 49, 32, 28, 90, 93, 6, 35, 73, 47, 43, 75, 8, 51, 3, 84, 34, 28, 60, 69, 45, 67, 58, 87, 65, 62, 97, 20, 31, 33, 33, 77, 50, 80, 48, 90, 75, 96, 44, 28, 21, 51, 75, 17, 89, 59, 56, 63, 18, 17, 30, 16, 7, 35, 57, 16, 42, 34, 37, 26, 68, 73, 5, 8, 12, 87, 83, 20, 97]

# second instance 15*15
# machine_data = [9, 14, 4, 13, 10, 3, 7, 8, 0, 5, 1, 2, 12, 6, 11, 10, 8, 11, 14, 3, 13, 9, 7, 4, 2, 6, 1, 5, 12, 0, 7, 0, 6, 5, 14, 13, 2, 11, 4, 12, 1, 9, 3, 10, 8, 9, 11, 14, 0, 1, 8, 5, 10, 12, 4, 13, 3, 6, 7, 2, 11, 4, 13, 3, 8, 1, 10, 12, 2, 14, 6, 7, 0, 9, 5, 5, 2, 1, 10, 0, 4, 8, 14, 6, 3, 9, 7, 11, 12, 13, 5, 10, 13, 0, 9, 8, 1, 11, 14, 7, 12, 2, 6, 4, 3, 12, 0, 9, 3, 13, 6, 5, 7, 2, 14, 11, 8, 10, 1, 4, 11, 10, 5, 13, 1, 9, 8, 7, 3, 6, 0, 2, 14, 12, 4, 2, 14, 3, 10, 6, 1, 0, 13, 11, 4, 5, 8, 7, 12, 9, 11, 14, 13, 5, 4, 9, 1, 6, 12, 0, 2, 8, 10, 3, 7, 12, 3, 10, 8, 4, 7, 13, 11, 14, 1, 2, 0, 5, 6, 9, 8, 13, 5, 0, 11, 9, 4, 12, 1, 10, 6, 2, 7, 14, 3, 2, 5, 4, 3, 9, 1, 11, 13, 7, 6, 10, 14, 0, 8, 12, 1, 10, 4, 2, 0, 7, 6, 9, 11, 12, 5, 14, 3, 13, 8]

# ptime_data = [86, 60, 10, 59, 65, 94, 71, 25, 98, 49, 43, 8, 90, 21, 73, 68, 28, 38, 36, 93, 35, 37, 28, 62, 86, 65, 11, 20, 82, 23, 33, 67, 96, 91, 83, 81, 60, 88, 20, 62, 22, 79, 38, 40, 82, 13, 14, 73, 88, 24, 16, 78, 70, 53, 68, 73, 90, 58, 7, 4, 93, 52, 63, 13, 19, 41, 71, 59, 19, 60, 85, 99, 73, 95, 19, 62, 60, 93, 16, 10, 72, 88, 69, 58, 41, 46, 63, 76, 83, 62, 50, 68, 90, 34, 44, 5, 8, 25, 70, 53, 78, 92, 62, 85, 70, 60, 64, 92, 44, 63, 91, 21, 1, 96, 19, 59, 12, 41, 11, 94, 93, 46, 51, 37, 91, 90, 63, 40, 68, 13, 16, 83, 49, 24, 23, 5, 35, 21, 14, 66, 3, 6, 98, 63, 64, 76, 94, 17, 62, 37, 35, 42, 62, 68, 73, 27, 52, 39, 41, 25, 9, 34, 50, 41, 98, 23, 32, 35, 10, 29, 68, 20, 8, 58, 62, 39, 32, 8, 33, 91, 28, 31, 3, 28, 66, 59, 24, 45, 81, 8, 44, 42, 2, 23, 53, 11, 93, 27, 59, 62, 23, 23, 7, 77, 64, 60, 97, 36, 53, 72, 36, 98, 38, 24, 84, 47, 72, 1, 91, 85, 68, 42, 20, 30, 30]


# E. Taillard Benchmark first instance 20*15

# ptime_data = [25, 75, 75, 76, 38, 62, 38, 59, 14, 13, 46, 31, 57, 92, 3, 67, 5, 11, 11, 40, 34, 77, 42, 35, 96, 22, 55, 21, 29, 16, 22, 98, 8, 35, 59, 31, 13, 46, 52, 22, 18, 19, 64, 29, 70, 99, 42, 2, 35, 11, 92, 88, 97, 21, 56, 17, 43, 27, 19, 23, 50, 5, 59, 71, 47, 39, 82, 35, 12, 2, 39, 42, 52, 65, 35, 48, 57, 5, 2, 60, 64, 86, 3, 51, 26, 34, 39, 45, 63, 54, 40, 43, 50, 71, 46, 99, 67, 34, 6, 95, 67, 54, 29, 30, 60, 59, 3, 85, 6, 46, 49, 5, 82, 18, 71, 48, 79, 62, 65, 76, 65, 55, 81, 15, 32, 52, 97, 69, 82, 89, 69, 87, 22, 71, 63, 70, 74, 52, 94, 14, 81, 24, 14, 32, 39, 67, 59, 18, 77, 50, 18, 6, 96, 53, 35, 99, 39, 18, 14, 90, 64, 81, 89, 48, 80, 44, 75, 12, 13, 74, 59, 71, 75, 30, 93, 26, 30, 84, 91, 93, 39, 56, 13, 29, 55, 69, 26, 7, 55, 48, 22, 46, 50, 96, 17, 57, 14, 8, 13, 95, 53, 78, 24, 92, 90, 68, 87, 43, 75, 94, 93, 92, 18, 28, 27, 40, 56, 83, 51, 15, 97, 48, 53, 78, 39, 47, 34, 42, 28, 11, 11, 30, 14, 10, 4, 20, 92, 19, 59, 28, 69, 82, 64, 40, 27, 82, 27, 43, 56, 17, 18, 20, 98, 43, 68, 84, 26, 87, 61, 95, 23, 88, 89, 49, 84, 12, 51, 3, 44, 20, 43, 54, 18, 72, 70, 28, 20, 22, 59, 36, 85, 13, 73, 29, 45, 7, 97, 4, 22, 74, 45, 62, 95, 66, 14, 40, 23, 79, 34, 8]

# machine_data = [3, 11, 14, 1, 10, 2, 4, 7, 0, 12, 5, 9, 6, 13, 8, 5, 0, 3, 8, 4, 1, 12, 14, 6, 7, 10, 2, 9, 13, 11, 2, 3, 14, 0, 9, 12, 5, 4, 7, 10, 8, 11, 13, 1, 6, 8, 10, 1, 13, 3, 4, 14, 9, 2, 5, 11, 7, 0, 6, 12, 14, 8, 1, 2, 10, 9, 12, 4, 6, 5, 0, 13, 3, 11, 7, 3, 10, 1, 5, 6, 0, 8, 7, 11, 13, 2, 14, 12, 9, 4, 2, 10, 1, 12, 8, 0, 7, 6, 14, 13, 4, 3, 5, 9, 11, 1, 0, 2, 4, 7, 13, 11, 3, 12, 5, 6, 14, 9, 8, 10, 4, 5, 9, 10, 7, 6, 2, 1, 12, 3, 13, 0, 8, 14, 11, 1, 4, 3, 10, 14, 0, 6, 13, 11, 8, 5, 12, 7, 9, 2, 3, 10, 1, 0, 9, 8, 14, 6, 4, 7, 2, 12, 5, 11, 13, 2, 7, 6, 8, 3, 5, 14, 4, 1, 0, 9, 10, 13, 11, 12, 0, 7, 14, 8, 12, 10, 9, 3, 6, 1, 4, 2, 11, 13, 5, 12, 3, 9, 4, 1, 0, 10, 6, 5, 2, 14, 13, 7, 8, 11, 3, 14, 6, 5, 13, 9, 1, 0, 12, 7, 2, 4, 10, 8, 11, 5, 14, 6, 12, 8, 2, 4, 9, 11, 13, 3, 1, 7, 0, 10, 3, 7, 10, 14, 0, 8, 1, 11, 5, 13, 4, 12, 6, 9, 2, 10, 8, 2, 11, 13, 6, 14, 3, 9, 7, 4, 5, 12, 0, 1, 3, 2, 12, 13, 1, 6, 14, 5, 4, 8, 9, 11, 0, 10, 7, 11, 14, 5, 6, 10, 9, 13, 1, 4, 8, 0, 3, 12, 2, 7]




# FISHER THOMPSON ft06 6*6 
# ptime_data = [1, 3, 6, 7, 3, 6,  8, 5, 10, 10, 10, 4,  5, 4, 8, 9, 1, 7,  5, 5, 5, 3, 8, 9,  9, 3, 5, 4, 3, 1,  3, 3, 9, 10, 4, 1]
# machine_data = [2, 0, 1, 3, 5, 4,  1, 2, 4, 5, 0, 3,  2, 3, 5, 0, 1, 4,  1, 0, 2, 3, 4, 5,  2, 1, 4, 5, 0, 3,  1, 3, 5, 0, 4, 2]

# FISHER THOMPSON ft10 10 * 10
# ptime_data = [
#     29, 78, 9, 36, 49, 11, 62, 56, 44, 21,
#     43, 90, 75, 11, 69, 28, 46, 46, 72, 30,
#     91, 85, 39, 74, 90, 10, 12, 89, 45, 33,
#     81, 95, 71, 99, 9, 52, 85, 98, 22, 43,
#     14, 6, 22, 61, 26, 69, 21, 49, 72, 53,
#     84, 2, 52, 95, 48, 72, 47, 65, 6, 25,
#     46, 37, 61, 13, 32, 21, 32, 89, 30, 55,
#     31, 86, 46, 74, 32, 88, 19, 48, 36, 79,
#     76, 69, 76, 51, 85, 11, 40, 89, 26, 74,
#     85, 13, 61, 7, 64, 76, 47, 52, 90, 45
# ]

# machine_data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 2, 4, 9, 3, 1, 6, 5, 7, 8, 1, 0, 3, 2, 8, 5, 7, 6, 9, 4, 1, 2, 0, 4, 6, 8, 7, 3, 9, 5, 2, 0, 1, 5, 3, 4, 8, 7, 9, 6, 2, 1, 5, 3, 8, 9, 0, 6, 4, 7, 1, 0, 3, 2, 6, 5, 9, 8, 7, 4, 2, 0, 1, 5, 4, 6, 8, 9, 7, 3, 0, 1, 3, 5, 2, 9, 6, 7, 4, 8, 1, 0, 2, 6, 8, 9, 5, 3, 4, 7]


# LAWRENCE la01 10*5
# machine_data = [1, 0, 4, 3, 2,  0, 3, 4, 2, 1,  3, 4, 1, 2, 0,  1, 0, 4, 2, 3,  0, 3, 2, 1, 4,  1, 2, 4, 0, 3,  3, 4, 1, 2, 0,  2, 0, 1, 3, 4,  3, 1, 4, 0, 2,  4, 3, 2, 1, 0]
# ptime_data = [21, 53, 95, 55, 34, 21, 52, 16, 26, 71, 39, 98, 42, 31, 12, 77, 55, 79, 66, 77, 83, 34, 64, 19, 37, 54, 43, 79, 92, 62, 69, 77, 87, 87, 93, 38, 60, 41, 24, 83, 17, 49, 25, 44, 98, 77, 79, 43, 75, 96]

# LAWRENCE la02 10*5
# machine_data = [0, 3, 1, 4, 2, 4, 2, 0, 1, 3, 1, 2, 4, 0, 3, 2, 1, 4, 0, 3, 4, 0, 3, 2, 1, 1, 0, 4, 3, 2, 4, 1, 3, 0, 2, 1, 0, 2, 3, 4, 4, 0, 2, 1, 3, 4, 2, 1, 3, 0]
# ptime_data = [20, 87, 31, 76, 17, 25, 32, 24, 18, 81, 72, 23, 28, 58, 99, 86, 76, 97, 45, 90, 27, 42, 48, 17, 46, 67, 98, 48, 27, 62, 28, 12, 19, 80, 50, 63, 94, 98, 50, 80, 14, 75, 50, 41, 55, 72, 18, 37, 79, 61]

# LAWRENCE la03 10*5
# machine_data =  [1, 2, 0, 4, 3, 2, 1, 0, 4, 3, 2, 3, 4, 0, 1, 4, 0, 2, 1, 3, 4, 0, 1, 3, 2, 4, 0, 1, 2, 3, 3, 2, 0, 4, 1, 4, 1, 0, 2, 3, 4, 0, 3, 2, 1, 4, 1, 0, 2, 3]
# ptime_data = [23, 45, 82, 84, 38, 21, 29, 18, 41, 50, 38, 54, 16, 52, 52, 37, 54, 74, 62, 57, 57, 81, 61, 68, 30, 81, 79, 89, 89, 11, 33, 20, 91, 20, 66, 24, 84, 32, 55, 8, 56, 7, 54, 64, 39, 40, 83, 19, 8, 7]

# LAWRENCE la04 10*5
# machine_data = [0, 2, 3, 4, 1, 1, 3, 4, 2, 0, 1, 0, 3, 4, 2, 2, 4, 0, 3, 1, 1, 3, 4, 0, 2, 3, 2, 0, 4, 1, 2, 1, 0, 3, 4, 1, 3, 0, 4, 2, 2, 4, 0, 1, 3, 2, 4, 3, 1, 0]
# ptime_data = [12, 94, 92, 91, 7, 19, 11, 66, 21, 87, 14, 75, 13, 16, 20, 95, 66, 7, 7, 77, 45, 6, 89, 15, 34, 77, 20, 76, 88, 53, 74, 88, 52, 27, 9, 88, 69, 62, 98, 52, 61, 9, 62, 52, 90, 54, 5, 59, 15, 88]

# LAWRENCE la05 10*5
# machine_data = [1, 0, 4, 2, 3, 4, 3, 0, 2, 1, 1, 3, 2, 0, 4, 0, 3, 4, 1, 2, 4, 2, 3, 1, 0, 3, 0, 4, 1, 2, 0, 3, 1, 4, 2, 4, 2, 3, 1, 0, 2, 3, 1, 0, 4, 2, 3, 0, 4, 1]
# ptime_data = [72, 87, 95, 66, 60, 5, 35, 48, 39, 54, 46, 20, 21, 97, 55, 59, 19, 46, 34, 37, 23, 73, 25, 24, 28, 28, 45, 5, 78, 83, 53, 71, 37, 29, 12, 12, 87, 33, 55, 38, 49, 83, 40, 48, 7, 65, 17, 90, 27, 23]

# LAWRENCE Benchmark  la06 15*5
# ptime_data = [
#     21, 34, 95, 53, 55,
#     52, 16, 71, 26, 21,
#     31, 12, 42, 39, 98,
#     77, 77, 79, 55, 66,
#     37, 34, 64, 19, 83,
#     43, 54, 92, 62, 79,
#     93, 69, 87, 77, 87,
#     60, 41, 38, 83, 24,
#     98, 17, 25, 44, 49,
#     96, 77, 79, 75, 43,
#     28, 35, 95, 76, 7,
#     61, 10, 95, 9, 35,
#     59, 16, 91, 59, 46,
#     43, 52, 28, 27, 50,
#     87, 45, 39, 9, 41
# ]

# machine_data = [1, 2, 4, 0, 3, 3, 4, 1, 2, 0, 2, 0, 1, 3, 4, 3, 1, 4, 0, 2, 4, 3, 2, 1, 0, 2, 1, 0, 3, 4, 0, 3, 1, 4, 2, 0, 1, 2, 4, 3, 2, 3, 4, 0, 1, 0, 4, 3, 1, 2, 4, 2, 0, 3, 1, 0, 4, 2, 1, 3, 4, 3, 1, 2, 0, 4, 1, 0, 2, 3, 0, 1, 2, 4, 3]



'''
Distances between machines for Pinedo book first example
'''

# TEST MATRIX 
# distance_matrix = np.array([
#     [0,2,4,4],
#     [2,0,4,4],
#     [4,4,0,2],
#     [4,4,2,0]
# ])

# WAREHOUSE MATRIX FOR GAZEBO SIMULATION
# distance_matrix = np.array([
#     [0, 5.16, 10.258, 10.258, 6.12, 9.258],
#     [5.16, 0, 10.258, 10.258, 6.12, 9.258],
#     [10.258, 10.258, 0, 5.16, 11.218, 6.86],
#     [10.258, 10.258, 5.16, 0, 11.218, 6.86],
#     [6.12, 6.12, 11.218, 11.218, 0, 10.22],
#     [9.258, 9.258, 6.86, 6.86, 10.22, 0]
# ])


# distance_matrix = np.array([
#     [0,0,0,0,0,0],
#     [0,0,0,0,0,0],
#     [0,0,0,0,0,0],
#     [0,0,0,0,0,0]
# ])



if enable_travel_time:
    # distance_matrix = np.array([
    #     [0, 5.16, 10.258, 10.258, 6.12, 9.258],
    #     [5.16, 0, 10.258, 10.258, 6.12, 9.258],
    #     [10.258, 10.258, 0, 5.16, 11.218, 6.86],
    #     [10.258, 10.258, 5.16, 0, 11.218, 6.86],
    #     [6.12, 6.12, 11.218, 11.218, 0, 10.22],
    #     [9.258, 9.258, 6.86, 6.86, 10.22, 0]
    # ])
    
    # PAPER MATRIX
    distance_matrix = np.array([
        [0, 5, 10, 10, 6, 9],
        [5, 0, 10, 10, 6, 9],
        [10, 10, 0, 5, 11, 6],
        [10, 10, 5, 0, 11, 6],
        [6, 6, 11, 11, 0, 10],
        [9, 9, 6, 6, 10, 0]
    ])
else:
    distance_matrix = np.array([
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0],
    [0,0,0,0,0,0]
])


def get_file(best_chromosome, processing_time, converged_at):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f'la01{timestamp}.docx'             # CHANGE FILE NAME
    if converged_at == 0:
        converged_at = processing_time
    
    directory = '/home/daniel/Multi-robot-Navigation/src/JobShopGA/Results/'        # CHANGE SAVING DIRECTORY
    
    filepath = os.path.join(directory, filename)
    
    
    with open(filepath, 'w') as file:
        file.write(f"Genetic Algorithm Specifications\n")
        file.write("------------------------\n")
        file.write(f'N = {N}, T = {T}, pc = {pc}, pm = {pm}, pswap = {pswap}, pinv = {pinv}, num_amrs {num_amrs}\n')
        file.write(f'Processing time = {processing_time}\n')
        file.write(f'Converged at = {converged_at}\n')
        file.write(f'best Cmax = {best_chromosome.fitness}\n')
        
        file.write(f'random generated numbers:{best_chromosome.encoded_list}\n')
        file.write(f'ranked list : {best_chromosome.ranked_list}\n operation_index :{best_chromosome.operation_index_list}\n')
        file.write(f'machine sequence: {best_chromosome.machine_sequence}\n ptime sequence: {best_chromosome.ptime_sequence}\n Cmax: {best_chromosome.Cmax}\n')


# print out necessary
if len(sys.argv) > 1:
    print_out = sys.argv[1].lower() == 'true'
else:
    # Default value if no command-line argument is provided
    print_out = False
    

def create_operation_data(machine_data, ptime_data, m):
    matrix = []
    sublist = []
    for i in range(len(machine_data)):
        sublist.append([machine_data[i], ptime_data[i]])
        if (i + 1) % m == 0:
            matrix.append(sublist)
            sublist = []
    # Check if there are remaining elements
    if sublist:
        matrix.append(sublist)
    return matrix
    
    # merged_array = np.array([machine_data, ptime_data])

    # # Reshape the array to get the desired format
    # reshaped_array = merged_array.reshape((len(machine_data) // len(set(machine_data)), len(set(machine_data)), 2))
    # return reshaped_array
    
operation_data = create_operation_data(machine_data,ptime_data, m)
print(operation_data)

def assign_operations(jobs, operation_data):
    for job, operation in zip(jobs, operation_data):
        job.operations = operation
    
    

def generate_population(N):
    population = []
    for _ in range(N):
        num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
        population.append(num)
    return population

def integer_list(population):
    ranked_population = []
    for i in range(N):
        sorted_list = []
        ranks = {}
        # Sort the list to get ranks in ascending order
        sorted_list = sorted(population[i])
            
        # Create a dictionary to store the ranks of each float number
        ranks = {value: index + 1 for index, value in enumerate(sorted_list)}
            
        # Convert each float number to its corresponding rank
        rank_list = [ranks[value] for value in population[i]]
        ranked_population.append(rank_list)
        
    return ranked_population

def indiv_integer_list(chromosome):
    # ranked_population = []
    # sorted_list = []
    # ranks = {}
    # # Sort the list to get ranks in ascending order
    # sorted_list = sorted(chromosome)
            
    # # Create a dictionary to store the ranks of each float number
    # ranks = {value: index for index, value in enumerate(sorted_list)}
            
    # # Convert each float number to its corresponding rank
    # rank_list = [ranks[value] for value in chromosome]
    # ranked_population.append(rank_list)
        
    # return rank_list
    
    ranks = rankdata(chromosome)
    return [int(rank - 1) for rank in ranks]

def remove_duplicates(numbers):
    seen = set()
    modified_numbers = []
    
    for num in numbers:
        # Check if the number is already in the set
        if num in seen:
            # Modify the number slightly
            modified_num = num + 0.01
            # Keep modifying until it's unique
            while modified_num in seen:
                modified_num += 0.01
            modified_numbers.append(modified_num)
            seen.add(modified_num)
        else:
            modified_numbers.append(num)
            seen.add(num)
        
    
    return modified_numbers

    
# get job operation sequence
def getJobindex(population):
    new_index = 0
    operation_index_pop = []
    for i in range(N):
        tlist = []
        temp = population[i]
        for j in range(m*n):
            new_index = (temp[j] % n) + 1
            tlist.append(new_index)
        operation_index_pop.append(tlist)
    
    return operation_index_pop

def indiv_getJobindex(chromosome):
    new_index = 0
    operation_index_pop = []

    tlist = []
    temp = chromosome
    for j in range(len(chromosome)):
        new_index = (temp[j] % n)
        tlist.append(new_index)
    operation_index_pop = tlist
    
    return operation_index_pop
    

def schedule_operations(population, jobs):
    operation_list = []
    explored = []
    
    for chromosome in population:
        for i in range(len(chromosome) - 1):
            explored.append(chromosome[i])
            numcount = explored.count(chromosome[i])
            if numcount <= m:
                operation_list.append(jobs[chromosome[i]-1].operations[numcount-1])
    return operation_list

def indiv_schedule_operations(chromosome, jobs):
    operation_list = []
    explored = []
    # print(chromosome)
    # x = Counter(chromosome)
    # for i in x.elements():
    #     print( "% s : % s" % (i, x[i]), end ="\n")
    
    for i in range(len(chromosome)):
        explored.append(chromosome[i])
        numcount = explored.count(chromosome[i])
        # if numcount < m:
        operation_list.append(jobs[chromosome[i]].operations[numcount-1])  # changed chromosome[i] to chromosome[i]-1
    return operation_list
            
# gives each operation a job number of whihc job it is part of
def install_operations(jobs):
    for job in jobs:
        job.operations = [Operation(job.job_number) for i in range(m)]

# operation_data = create_operation_data(machine_data,ptime_data, m)

def assign_data_to_operations(jobs, operation_data):
    for job,sublist in zip(jobs, operation_data):
        for operation,i in zip(job.operations, range(m)):
            operation.operation_number = i
            operation.machine = sublist[i][0]
            operation.Pj = sublist[i][1]
            
# def assign_amrs_to_jobs(jobs, amrs, operation_index_list):
#     t_operations = set(operation_index_list)
#     for num in t_operations:
#         jobs[num].amr_number = random.randint(0, num_amrs - 1)
#         amrs[jobs[num].amr_number].assigned_jobs.append(jobs[num].job_number)
        
def assign_amrs_to_jobs(jobs, amrs, amr_assignments):
    for job, amr_num in zip(jobs, amr_assignments):
        job.amr_number = amr_num
        amrs[job.amr_number].assigned_jobs.append(job.job_number)
        
        
def get_amr_assignments():
    amr_assignments = []
    for num in range(n):
        amr_num = random.randint(0,num_amrs - 1)
        amr_assignments.append(amr_num)
        
    return amr_assignments
            
            
def get_machine_sequence(operation_schedule):
    machine_sequence = []
    for operation in operation_schedule:
        machine_sequence.append(operation.machine)
        
    return machine_sequence

def get_processing_times(operation_schedule):
    ptime_sequence = []
    for operation in operation_schedule:
        ptime_sequence.append(operation.Pj)
        
    return ptime_sequence

def calculate_Cj(operation_schedule, machines, jobs, machine_sequence, ptime_sequence):
    for operation in operation_schedule:
        if operation.operation_number == 0:
            operation.start_time = machines[operation.machine].finish_operation_time
            operation.Cj = operation.start_time + operation.Pj
            machines[operation.machine].finish_operation_time = operation.Cj
            # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
            
        else:
            if jobs[operation.job_number].operations[operation.operation_number - 1].Cj < machines[operation.machine].finish_operation_time:
                operation.start_time = machines[operation.machine].finish_operation_time
                operation.Cj = operation.start_time + operation.Pj
                machines[operation.machine].finish_operation_time = operation.Cj
                # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                
            else:
                operation.start_time = jobs[operation.job_number].operations[operation.operation_number - 1].Cj
                operation.Cj = operation.start_time + operation.Pj
                if operation.Pj != 0:
                    machines[operation.machine].finish_operation_time = operation.Cj
                # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                

'''
The Cj is calculated by adding up the times of machine processes, and travel times across each machine.
Edge cases solved:
-A different job completed before travel time of first job to the same machine.
-Two jobs on different AMRs at the same machine (travel time delay is not to be considered)
-When a job have number of operations < m (is not processed on all machines)
'''

def calculate_Cj_with_amr(operation_schedule, machines, jobs, amrs):
    t_op = operation_schedule
    skipped = []
    while t_op != []:
        # print('running')
        for operation in t_op:
            # CHECK IF AMR IS ASSIGNED TO A JOB, ONLY ASSIGN IF THE OPERATION NUMBER IS ZERO
            if amrs[jobs[operation.job_number].amr_number].current_job == None and operation.operation_number == 0:
                amrs[jobs[operation.job_number].amr_number].current_job = operation.job_number
                amrs[jobs[operation.job_number].amr_number].job_objects.append(jobs[operation.job_number]) # APPEND JOB OBJECTS
                # IF AMR JUST COMPLETED A JOB UPDATE THE NEXT JOBS MACHINE START TO THE TIME WHEN AMR COMPLETED PREVIOUS JOB
                if machines[operation.machine].finish_operation_time < amrs[jobs[operation.job_number].amr_number].job_completion_time:
                    machines[operation.machine].finish_operation_time = amrs[jobs[operation.job_number].amr_number].job_completion_time
                
                
            # CHECK IF AMR IS CURRENTLY PROCESSING THIS JOB
            if operation.job_number == amrs[jobs[operation.job_number].amr_number].current_job:
                
                if operation.operation_number == 0:
                    if amrs[jobs[operation.job_number].amr_number].completed_jobs == []:
                        operation.start_time = machines[operation.machine].finish_operation_time
                    else:
                        # MAKE SURE THE PREVIOUS JOBS TRAVEL TIME SHOULD BE GIVEN TO NEXT JOB IF M'TH JOB IS HAVING PJ = 0
                        i = 0
                        while jobs[amrs[jobs[operation.job_number].amr_number].completed_jobs[-1]].operations[m-i-1].Pj == 0:
                            i+=1   
                        operation.start_time = machines[operation.machine].finish_operation_time + jobs[amrs[jobs[operation.job_number].amr_number].completed_jobs[-1]].operations[m-i-1].travel_time
                        
                    jobs[operation.job_number].job_start_time = operation.start_time # SET JOB START TIME
                    operation.Cj = operation.start_time + operation.Pj
                    machines[operation.machine].finish_operation_time = operation.Cj
                    # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                    
                    
                else:
                    # IF MACHINE RUN TIME IS LESSER THAN JOB COMPLETION TIME AND TRAVEL TIME FROM PREVIOUS LOCATION COMBINED.
                    if jobs[operation.job_number].operations[operation.operation_number - 1].Cj + jobs[operation.job_number].operations[operation.operation_number - 1].travel_time < machines[operation.machine].  finish_operation_time:
                        operation.start_time = machines[operation.machine].finish_operation_time
                        operation.Cj = operation.start_time + operation.Pj
                        machines[operation.machine].finish_operation_time = operation.Cj 
                        # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                        
                    else:
                        operation.start_time = jobs[operation.job_number].operations[operation.operation_number - 1].Cj + jobs[operation.job_number].operations[operation.operation_number - 1].travel_time
                        operation.Cj = operation.start_time + operation.Pj
                        if operation.Pj != 0:
                            machines[operation.machine].finish_operation_time = operation.Cj
                        # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                
                
            # SKIP THE JOB AND RETURN TO IT LATER
            else:
                skipped.append(operation)
            
            # UPDATE PARAMETERS ONCE A JOB IS COMPLETED
            if operation.operation_number == m - 1 and amrs[jobs[operation.job_number].amr_number].current_job == operation.job_number:
                        amrs[jobs[operation.job_number].amr_number].current_job = None
                        if amrs[jobs[operation.job_number].amr_number].assigned_jobs != []:
                            amrs[jobs[operation.job_number].amr_number].assigned_jobs.remove(operation.job_number)
                        amrs[jobs[operation.job_number].amr_number].completed_jobs.append(operation.job_number)
                        # IF FINAL JOB PJ IS ZERO TAKE PREV COMPLETED TIME
                        if operation.Pj != 0:
                            amrs[jobs[operation.job_number].amr_number].job_completion_time = operation.Cj
                            jobs[operation.job_number].job_completion_time = amrs[jobs[operation.job_number].amr_number].job_completion_time
                        else:
                            i = 0
                            while jobs[operation.job_number].operations[operation.operation_number - i].Pj == 0:
                                i += 1
                            amrs[jobs[operation.job_number].amr_number].job_completion_time = jobs[operation.job_number].operations[operation.operation_number -  i].Cj
                        jobs[operation.job_number].job_completion_time = amrs[jobs[operation.job_number].amr_number].job_completion_time
                
        t_op = skipped
        skipped = []
    # eof while

def assign_machine_operationlist(machines, operation_schedule):
    for operation in operation_schedule:
        machines[operation.machine].operationlist.append(operation)

def get_Cmax(machines):
    runtimes = []
    for machine in machines:
        runtimes.append(machine.finish_operation_time)
        
    return max(runtimes)


# def process_chromosome(chromosome, amr_assignments):
    
#     # print(operation_data)
#     jobs = [Job(number) for number in range(n)]
#     machines = [Machine(number) for number in range(m)]
#     amrs = [AMR(number) for number in range(num_amrs)]
#     assign_operations(jobs, operation_data)
    
#     ranked_list = indiv_integer_list(chromosome)
#     operation_index_list = indiv_getJobindex(ranked_list)
    
#     # CASE 1
#     # operation_index_list = [1, 2, 0, 1, 2, 0, 2, 0, 1, 0, 2, 1]
    
    
#     install_operations(jobs)
#     assign_data_to_operations(jobs, operation_data)
#     operation_schedule = indiv_schedule_operations(operation_index_list, jobs)
#     # assign_amrs_to_jobs(jobs, amrs, amr_assignments)
    
#     # get the sequence of machines
#     machine_sequence = get_machine_sequence(operation_schedule)
    
#     # get the sequence of processing times
#     ptime_sequence = get_processing_times(operation_schedule)
    
#     # calculate_Cj(operation_schedule, machines, jobs)
#     calculate_Cj_with_amr(operation_schedule, machines, jobs, amrs)
#     assign_machine_operationlist(machines, operation_schedule)
#     Cmax = get_Cmax(machines)
    
#     chromosome = Chromosome(chromosome)
        
#     chromosome.ranked_list = ranked_list
#     chromosome.operation_index_list = operation_index_list
#     chromosome.job_list = jobs
#     chromosome.amr_list = amrs
#     chromosome.operation_schedule = operation_schedule
#     chromosome.machine_sequence = machine_sequence
#     chromosome.machine_list = machines
#     chromosome.ptime_sequence = ptime_sequence
#     chromosome.Cmax = Cmax
    
#     return chromosome

def check_list_length(my_list):
    
    
    try:
        if len(my_list) != m*n:
            raise ValueError(f"List length is not {m*n}")
        # print("List length is 12")
    except ValueError as e:
        print(f"Error: {e}")
        print(len(my_list))
        tb = traceback.format_exc()
        print("Traceback:\n", tb)
        stack = inspect.stack()
        print("Call stack:")
        for frame in stack:
            print(f"File: {frame.filename}, Line: {frame.lineno}, Function: {frame.function}")
        
# def get_travel_time(jobs, amrs, distance_matrix):
    
def get_travel_time(jobs, amrs, distance_matrix):
    for job in jobs:
        for operation in job.operations:
            operation.travel_time = operation.calculate_travel_time(amrs, jobs, distance_matrix, enable_travel_time)
            
            
'''
Single function to completely process an individual chromosome.
'''

def process_chromosome(chromosome, amr_assignments):
    
    # print(operation_data)
    jobs = [Job(number) for number in range(n)]
    machines = [Machine(number) for number in range(m)]
    amrs = [AMR(number) for number in range(num_amrs)]
    assign_operations(jobs, operation_data)
    
    chromosome = remove_duplicates(chromosome)
    # print(chromosome)
    ranked_list = indiv_integer_list(chromosome)
    # print(ranked_list)
    operation_index_list = indiv_getJobindex(ranked_list)
    
    # CASE 1
    # operation_index_list = [1, 2, 0, 1, 2, 0, 2, 0, 1, 0, 2, 1]
    
    
    install_operations(jobs)
    assign_data_to_operations(jobs, operation_data)
    # check_list_length(operation_index_list)
    
    operation_schedule = indiv_schedule_operations(operation_index_list, jobs)    # HERE IS THE MF ERROR
    check_list_length(operation_schedule)
    assign_amrs_to_jobs(jobs, amrs, amr_assignments)
    
    # get the sequence of machines
    machine_sequence = get_machine_sequence(operation_schedule)
    
    # get the sequence of processing times
    ptime_sequence = get_processing_times(operation_schedule)
    
    # SET TRAVEL TIMES FOR EACH JOB
    get_travel_time(jobs, amrs, distance_matrix)
    
    # calculate_Cj(operation_schedule, machines, jobs)
    calculate_Cj_with_amr(operation_schedule, machines, jobs, amrs)
    assign_machine_operationlist(machines, operation_schedule)
    Cmax = get_Cmax(machines)
    
    chromosome = Chromosome(chromosome)
        
    chromosome.ranked_list = ranked_list
    chromosome.operation_index_list = operation_index_list
    chromosome.job_list = jobs
    chromosome.amr_list = amrs
    chromosome.operation_schedule = operation_schedule
    chromosome.machine_sequence = machine_sequence
    chromosome.machine_list = machines
    chromosome.ptime_sequence = ptime_sequence
    chromosome.Cmax = Cmax
    chromosome.fitness = chromosome.Cmax + chromosome.penalty
    
    return chromosome

def PlotGanttChar (chromosome):
        # ------------------------------
        # Figure and set of subplots
        
    
    Cmax = chromosome.Cmax
    fig, ax = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(10)
    # ylim and xlim of the axes
    ax.set_ylabel('Machine', fontweight ='bold', loc='top', color='magenta', fontsize=16)
    ax.set_ylim(-0.5, m-0.5)
    ax.set_yticks(range(m), minor=False)
    ax.set_yticklabels(range(1, m + 1), minor=False)
    ax.tick_params(axis='y', labelcolor='magenta', labelsize=16)
        
    ax.set_xlabel('Time', fontweight ='bold', loc='right', color='red', fontsize=16)
    ax.set_xlim(0, Cmax+2)
        
    ax.tick_params(axis='x', labelcolor='red', labelsize=16)
        
    ax.grid(True)
        
    tmpTitle = 'Job Shop Scheduling (m={:02d}; n={:03d}; Utilization={:04d})'.format(m, n, Cmax)
    plt.title(tmpTitle, size=20, color='blue')
        
    colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta','blue','green','silver','purple', 'cyan']
        
        
    for i in range (m):
        joblen = len(chromosome.machine_list[i].operationlist)
        for k in range(joblen):
            j = chromosome.machine_list[i].operationlist[k]
            ST = j.start_time
            cIndx = 0
            # cIndx = k%(n*N)
            if j.Pj != 0:
                ax.broken_barh([(ST, j.Pj)], (-0.3+i, 0.6), facecolor=colors[j.job_number], linewidth=1, edgecolor='black')
                ax.text((ST + (j.Pj)/2), (i), '{}'.format(j.job_number + 1), fontsize=18)
    
    
'''
Plots a gantt chart along with AMR constraints applied.
'''
def PlotGanttChar_with_amr(chromosome):

    # Get the makespan (Cmax) from the chromosome
    Cmax = chromosome.Cmax

    # Figure and set of subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [8, 1]})
    
    # Bottom Gantt chart (main)
    ax = axs[0]
    ax.set_ylabel('Machine', fontweight='bold', loc='top', color='magenta', fontsize=16)
    ax.set_ylim(-0.5, m - 0.5)
    ax.set_yticks(range(m), minor=False)
    ax.tick_params(axis='y', labelcolor='magenta', labelsize=16)
    
    ax.set_xlim(0, Cmax + 2)
    ax.tick_params(axis='x', labelcolor='red', labelsize=16)
    ax.grid(True)

    tmpTitle = f'Job Shop Scheduling (m={m}; n={n}; AMRs:{num_amrs}; Cmax={round(Cmax, 2)}; )'
    ax.set_title(tmpTitle, size=20, color='blue')

    colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta', 'blue', 'green', 'silver']

    for i in range(m):
        joblen = len(chromosome.machine_list[i].operationlist)
        for k in range(joblen):
            j = chromosome.machine_list[i].operationlist[k]
            ST = j.start_time
            if j.Pj != 0:
                ax.broken_barh([(ST, j.Pj)], (-0.3 + i, 0.6), facecolor=colors[j.job_number], linewidth=1, edgecolor='black')
                ax.broken_barh([(j.Cj, j.travel_time)], (-0.3 + i, 0.6), facecolor='black', linewidth=1, edgecolor='black')
                
                ax.text(ST + (j.Pj / 2 - 0.3), i + 0.03, '{}'.format(j.job_number), fontsize=18)
    
    
    # Top Gantt chart with custom y-ticks
    top_ax = axs[1]
    top_ax.set_ylabel('AMRs', fontweight='bold', loc='top', color='magenta', fontsize=16)
    top_ax.set_xlabel('Time', fontweight='bold', loc='right', color='red', fontsize=16)
    top_ax.set_ylim(-0.5, num_amrs - 0.5)
    top_ax.set_yticks(range(num_amrs), minor=False)
    top_ax.tick_params(axis='y', labelcolor='magenta', labelsize=16)
    top_ax.set_xlim(0, Cmax + 2)
    top_ax.tick_params(axis='x', labelcolor='red', labelsize=16)
    top_ax.grid(True)

    # Example data for the top Gantt chart
    top_colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta', 'blue', 'green', 'silver']
    # top_ax.broken_barh([(5, 10)], (-0.3, 0.6), facecolor=top_colors[0], linewidth=1, edgecolor='black')
    # top_ax.text(10, 0.03, '0', fontsize=18)
    # top_ax.broken_barh([(15, 20)], (0.7, 0.6), facecolor=top_colors[1], linewidth=1, edgecolor='black')
    # top_ax.text(25, 1.03, '1', fontsize=18)
    
    for i in range(num_amrs):
        joblen = len(chromosome.amr_list[i].job_objects)
        for k in range(joblen):
            j = chromosome.amr_list[i].job_objects[k]
            ST = j.job_start_time
            duration = j.job_completion_time - j.job_start_time
            if duration != 0:
                top_ax.broken_barh([(ST, duration)], (-0.3 + i, 0.6), facecolor=top_colors[j.job_number], linewidth=1, edgecolor='black')
                top_ax.text(ST + (duration) / 2 , i - 0.2, '{}'.format(j.job_number), fontsize=14, ha = 'center')

    plt.tight_layout()
    
    if create_txt_file:
        # CHANGE DIRECTORY FOR SAVING FIGURE
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'/home/daniel/Multi-robot-Navigation/src/JobShopGA/Results/gantt_chart{timestamp}'
        plt.savefig(filename)
    # plt.show()
        # directory = '/home/daniel/Multi-robot-Navigation/src/JobShopGA/Results/'        # CHANGE SAVING DIRECTORY

'''
Types of Selection methods implemented:
USED IN ALGORITHM:
-two way tournament (tournament)

NOT USED IN ALGORITHM
-three way tournament (three_way_tournament)
-stochastic universal sampling (stochastic_universal_sampling)
'''
    
def tournament(population):
    indices2 = [x for x in range(N)]
    
    winners = []
    while len(indices2) != 0:
        i1 = random.choice(indices2)
        i2 = random.choice(indices2)
        while i1 == i2:
            i2 = random.choice(indices2)
            
        if population[i1].fitness < population[i2].fitness:
            winners.append(population[i1])
        else:
            winners.append(population[i2])
            
        indices2.remove(i1)
        indices2.remove(i2)
    
    indices2 = [x for x in range(N)]
    
    while len(indices2) != 0:
        i1 = random.choice(indices2)
        i2 = random.choice(indices2)
        while i1 == i2:
            i2 = random.choice(indices2)
            
        if population[i1].fitness < population[i2].fitness:
            winners.append(population[i1])
        else:
            winners.append(population[i2])
            
        indices2.remove(i1)
        indices2.remove(i2)
        
    return winners

def three_way_tournament(population):
    selected_parents = []
    population_size = len(population)
    while len(selected_parents) < population_size:
        tournament_indices = random.sample(range(population_size), 3)
        tournament_individuals = [population[i] for i in tournament_indices]
        tournament_fitness = [population[i].fitness for i in tournament_indices]
        # Find the index of the fittest individual in the tournament
        fittest_index = tournament_fitness.index(min(tournament_fitness))
        # Select the fittest individual as a parent
        selected_parents.append(tournament_individuals[fittest_index])
        
    return selected_parents


def stochastic_universal_sampling(population, num_parents):
    # Calculate inverted fitness values
    max_fitness = max(chromosome.fitness for chromosome in population)
    inverted_fitness = [max_fitness - chromosome.fitness for chromosome in population]

    # Calculate total inverted fitness
    total_inverted_fitness = sum(inverted_fitness)

    # Calculate distance between selection pointers
    pointer_distance = total_inverted_fitness / num_parents

    # Randomly choose a starting point for the selection pointers
    start_point = random.uniform(0, pointer_distance)

    # Create selection pointers
    pointers = [start_point + i * pointer_distance for i in range(num_parents)]

    # Initialize selected individuals list
    selected_individuals = []

    # Iterate over selection pointers and select individuals
    cumulative_fitness = 0
    idx = 0
    for pointer in pointers:
        while cumulative_fitness < pointer:
            cumulative_fitness += inverted_fitness[idx]
            idx += 1
        selected_individuals.append(population[idx])

    return selected_individuals

'''
Implemented crossover functions:
USED IN ALGORITHM:
single_point_crossover
double_point_crossover  (non overlapping)
'''

def single_point_crossover(chrom1, chrom2, amr_assignments):
    
    parent1 = chrom1.encoded_list
    parent2 = chrom2.encoded_list
    
    r = random.uniform(0,1)
    # r = 0.4
    
    p = random.randint(0,len(parent1))
    if r > pc:
        return chrom1 , chrom2
    else:
        offspring1 = parent1[0:p] + parent2[p:]
        offspring2 = parent2[0:p] + parent1[p:]
        # checked_offsp1 = remove_duplicates(offspring1)[:]
        # checked_offsp2 = remove_duplicates(offspring2)[:]
        chrom_out1 = process_chromosome(offspring1, amr_assignments)
        chrom_out2 = process_chromosome(offspring2, amr_assignments)
    
    return chrom_out1, chrom_out2

def double_point_crossover(chrom1, chrom2, amr_assignments):
    parent1 = chrom1.encoded_list
    parent2 = chrom2.encoded_list
    
    r = random.uniform(0,1)
    
    if r > pc:
        return chrom1, chrom2
    
    indexes = [num for num in range(len(parent1))]
    
    point1 = random.randint(0, len(parent1) - 1)
    point2 = random.randint(point1 + 1, len(parent1))
    child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
    child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
        
    # checked_offsp1 = remove_duplicates(child1)[:]
    # checked_offsp2 = remove_duplicates(child2)[:]
    offspring1 = process_chromosome(child1, amr_assignments)
    offspring2 = process_chromosome(child2, amr_assignments)
    
    return offspring1, offspring2
    
    

def single_bit_mutation(chromosome, amr_assignments):
    
    r = random.uniform(0,1)
    code = chromosome.encoded_list[:]
    
    if r > pm:
        return chromosome
    else:
        index = random.randint(0, len(code) - 1)
        code[index] = round(random.uniform(0,m*n), 2)
        # checked_code = remove_duplicates(code)[:]
        mutated_chromosome = process_chromosome(code, amr_assignments)
    
    return mutated_chromosome

'''
Implemented next gen selection:
USED IN ALGORITHM:
-replace worst by sorting parent+offspring population

NOT USED IN ALGORITHM:
20% best parent population, 80% best offspring population

'''

def next_gen_selection(parents, offsprings):
    total_population = []
    total_population.extend(parents)
    total_population.extend(offsprings)
    
    sortedGen = []
    sortedGen = sorted(total_population, key = lambda x : x.fitness)
    return sortedGen[:N], sortedGen[0]
    
    # Use 20% parents 80% offsprings
    # sorted_parent = []
    # number = len(parents)  # Your number
    # twenty_percent = int(number * 0.2)
    # sorted_parents = sorted(parents, key = lambda  x : x.fitness )
    
    # sorted_offsprings = []
    # number = len(offsprings)  # Your number
    # eighty_percent = number - twenty_percent
    # sorted_offsprings = sorted(sorted_offsprings, key = lambda  x : x.fitness )
    
    # total_population = sorted_parents[0:twenty_percent] + sorted_offsprings[twenty_percent:]
    # sorted_total_population = sorted(total_population, key = lambda  x : x.fitness )
    # return total_population, sorted_total_population[0]
    
def swapping(chromosome, amr_assignments):
    r = random.uniform(0,1)
    if r > pswap:
        return chromosome
    
    code = chromosome.encoded_list[:]
    indexes = [num for num in range(len(code))]
    
    p = random.choice(indexes)
    q = random.choice(indexes)
    while p == q:
        q = random.choice(indexes)
        
    code[p], code[q] = code[q], code[p]
    
    swapped_chromosome = process_chromosome(code, amr_assignments)
    return swapped_chromosome
    
def inversion(chromosome, amr_assignments):
    
    r = random.uniform(0,1)
    if r > pinv:
        return chromosome
    
    code = chromosome.encoded_list[:]
    indexes = [num for num in range(len(code))]
    p = random.choice(indexes)
    q = random.choice(indexes)
    while p == q:
        q = random.choice(indexes)
        
    
    p, q = min(p, q), max(p, q)
    code[p:q+1] = reversed(code[p:q+1])
    
    inverted_chromosome = process_chromosome(code, amr_assignments)
    
    return inverted_chromosome



def create_disturbance(population):
    p = N//2
    first_half =  population[:p]
    rem = []
    for _ in range(N):
        num = [round(random.uniform(0,m*n), 2) for _ in range(N - p)]
        rem.append(process_chromosome(num))
    
    new_population = first_half + rem
    return new_population

'''
Heuristics implemented and used:

Shortest processing time first (SPT_heuristic)
Longest Processing Time first (LPT_heuristic)
Shortest Remaining Time first (SRT_heuristic)

'''

def SPT_heuristic(operation_data):
    operation_index_list = []
    n = len(operation_data[0])  # Number of operations
    m = len(operation_data)     # Number of jobs

    for j in range(n):
        tlist = [(i, operation_data[i][j]) for i in range(m)]
        tlist.sort(key=lambda x: x[1][1])  # Sort based on processing time
        operation_index_list.extend([t[0] for t in tlist])

    return operation_index_list

def LPT_heuristic(operation_data):
    operation_index_list = []
    n = len(operation_data[0])  # Number of operations
    m = len(operation_data)     # Number of jobs

    for j in range(n):
        tlist = [(i, operation_data[i][j]) for i in range(m)]
        tlist.sort(key=lambda x: x[1][1], reverse=True)  # Sort based on processing time
        operation_index_list.extend([t[0] for t in tlist])
        
    return operation_index_list

def srt_heuristic(operation_data):
    rem_time = 0
    job_rem_time = []
    operation_index_list = []
    
    for i in range(m):
        job_rem_time = []
        for job in operation_data:
            rem_time = 0
            tjob = job[i:]
            for operation in tjob:
                rem_time += operation[1]
            job_rem_time.append(rem_time)
        sorted_indices = sorted(range(len(job_rem_time)), key=lambda x: job_rem_time[x])
        operation_index_list.extend(sorted_indices)
    
        
    return operation_index_list
        

def decode_operations_to_schedule(operation_index, num_jobs=n):
    n = len(operation_index)
    possible_indices = [[(num_jobs * j + op) for j in range(n // num_jobs + 1)] for op in operation_index]
    ranked_list = [0] * n
    used_indices = set()
    is_valid = True
    for i, options in enumerate(possible_indices):
        # Find the smallest available index that hasn't been used yet
        for option in sorted(options):
            if option not in used_indices and option < n:
                ranked_list[i] = option
                used_indices.add(option)
                break
        else:
            # If no valid option is found, note that configuration may be invalid
            is_valid = False
            break

    if not is_valid:
        return None, None  # Indicate that no valid configuration was found
    
    random_numbers = [0] * n
    index_to_number = {rank: i for i, rank in enumerate(ranked_list)}
    for i in range(n):
        random_numbers[index_to_number[i]] = i + 1  # Simple 1-to-n mapping for simplicity

    return ranked_list, random_numbers


'''
Generate one particle from each heuristic and append to population, remaining are randomly generated
'''
def generate_population_with_heuristic(operation_data, amr_assignments):
    # p = N//2
    
    # GENERATE WITH SPT AND RANDOM
    # population = []
    # for i in range(p):
    #     num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
    #     population.append(process_chromosome(num))
    
    # for _ in range(N - p):
    #     spt = SPT_heuristic(operation_data)
    #     ranked, code = decode_operations_to_schedule(spt)
    #     population.append(process_chromosome(code))
        
    # return population
    
    
    # GENERATE WITH SPT, LPT AND RANDOM
    population = []
    number = n*m
    # twenty_percent = int(number * 0.2)
    # for i in range(twenty_percent):
    #     spt = SPT_heuristic(operation_data)
    #     ranked, code = decode_operations_to_schedule(spt)
    #     population.append(process_chromosome(code))
        
    # for i in range(twenty_percent):
    #     lpt = LPT_heuristic(operation_data)
    #     ranked, code = decode_operations_to_schedule(lpt)
    #     population.append(process_chromosome(code))
        
    # for i in range(N - twenty_percent + twenty_percent):
    #     num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
    #     population.append(process_chromosome(num))
        
    # random.shuffle(population)
    if N > 6:
    
        for i in range(2):
            srt_op_seq = srt_heuristic(operation_data)
            ranked, code = decode_operations_to_schedule(srt_op_seq)
            population.append(process_chromosome(code, amr_assignments))
        
        for i in range(2):
            spt_op_seq = SPT_heuristic(operation_data)
            ranked, code = decode_operations_to_schedule(spt_op_seq)
            population.append(process_chromosome(code, amr_assignments))
            
            
        for i in range(2):
            lpt_op_seq = LPT_heuristic(operation_data)
            ranked, code = decode_operations_to_schedule(lpt_op_seq)
            population.append(process_chromosome(code, amr_assignments))
        
        for i in range(N - 6):
            num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
            population.append(process_chromosome(num, amr_assignments))
        
    else:
        initial_population = generate_population(N)
        population = []
        for encoded_list in initial_population:
            # print(f'generated list: {encoded_list}')
            chromosome = process_chromosome(encoded_list, amr_assignments)
            population.append(chromosome)
        
    return population

def get_sequences_in_amr(amrs):
    glob_amr_machine = []
    glob_amr_ptime = []
    for amr in amrs:
        amr_machines = [o.machine for j in amr.job_objects for o in j.operations]
        amr_machines.extend([-2, -1])
        amr_ptimes = [o.Pj for j in amr.job_objects for o in j.operations]
        amr_ptimes.extend([1, 1])
        amr.machine_sequence = amr_machines
        amr.ptime_sequence = amr_ptimes
        glob_amr_machine.append(amr_machines)
        glob_amr_ptime.append(amr_ptimes)
    return glob_amr_machine, glob_amr_ptime

def create_amr_json(machine_sequences, ptime_sequences, output_file):
    # Initialize the structure
    amr_data = {
        "amr_list": [
            {
                "amr_no": 1,
                "machine_sequence": machine_sequences[0],
                "ptime_sequence": ptime_sequences[0]
            },
            {
                "amr_no": 2,
                "machine_sequence": machine_sequences[1],
                "ptime_sequence": ptime_sequences[1]
            }
        ]
    }

    # Write the data to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(amr_data, json_file, indent=4)
        
        
'''
UNOPTIMIZED MAIN LOOP (was used for debugging)
'''
def main1():
    
    t = 0
    ypoints = []
    
    # generate initial population
    initial_population = generate_population(N)
    population = []
    for encoded_list in initial_population:
        # print(f'generated list: {encoded_list}')
        chromosome = process_chromosome(encoded_list)
        population.append(chromosome)
        
    best_chromosome = population[0]
        
    # start generations
    while t < T:
        
        # create mating pool
        winners_list = tournament(population)
        
        # perform crossover on mating pool
        indices = [x for x in range(N)]
        offspring_list = winners_list
        while len(indices) != 0:
            i1 = random.choice(indices)
            i2 = random.choice(indices)
            while i1 == i2:
                i2 = random.choice(indices)
            
            offspring1, offspring2 = single_point_crossover(winners_list[i1], winners_list[i2])
            offspring_list[i1] = offspring1
            offspring_list[i2] = offspring2
            
            indices.remove(i1)
            indices.remove(i2)
            
        # perform mutation
        mutated_list = []
        for chromosome in offspring_list:
            mutated_chromosome = single_bit_mutation(chromosome)
            mutated_list.append(mutated_chromosome)
            
            
        # perform swapping operation
        swap_list = []
        for chromosome in mutated_list:
            swap_chromosome = swapping(chromosome)
            swap_list.append(swap_chromosome)
            
            
        # perform inversion operation on chromosomes
        invert_list = []
        for chromosome in swap_list:
            inverted_chromosome = inversion(chromosome)
            invert_list.append(inverted_chromosome)
            
        # selection of survivors for next generation
        
        survivors = next_gen_selection(winners_list, invert_list)
        
        if survivors[0].fitness < best_chromosome.fitness:
            best_chromosome = survivors[0]
            
        ypoints.append(best_chromosome.fitness)
        winners_list = survivors
        
        if (t + 1) % 25 == 0:
            print(f'At generation {t + 1}, best fitness :{best_chromosome.fitness}')
        
        
        t += 1
        # end of loop
        
    xpoints = [x for x in range(1, t+ 1)]
    plt.plot(xpoints, ypoints,  color= 'b')
    
    # print(f'best Cmax = {ypoints[N-1]}')
    print(f'best Cmax = {best_chromosome.fitness}')
    
    print('random generated numbers:',best_chromosome.encoded_list)
    print(f'ranked list : {best_chromosome.ranked_list}\n operation_index :{best_chromosome.operation_index_list},\n operation object{best_chromosome.operation_schedule}\n')
    print(f'machine sequence: {best_chromosome.machine_sequence}\n ptime sequence: {best_chromosome.ptime_sequence}\n Cmax: {best_chromosome.Cmax}')

    PlotGanttChar(best_chromosome)
    
    plt.show()
    
    print('\n')


    
'''
Optimized loop main program
'''
def main2():
    
    # Record the start time
    start_time = time.time()
    flag = 0
    count = 0
    t = 0
    ypoints = []
    
    # generate initial population
    # initial_population = generate_population(N)
    # population = []
    # for encoded_list in initial_population:
    #     # print(f'generated list: {encoded_list}')
    #     chromosome = process_chromosome(encoded_list)
    #     population.append(chromosome)
    
    amr_assignments = get_amr_assignments()
        
    population = generate_population_with_heuristic(operation_data, amr_assignments)
        
    sorted_population = sorted(population, key = lambda  x : x.fitness )
        
    best_chromosome = sorted_population[0]
    
    # TERMINATION CONDITION
    history = 0
    stagnation = 0
    
        
    # start generations
    while t < T:
        
        new_amr_assignments = get_amr_assignments()
        
        # create mating pool
        winners_list = tournament(population)
        # winners_list = three_way_tournament(population)
        
        
        
        # perform crossover on mating pool
        indices = [x for x in range(N)]
        offspring_list = winners_list
        while len(indices) != 0:
            i1 = random.choice(indices)
            i2 = random.choice(indices)
            while i1 == i2:
                i2 = random.choice(indices)
                
            rchoice = random.uniform(0,1)
            if rchoice < 1:
                offspring1, offspring2 = single_point_crossover(winners_list[i1], winners_list[i2], new_amr_assignments)
            else:
                # potential bug, skipping job
                offspring1, offspring2 = double_point_crossover(winners_list[i1], winners_list[i2], new_amr_assignments)
            offspring_list[i1] = offspring1
            offspring_list[i2] = offspring2
            
            indices.remove(i1)
            indices.remove(i2)
            
        # perform mutation
        enhanced_list = []
        for chromosome in offspring_list:
            mutated_chromosome = single_bit_mutation(chromosome, new_amr_assignments)
            
            # perform swapping operation
            swap_chromosome = swapping(mutated_chromosome, new_amr_assignments)
            
            if swap_chromosome.Cmax < mutated_chromosome.Cmax:
                enhanced_list.append(swap_chromosome)
                inverted_chromosome = inversion(swap_chromosome, new_amr_assignments)
                if inverted_chromosome.Cmax < swap_chromosome.Cmax:
                    enhanced_list.append(inverted_chromosome)
                else:
                    enhanced_list.append(swap_chromosome)
            else:    
                enhanced_list.append(mutated_chromosome)
        
            # # perform inversion operation on chromosome
            # inverted_chromosome = inversion(swap_chromosome, new_amr_assignments)
            
            # enhanced_list.append(mutated_chromosome)
            
            # # selection of survivors for next generation
        
        survivors, best_in_gen = next_gen_selection(winners_list, enhanced_list)
        
        survivors[-1] = best_in_gen
        if best_in_gen.fitness < best_chromosome.fitness:
            best_chromosome = best_in_gen
            amr_assignments = new_amr_assignments
            
        if best_chromosome.fitness == history and activate_termination == 1:
            stagnation += 1
            
        if stagnation > 10:
            elapsed = time.time() - start_time
            converged_at = elapsed
        else:
            converged_at = 0
        
        #CHECK IF AMR ASSIGNMENT IS BETTER OR WORSE
        
        history = best_chromosome.fitness
            
        ypoints.append(best_chromosome.fitness)
        winners_list = survivors
        
        if (t + 1) % 25 == 0:
            print(f'At generation {t + 1}, best fitness :{best_chromosome.fitness}')
        
        
        
        t += 1
        # end of loop
        
    
    
    
    xpoints = [x for x in range(1, t+ 1)]
    
    if display_convergence:
        plt.plot(xpoints, ypoints,  color= 'b')
    
    # Record the end time
    end_time = time.time()
    processing_time = end_time - start_time
    
    if create_txt_file:
        get_file(best_chromosome, processing_time, converged_at)
    
    
    # print(f'best Cmax = {ypoints[N-1]}')
    print(f'best Cmax = {best_chromosome.fitness}')
    
    print('random generated numbers:',best_chromosome.encoded_list)
    print(f'ranked list : {best_chromosome.ranked_list}\n operation_index :{best_chromosome.operation_index_list},\n operation object{best_chromosome.operation_schedule}\n')
    print(f'machine sequence: {best_chromosome.machine_sequence}\n ptime sequence: {best_chromosome.ptime_sequence}\n Cmax: {best_chromosome.Cmax}')



    PlotGanttChar_with_amr(best_chromosome)
    
    
    if display_schedule:
        plt.show()
    
    machine_seq_amrs, ptime_seq_amrs = get_sequences_in_amr(best_chromosome.amr_list)
    print(machine_seq_amrs,'\n',ptime_seq_amrs)   
    
    if update_json_file:
        create_amr_json(machine_seq_amrs, ptime_seq_amrs, 'amr_data.json')

    # plt.show()
    
    print('\n')

'''
For testing with multiple runs
'''
def run_tests():
    runs = 1
    for _ in range(runs):
        main2()
        

if __name__ == '__main__':
    run_tests()