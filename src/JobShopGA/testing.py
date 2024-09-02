import random
import matplotlib.pyplot as plt
import numpy as np
import sys
import math
from job import Job
from machine import Machine
from operation import Operation
from chromosome import Chromosome
from scipy.stats import rankdata
from amr import AMR
import json

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

# distance_matrix = np.array([
#     [0,2,4,4],
#     [2,0,4,4],
#     [4,4,0,2],
#     [4,4,2,0]
# ])

distance_matrix = np.array([
    [0, 5, 10, 10, 6, 9],
    [5, 0, 10, 10, 6, 9],
    [10, 10, 0, 5, 11, 6],
    [10, 10, 5, 0, 11, 6],
    [6, 6, 11, 11, 0, 10],
    [9, 9, 6, 6, 10, 0]
])



# machine_data = [0,1,2,3, 1,0,3,2, 0,1,3,2]
# ptime_data = [10,8,4,0, 4,3,5,6, 4,7,3,0]

# machine_data = [1,3,2,4, 4,1,2,3, 2,3,4,1 ]
# ptime_data = [5,6,3,0, 8,8,3,6, 2,3,1,0]

# PAPER SAMPLE DATA
machine_data = [0,2,1,3, 3,0,1,2, 1,2,3,0]
ptime_data = [5,6,3,0, 8,8,3,6, 2,3,1,0]

# print out necessary
if len(sys.argv) > 1:
    print_out = sys.argv[1].lower() == 'true'
else:
    # Default value if no command-line argument is provided
    print_out = False
    
if len(sys.argv) > 1:
    test_old_prog = sys.argv[1].lower() == 'old'
else:
    # Default value if no command-line argument is provided
    test_old_prog = False

if len(sys.argv) > 1:
    processing = sys.argv[1].lower() == 'proc'
else:
    # Default value if no command-line argument is provided
    processing = False

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

def assign_operations(jobs, operation_data):
    for job, operation in zip(jobs, operation_data):
        job.operations = operation
    
operation_data = create_operation_data(machine_data,ptime_data, m)
        
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
        ranks = {value: index for index, value in enumerate(sorted_list)}
            
        # Convert each float number to its corresponding rank
        rank_list = [ranks[value] for value in population[i]]
        ranked_population.append(rank_list)
        
    return ranked_population

def induv_integer_list(chromosome):
    # ranked_population = []
    # sorted_list = []
    # ranks = {}
    # # Sort the list to get ranks in ascending order
    # sorted_list = sorted(chromosome)
            
    # # Create a dictionary to store the ranks of each float number
    # ranks = {value: index for index, value in enumerate(sorted_list)}
            
    # # Convert each float number to its corresponding rank
    # rank_list = [ranks[value] + 1 for value in chromosome]
    # ranked_population.append(rank_list)
        
    # return rank_list
    
    ranks = rankdata(chromosome)
    return [int(rank - 1) for rank in ranks]
    
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

def induv_getJobindex(chromosome):
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

def induv_schedule_operations(chromosome, jobs):
    operation_list = []
    explored = []
    
    for i in range(len(chromosome)):
        explored.append(chromosome[i])
        numcount = explored.count(chromosome[i])
        if numcount <= m:
            operation_list.append(jobs[chromosome[i]].operations[numcount-1])
    return operation_list
            
# gives each operation a job number of whihc job it is part of
def install_operations(jobs):
    for job in jobs:
        job.operations = [Operation(job.job_number) for i in range(m)]



def assign_data_to_operations(jobs, operation_data):
    for job,sublist in zip(jobs, operation_data):
        for operation,i in zip(job.operations, range(m)):
            operation.operation_number = i
            operation.machine = sublist[i][0]
            operation.Pj = sublist[i][1]
            
def assign_amrs_to_jobs(jobs, amrs, operation_index_list):
    # t_operations = set(operation_index_list)
    # for num in t_operations:
    #     jobs[num].amr_number = random.randint(0, num_amrs - 1)
    #     amrs[jobs[num].amr_number].assigned_jobs.append(jobs[num].job_number)
    
    # TEST VALUES
    jobs[0].amr_number = 0
    jobs[1].amr_number = 1
    jobs[2].amr_number = 0
    
    amrs[0].assigned_jobs = [2,0]
    amrs[1].assigned_jobs = [1]
            
            
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

def calculate_Cj(operation_schedule, machines, jobs):
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
                # print(f'machine no: {machines[operation.machine].machine_id}, new finish time :{machines[operation.machine].

'''
Checkpoint: when a job is completed, the amr should start the next job after considering travel time of travelling to the unloading dock, unloading, then go to loading dock, load job and then travel to the first machine of next job
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
                    if jobs[operation.job_number].operations[operation.operation_number - 1].Cj < machines[operation.machine].  finish_operation_time:
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

def get_travel_time(jobs, amrs, distance_matrix):
    for job in jobs:
        for operation in job.operations:
            operation.travel_time = operation.calculate_travel_time(amrs, jobs, distance_matrix, enable_travel_time)


def process_chromosome(chromosome):
    
    # print(operation_data)
    jobs = [Job(number) for number in range(n)]
    machines = [Machine(number) for number in range(m)]
    amrs = [AMR(number) for number in range(num_amrs)]
    assign_operations(jobs, operation_data)
    
    
    chromosome = remove_duplicates(chromosome)
    
    ranked_list = induv_integer_list(chromosome)
    operation_index_list = induv_getJobindex(ranked_list)
    
    # CASE 1
    operation_index_list = [1,1,2,2,2,0,1,0,0,1, 0, 2]
    
    
    install_operations(jobs)
    assign_data_to_operations(jobs, operation_data)
    operation_schedule = induv_schedule_operations(operation_index_list, jobs)
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
    ax.tick_params(axis='y', labelcolor='magenta', labelsize=16)
        
    ax.set_xlabel('Time', fontweight ='bold', loc='right', color='red', fontsize=16)
    ax.set_xlim(0, Cmax+2)
        
    ax.tick_params(axis='x', labelcolor='red', labelsize=16)
        
    ax.grid(True)
        
    tmpTitle = 'Job Shop Scheduling (m={:02d}; n={:03d}; Utilization={:04d})'.format(m, n, Cmax)
    plt.title(tmpTitle, size=24, color='blue')
        
    colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta','blue','green','silver']
        
        
    for i in range (m):
        joblen = len(chromosome.machine_list[i].operationlist)
        for k in range(joblen):
            j = chromosome.machine_list[i].operationlist[k]
            ST = j.start_time
            cIndx = 0
            # cIndx = k%(n*N)
            if j.Pj != 0:
                ax.broken_barh([(ST, j.Pj)], (-0.3+i, 0.6), facecolor=colors[j.job_number], linewidth=1, edgecolor='black')
                ax.text((ST + (j.job_number/2-0.3)), (i+0.03), '{}'.format(j.job_number), fontsize=18)
                
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
    
    # ax.set_xlim(0, 140)
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110])
    
    ax.set_xlim(0, Cmax + 20)
    ax.tick_params(axis='x', labelcolor='red', labelsize=16)
    ax.grid(True)

    tmpTitle = f'Job Shop Scheduling (m={m}; n={n}; Cmax={Cmax}; AMRs:{num_amrs})'
    ax.set_title(tmpTitle, size=20, color='blue')

    colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta', 'blue', 'green', 'silver']

    for i in range(m):
        joblen = len(chromosome.machine_list[i].operationlist)
        for k in range(joblen):
            j = chromosome.machine_list[i].operationlist[k]
            ST = j.start_time
            if j.Pj != 0:
                ax.broken_barh([(ST, j.Pj)], (-0.3 + i, 0.6), facecolor=colors[j.job_number], linewidth=1, edgecolor='black')
                ax.broken_barh([(j.Cj, int(j.travel_time))], (-0.3 + i, 0.6), facecolor='black', linewidth=1, edgecolor='black')
                
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

def PlotGanttChar_with_amr_without_travel_mark(chromosome):

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

    tmpTitle = f'Job Shop Scheduling (m={m}; n={n}; Cmax={Cmax}; AMRs:{num_amrs})'
    ax.set_title(tmpTitle, size=20, color='blue')

    colors = ['orange', 'deepskyblue', 'indianred', 'limegreen', 'slateblue', 'gold', 'violet', 'grey', 'red', 'magenta', 'blue', 'green', 'silver']

    for i in range(m):
        joblen = len(chromosome.machine_list[i].operationlist)
        for k in range(joblen):
            j = chromosome.machine_list[i].operationlist[k]
            ST = j.start_time
            if j.Pj != 0:
                ax.broken_barh([(ST, j.Pj)], (-0.3 + i, 0.6), facecolor=colors[j.job_number], linewidth=1, edgecolor='black')
                # ax.broken_barh([(j.Cj, int(j.travel_time))], (-0.3 + i, 0.6), facecolor='black', linewidth=1, edgecolor='black')
                
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
        
    return winners
    
    
                
def single_point_crossover(chrom1, chrom2):
    
    parent1 = chrom1.encoded_list
    parent2 = chrom2.encoded_list
    
    # r = random.uniform(0,1)
    r = 0.4
    
    p = 5
    if r > pc:
        return chrom1 , chrom2
    else:
        offspring1 = parent1[0:p] + parent2[p:]
        offspring2 = parent2[0:p] + parent1[p:]
        chrom_out1 = process_chromosome(offspring1)
        chrom_out2 = process_chromosome(offspring2)
    
    return chrom_out1, chrom_out2
    
def swapping(chromosome):
    code = chromosome.encoded_list
    indexes = [num for num in range(len(code))]
    
    p = random.choice(indexes)
    q = random.choice(indexes)
    while p == q:
        q = random.choice(indexes)
        
    print(code)
        
    code[p], code[q] = code[q], code[p]
    print(code)

def inversion(chromosome):
    code = chromosome.encoded_list
    indexes = [num for num in range(len(code))]
    p = random.choice(indexes)
    q = random.choice(indexes)
    while p == q:
        q = random.choice(indexes)
        
    print(code)
    p, q = min(p, q), max(p, q)
    code[p:q+1] = reversed(code[p:q+1])
    print(code)
    
def SPT_heuristic(operation_data):
    operation_index_list = []
    n = len(operation_data[0])  # Number of operations
    m = len(operation_data)     # Number of jobs

    for j in range(n):
        tlist = [(i, operation_data[i][j]) for i in range(m)]
        tlist.sort(key=lambda x: x[1][1])  # Sort based on processing time
        operation_index_list.extend([t[0] for t in tlist])

    return operation_index_list
        

def decode_operations_to_schedule(operation_index, num_jobs=3):
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

def generate_population_with_heuristic(operation_data):
    p = N//2
    
    population = []
    for _ in range(p):
        num = [round(random.uniform(0,m*n), 2)]
        population.append(process_chromosome(num))
    
    for _ in range(N - p):
        spt = SPT_heuristic(operation_data)
        code = decode_operations_to_schedule(spt)
        population.append(process_chromosome(code))
        
    return population

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


def parse_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        
    machine_sequences = []
    ptime_sequences = []
    
    new_machine_sequences = []
    new_ptime_sequences = []
    
        
    for amr in data['amr_list']:
        machine_sequences.append(amr['machine_sequence'])
        ptime_sequences.append(amr['ptime_sequence'])
        
    for machines, ptimes in zip(machine_sequences, ptime_sequences):
        new_machines = []
        new_ptimes = []
        for machine, ptime in zip(machines, ptimes):
            if ptime != 0:
                new_machines.append(machine)
                new_ptimes.append(ptime)
        new_machine_sequences.append(new_machines)
        new_ptime_sequences.append(new_ptimes)
    
    print(machine_sequences, ptime_sequences)
    print(new_machine_sequences, new_ptime_sequences)
    amr1_sequence = new_machine_sequences[0]
    return amr1_sequence
    
        


def main1():
    operation_data = create_operation_data(machine_data,ptime_data, m)


    jobs = [Job(number) for number in range(n)]
    machines = [Machine(number) for number in range(m)]


    assign_operations(jobs, operation_data)

    initial_population = generate_population(N)
    ranked_population = integer_list(initial_population)
    operation_index_pop = getJobindex(ranked_population)

    # CASE 1
    # operation_index_pop = [[2, 0, 2, 1, 0, 2, 0, 1, 1, 1, 2, 0]]

    # CASE 2
    # operation_index_pop = [[0, 1, 2, 1, 0, 0, 2, 2, 1, 1, 0, 2]] 

    # install the operations in each job
    install_operations(jobs)
    assign_data_to_operations(jobs, operation_data)
    # create sequence with actual operations
    operation_schedule = schedule_operations(operation_index_pop, jobs)

    # get the sequence of machines
    machine_sequence = get_machine_sequence(operation_schedule)

    # get the sequence of processing times
    ptime_sequence = get_processing_times(operation_schedule)

    calculate_Cj(operation_schedule, machines, jobs, machine_sequence, ptime_sequence)
    Cmax = get_Cmax(machines)

    if print_out:
        print(operation_data)
        print('Job 0 operations', jobs[0].operations[0].job_number)
        print('Job 1 operations', jobs[1].operations[1].job_number)
        print('Job 2 operations',jobs[2].operations)
        print('initial population: \n', initial_population)
        print('ranked list:\n', ranked_population)
        print('job operation sequence list:\n', operation_index_pop)
        print('job operation sequence:\n', operation_schedule)
        print(f'machine sequence: {machine_sequence}')
        print(f'ptime sequence: {ptime_sequence}')
        
        for operation in operation_schedule:
            print(f'\n operation of job number: {operation.job_number},operation number: {operation.operation_number}, operation machine number :{ operation.machine}, processing time:{operation.Pj}\n Start time: {operation.start_time}, Pj: {operation.Pj }, Cj: {operation.Cj}')
            
        for machine in machines:
            print(f'machine number: {machine.machine_id}, machine finish: {machine.finish_operation_time}')
            
        print(f'Cmax is {Cmax}')
        
def main2():
    initial_population = generate_population(N)
    
    print(operation_data)
    population = []
    # for encoded_list in initial_population:
    #     print(f'generated list: {encoded_list}')
    #     chromosome = process_chromosome(encoded_list)
    #     population.append(chromosome)
    
    # encoded_list1 = [7.45,	10.69,	9.73,	1.31,	1.67,	1.58,	7.29,	2.77,	8.91,	7.35,	3.46,	7.47]
    # chromosome_test1 = process_chromosome(encoded_list1)
    # print(chromosome_test1.operation_index_list)
    # population.append(chromosome_test1)
    
    # encoded_list2 = [4.74, 8.05, 10.48, 7.19, 6.05, 0.56, 0.04, 3.82, 1.37, 3.95, 1.46, 5.38]
    # chromosome_test2 = process_chromosome(encoded_list2)
    # print(chromosome_test2.operation_index_list)
    # population.append(chromosome_test2)
    
    encoded_list3 = [4.25,9.24,7.24,7.71,3.58,7.86,2.11,6.57,8.31,1.7]
    chromosome_test3 = process_chromosome(encoded_list3)
    population.append(chromosome_test3)
    
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
    
    PlotGanttChar_with_amr(chromosome_test3)
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
    
    amr1_sequence = parse_json('amr_data.json')
    print(f'amr1 sequence = {amr1_sequence}')
    
        
if __name__ == '__main__':
    main2()