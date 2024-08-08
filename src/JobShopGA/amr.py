class AMR:
    def __init__(self, number):
        self.amr_number = number
        self.current_job = None
        self.assigned_jobs = []
        self.completed_jobs = []
        self.job_objects = []
        self.job_start_time = 0
        self.job_completion_time = 0
        self.machine_sequence = []
        self.ptime_sequence  = []