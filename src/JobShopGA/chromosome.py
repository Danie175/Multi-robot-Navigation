class Chromosome:
    def __init__(self, encoded_list):
        self.encoded_list = encoded_list
        self.ranked_list = []
        self.operation_index_list = []
        self.job_list = []
        self.amr_list = []
        self.operation_schedule = []
        self.machine_sequence = []
        self.machine_list = []
        self.ptime_sequence = []
        self.Cmax = 9999
        self.penalty = 0
        self.fitness = 9999
        
    def set_fitness(self):
        self.fitness = self.Cmax + self.penalty