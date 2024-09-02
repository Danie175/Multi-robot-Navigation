class Operation:
    def __init__(self, job_number):
        self.job_number = job_number
        self.operation_number = 0
        self.machine = None
        self.Pj = None
        self.start_time = 0
        self.Cj = 0
        self.travel_time = 0
        
    def __str__(self):
        return str(self.job_number)
        
    def getCj(self):
        self.Cj = self.start_time + self.Pj
        
        
    # TURN ON SOURCE AND DISTANCE FOR USING TRAVEL TIME
    def calculate_travel_time(self, amrs, jobs, distance_matrix, en_tt):
        distance = 0
        
        velocity = amrs[jobs[self.job_number].amr_number].velocity
        
        if en_tt:
            
            source = self.machine
            
            if self.Pj == 0:
                return 0
            
            # IF NEXT JOB PROCESSING TIME IS 0 PUT THIS JOB AS LAST JOB
            if self.operation_number != len(jobs[self.job_number].operations) - 1:
                if jobs[self.job_number].operations[self.operation_number + 1].Pj == 0:
                    
                    distance = distance_matrix[source][5] + distance_matrix[5][4]  
                    
                    return distance/velocity
                    
            if self.operation_number == len(jobs[self.job_number].operations) - 1:
                
                distance = distance_matrix[source][5] + distance_matrix[5][4]
            
            else:
                dest = jobs[self.job_number].operations[self.operation_number + 1].machine
                distance = distance_matrix[source][dest]
                
        return distance/velocity
            