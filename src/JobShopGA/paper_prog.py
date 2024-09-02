import random
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.stats import rankdata
from job import Job
from machine import Machine
from chromosome import Chromosome
import time
import os
from datetime import datetime
from amr import AMR
import json

'''
classes cutom
'''

class Operation:
    def __init__(self, job_number):
        self.job_number = job_number
        self.operation_number = 0
        self.machine = None
        self.Pj = None
        self.start_time = 0
        self.Cj = 0
        self.travel_time = 0
        
    def getCj(self):
        self.Cj = self.start_time + self.Pj
        
        
    # TURN ON SOURCE AND DISTANCE FOR USING TRAVEL TIME
    def calculate_travel_time(self, amrs, jobs, distance_matrix, en_tt):
        distance = 0
        
        if en_tt:
            source = self.machine
        else:
            source = 0
        velocity = amrs[jobs[self.job_number - 1].amr_number - 1].velocity
        if self.Pj == 0:
            return 0
        
        # IF NEXT JOB PROCESSING TIME IS 0 PUT THIS JOB AS LAST JOB
        if self.operation_number != len(jobs[self.job_number - 1].operations) - 1:
            if jobs[self.job_number - 1].operations[self.operation_number - 1].Pj == 0:
                if en_tt:
                    distance = 10         # ASSUMING COMMON DISTANCE BETWEEN LOADING DOCK, UNLOADING DOCK AND CURRENT MACHINE
                else:
                    distance = 0
                return distance/velocity
                
        if self.operation_number == len(jobs[self.job_number - 1].operations) - 1:
            if en_tt:
                distance = 10
            else:
                distance = 0
        else:
            dest = jobs[self.job_number - 1].operations[self.operation_number - 1].machine
            distance = distance_matrix[source][dest]
        return distance/velocity

'''
Parameters are HERE
'''
m = 4
n = 3
num_amrs = 2
N = 100
pc = 0.8
pm = 0.05
pswap = 0.05
pinv = 0.05
T = 100

activate_termination = 0
enable_travel_time = 1
display_convergence = 1
display_schedule = 1

'''
INSTANCE DATA FOR JOB SHOP

last two rows and collums are loading dock and unloading dock respectively
'''

# Pinedo book first example
machine_data = [1,3,2,0, 4,1,2,3, 2,3,4,0]
ptime_data = [5,6,3,0, 8,8,3,6, 2,3,1,0]


if enable_travel_time:
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

operation_data = create_operation_data(machine_data,ptime_data, m)
print(operation_data)

def get_amr_assignments():
    amr_assignments = []
    for num in range(n):
        amr_num = random.randint(1,num_amrs)
        amr_assignments.append(amr_num)
        
    return amr_assignments

def assign_amrs_to_jobs(jobs, amrs, operation_index_list):
    # t_operations = set(operation_index_list)
    # for num in t_operations:
    #     jobs[num].amr_number = random.randint(0, num_amrs - 1)
    #     amrs[jobs[num].amr_number].assigned_jobs.append(jobs[num].job_number)
    
    # TEST VALUES
    jobs[0].amr_number = 1
    jobs[1].amr_number = 2
    jobs[2].amr_number = 1
    
    # amrs[0].assigned_jobs = [3,1]
    # amrs[1].assigned_jobs = [2]

def assign_operations(jobs, operation_data):
    for job, operation in zip(jobs, operation_data):
        job.operations = operation
        
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
        else:
            modified_numbers.append(num)
            seen.add(num)
    
    return modified_numbers

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
    return [int(rank) for rank in ranks]

def indiv_getJobindex(chromosome):
    new_index = 0
    operation_index_pop = []

    tlist = []
    temp = chromosome
    for j in range(len(chromosome)):
        new_index = (temp[j] % n + 1)
        tlist.append(new_index)
    operation_index_pop = tlist
    
    return operation_index_pop

# gives each operation a job number of whihc job it is part of
def install_operations(jobs):
    for job in jobs:
        job.operations = [Operation(job.job_number) for i in range(m)]
        
        
def assign_data_to_operations(jobs, operation_data):
    for job,sublist in zip(jobs, operation_data):
        for operation,i in zip(job.operations, range(m)):
            operation.operation_number = i + 1
            operation.machine = sublist[i][0]
            operation.Pj = sublist[i][1]
            
def check_list_length(my_list):
    try:
        if len(my_list) != m*n:
            raise ValueError(f"List length is not {m*n}")
        # print("List length is 12")
    except ValueError as e:
        print(f"Error: {e}")
        
# def assign_amrs_to_jobs(jobs, amrs, amr_assignments):
#     for job, amr_num in zip(jobs, amr_assignments):
#         job.amr_number = amr_num
#         amrs[job.amr_number - 1].assigned_jobs.append(job.job_number)
        
        
def indiv_schedule_operations(chromosome, jobs):
    operation_list = []
    explored = []
    
    for i in range(len(chromosome)):
        explored.append(chromosome[i])
        numcount = explored.count(chromosome[i])
        if numcount <= m:
            operation_list.append(jobs[chromosome[i] - 1].operations[numcount-1])  # changed chromosome[i] to chromosome[i]-1
    return operation_list

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

def get_travel_time(jobs, amrs, distance_matrix):
    for job in jobs:
        for operation in job.operations:
            operation.travel_time = operation.calculate_travel_time(amrs, jobs, distance_matrix, enable_travel_time)
            
            
def calculate_Cj_with_amr(operation_schedule, machines, jobs, amrs):
    t_op = operation_schedule
    skipped = []
    while t_op != []:
        # print('running')
        for operation in t_op:
            # CHECK IF AMR IS ASSIGNED TO A JOB, ONLY ASSIGN IF THE OPERATION NUMBER IS ZERO
            if amrs[jobs[operation.job_number - 1].amr_number - 1].current_job == None and operation.operation_number == 1:
                amrs[jobs[operation.job_number - 1].amr_number - 1].current_job = operation.job_number
                amrs[jobs[operation.job_number - 1].amr_number - 1].job_objects.append(jobs[operation.job_number - 1]) # APPEND JOB OBJECTS
                # IF AMR JUST COMPLETED A JOB UPDATE THE NEXT JOBS MACHINE START TO THE TIME WHEN AMR COMPLETED PREVIOUS JOB
                if machines[operation.machine - 1].finish_operation_time < amrs[jobs[operation.job_number - 1].amr_number - 1].job_completion_time:
                    machines[operation.machine - 1].finish_operation_time = amrs[jobs[operation.job_number - 1].amr_number - 1].job_completion_time
                
                
            # CHECK IF AMR IS CURRENTLY PROCESSING THIS JOB
            if operation.job_number == amrs[jobs[operation.job_number - 1].amr_number - 1].current_job:
                
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
                    if jobs[operation.job_number - 1].operations[operation.operation_number].Cj + jobs[operation.job_number - 1].operations[operation.operation_number].travel_time < machines[operation.machine - 1].  finish_operation_time:
                        operation.start_time = machines[operation.machine - 1].finish_operation_time
                        operation.Cj = operation.start_time + operation.Pj
                        machines[operation.machine - 1].finish_operation_time = operation.Cj 
                        # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                        
                    else:
                        operation.start_time = jobs[operation.job_number].operations[operation.operation_number - 1].Cj + jobs[operation.job_number].operations[operation.operation_number - 1].travel_time
                        operation.Cj = operation.start_time + operation.Pj
                        if operation.Pj != 0:
                            machines[operation.machine - 1].finish_operation_time = operation.Cj
                        # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].finish_operation_time}')
                
                
            # SKIP THE JOB AND RETURN TO IT LATER
            else:
                skipped.append(operation)
            
            # UPDATE PARAMETERS ONCE A JOB IS COMPLETED
            if operation.operation_number == m and amrs[jobs[operation.job_number - 1].amr_number - 1].current_job == operation.job_number:
                        amrs[jobs[operation.job_number - 1].amr_number - 1].current_job = None
                        if amrs[jobs[operation.job_number - 1].amr_number - 1].assigned_jobs != []:
                            amrs[jobs[operation.job_number - 1].amr_number - 1].assigned_jobs.remove(operation.job_number - 1)
                        amrs[jobs[operation.job_number - 1].amr_number - 1].completed_jobs.append(operation.job_number)
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

'''
Single function to completely process an individual chromosome.
'''

def process_chromosome(chromosome):
    
    # print(operation_data)
    jobs = [Job(number + 1) for number in range(n)]
    machines = [Machine(number + 1) for number in range(m)]
    amrs = [AMR(number + 1) for number in range(num_amrs)]
    assign_operations(jobs, operation_data)
    
    
    chromosome = remove_duplicates(chromosome)
    
    ranked_list = indiv_integer_list(chromosome)
    operation_index_list = indiv_getJobindex(ranked_list)
    
    # CASE 1
    # operation_index_list = [1, 2, 0, 1, 2, 0, 2, 0, 1, 0, 2, 1]
    operation_index_list = [2, 2, 1, 2, 1, 3, 3, 3, 1, 2, 1, 3]
    
    
    install_operations(jobs)
    assign_data_to_operations(jobs, operation_data)
    operation_schedule = indiv_schedule_operations(operation_index_list, jobs)
    assign_amrs_to_jobs(jobs, amrs, operation_index_list)
    
    # get the sequence of machines
    machine_sequence = get_machine_sequence(operation_schedule)
    
    # get the sequence of processing times
    ptime_sequence = get_processing_times(operation_schedule)
    
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
    
    return chromosome

'''
Generate one particle from each heuristic and append to population, remaining are randomly generated
'''
# def generate_population_with_heuristic(operation_data, amr_assignments):
#     # p = N//2
    
#     # GENERATE WITH SPT AND RANDOM
#     # population = []
#     # for i in range(p):
#     #     num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
#     #     population.append(process_chromosome(num))
    
#     # for _ in range(N - p):
#     #     spt = SPT_heuristic(operation_data)
#     #     ranked, code = decode_operations_to_schedule(spt)
#     #     population.append(process_chromosome(code))
        
#     # return population
    
    
#     # GENERATE WITH SPT, LPT AND RANDOM
#     population = []
#     number = n*m
#     # twenty_percent = int(number * 0.2)
#     # for i in range(twenty_percent):
#     #     spt = SPT_heuristic(operation_data)
#     #     ranked, code = decode_operations_to_schedule(spt)
#     #     population.append(process_chromosome(code))
        
#     # for i in range(twenty_percent):
#     #     lpt = LPT_heuristic(operation_data)
#     #     ranked, code = decode_operations_to_schedule(lpt)
#     #     population.append(process_chromosome(code))
        
#     # for i in range(N - twenty_percent + twenty_percent):
#     #     num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
#     #     population.append(process_chromosome(num))
        
#     # random.shuffle(population)
#     if N > 6:
    
#         for i in range(2):
#             srt_op_seq = srt_heuristic(operation_data)
#             ranked, code = decode_operations_to_schedule(srt_op_seq)
#             population.append(process_chromosome(code, amr_assignments))
        
#         for i in range(2):
#             spt_op_seq = SPT_heuristic(operation_data)
#             ranked, code = decode_operations_to_schedule(spt_op_seq)
#             population.append(process_chromosome(code, amr_assignments))
            
#         for i in range(2):
#             lpt_op_seq = LPT_heuristic(operation_data)
#             ranked, code = decode_operations_to_schedule(lpt_op_seq)
#             population.append(process_chromosome(code, amr_assignments))
        
#         for i in range(N - 6):
#             num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
#             population.append(process_chromosome(num, amr_assignments))
        
#     else:
#         initial_population = generate_population(N)
#         population = []
#         for encoded_list in initial_population:
#             # print(f'generated list: {encoded_list}')
#             chromosome = process_chromosome(encoded_list, amr_assignments)
#             population.append(chromosome)
        
#     return population

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

# def generate_population(N):
#     population = []
#     for _ in range(N):
#         num = [round(random.uniform(0,m*n), 2) for _ in range(n*m)]
#         population.append(num)
#     return population

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
    plt.show()


def main2():
    # initial_population = generate_population(N)
    
    print(operation_data)
    population = []
    # for encoded_list in initial_population:
    #     print(f'generated list: {encoded_list}')
    #     chromosome = process_chromosome(encoded_list)
    #     population.append(chromosome)
    
    # encoded_list1 = [7.45,	10.69,	9.73,	1.31,	1.67,	1.58,	7.29,	2.77,	8.91,	7.35,	3.46,	7.47]
    encoded_list1 = [4.25,9.24,7.24,7.71, 3.58, 7.86, 2.11, 6.57, 8.31, 1.7]
    
    chromosome_test1 = process_chromosome(encoded_list1)
    print(chromosome_test1.operation_index_list)
    population.append(chromosome_test1)
    
    # encoded_list2 = [4.74, 8.05, 10.48, 7.19, 6.05, 0.56, 0.04, 3.82, 1.37, 3.95, 1.46, 5.38]
    # chromosome_test2 = process_chromosome(encoded_list2)
    # print(chromosome_test2.operation_index_list)
    # population.append(chromosome_test2)
    
    # encoded_list3 = [4.25,9.24,7.24,7.71,3.58,7.86,2.11,6.57,8.31,1.7]
    # chromosome_test3 = process_chromosome(encoded_list3)
    # population.append(chromosome_test3)
    
    # operation_seq_index = srt_heuristic(operation_data)
    # print(operation_seq_index)
    # print('spt operation sequence:', operation_seq_index)
    # ranked_list, random_numbers_list = decode_operations_to_schedule(operation_seq_index)
    # print('decoded ranked_list', ranked_list)
    # print('decoded random numbers list', random_numbers_list)
    # chromosome_test3 = process_chromosome(random_numbers_list)
    # print('random generated numbers:',chromosome_test3.encoded_list)
    # print(f'ranked list : {chromosome_test3.ranked_list}\n operation_index :{chromosome_test3.operation_index_list},\n operation object{chromosome_test3.operation_schedule}\n')
    # print(f'machine sequence: {chromosome_test3.machine_sequence}\n ptime sequence: {chromosome_test3.ptime_sequence}\n Cmax: {chromosome_test3.Cmax}')
    # for machine in chromosome_test3.machine_list:
    #     print(f'machine no: {machine.machine_id}, Cj :{machine.finish_operation_time}')
    
    PlotGanttChar_with_amr(chromosome_test1)
    # PlotGanttChar_with_amr_without_travel_mark(chromosome_test3)
    # PlotGanttChar_with_amr(chromosome_test2)
    # PlotGanttChar(chromosome_test2)
    plt.show()
    
    # for chromosome in population:
    #     for machine in chromosome.machine_list:
    #         for operation in machine.operationlist:
    #             print(f'machine no: {machine.machine_id}, operation assigned mach: {operation.machine}, job no: {operation.job_number}, operation no: {operation.operation_number}')
            
        
        
    # PlotGanttChar(chromosome_test)
    # plt.show()
    
    # winners_list = tournament(population)
    
    # print('parents are')
    # for chromosome in winners_list:
    #     print(chromosome.encoded_list)
    
    # serial crossover section
    
    # indices = [x for x in range(N)]
    # offspring_list = winners_list
    # while len(indices) != 0:
    #     i1 = random.choice(indices)
    #     i2 = random.choice(indices)
    #     while i1 == i2:
    #         i2 = random.choice(indices)
        
    #     offspring1, offspring2 = single_point_crossover(winners_list[i1], winners_list[i2])
    #     offspring_list[i1] = offspring1
    #     offspring_list[i2] = offspring2
        
    #     indices.remove(i1)
    #     indices.remove(i2)
    
    offspring_list = []
    
    # offspring1, offspring2 = single_point_crossover(chromosome_test1, chromosome_test2)
    # offspring_list.extend([offspring1, offspring2])
    
    # swapping(chromosome_test1)
    
    # inversion(chromosome_test1)
    
        
    if print_out:
        for chromosome in population:
            print('random generated numbers:',chromosome.encoded_list)
            print(f'ranked list : {chromosome.ranked_list}\n operation_index :{chromosome.operation_index_list},\n operation object{chromosome.operation_schedule}\n')
            print(f'machine sequence: {chromosome.machine_sequence}\n ptime sequence: {chromosome.ptime_sequence}\n Cmax: {chromosome.Cmax}')
            for machine in chromosome.machine_list:
                print(f'machine no: {machine.machine_id}, Cj :{machine.finish_operation_time}')
        for chromosome in offspring_list:
            print('random generated numbers:',chromosome.encoded_list)
            print(f'ranked list : {chromosome.ranked_list}\n operation_index :{chromosome.operation_index_list},\n operation object{chromosome.operation_schedule}\n')
            print(f'machine sequence: {chromosome.machine_sequence}\n ptime sequence: {chromosome.ptime_sequence}\n Cmax: {chromosome.Cmax}')
            for machine in chromosome.machine_list:
                print(f'machine no: {machine.machine_id}, Cj :{machine.finish_operation_time}')
                
    # print('offsprings are:')
    # for chromosome in offspring_list:
    #     print(chromosome.encoded_list)
    
    # amr1_sequence = parse_json('amr_data.json')
    # print(f'amr1 sequence = {amr1_sequence}')
    
        
if __name__ == '__main__':
    main2()