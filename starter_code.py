# Vehicle class definition
@optapy.problem_fact
class Vehicle:
    def __init__(self,
                 vehicle_num: int,
                 speed: int,
                 vehicle_capacity: int,
                 vehicle_depot_name: str,
                 shift_time: int,
                 vehicle_return_depot: str,
                 vehicle_shift_start: datetime):

        self.vehicle_num = vehicle_num
        self.speed = speed
        self.vehicle_capacity = vehicle_capacity
        self.vehicle_depot_name = vehicle_depot_name
        self.shift_time = shift_time
        self.vehicle_return_depot = vehicle_return_depot
        self.vehicle_shift_start = vehicle_shift_start


# Crew class definition
@optapy.problem_fact
class Crew:
    def __init__(self,
                 vehicles: List[Vehicle]):
        self.vehicles = vehicles

#WorkOrder class defintion
@optapy.planning_entity
class WorkOrder:
    def __init__(self,
                 id: int,
                 task_id: int,
                 status: str,
                 created_date: datetime,
                 est_cmp_date: datetime,
                 est_cmp_time: datetime,
                 severity: str,
                 priority: str,
                 area_code: str,
                 sand_volume: int,
                 time_taken_for_cleaning: int,
                 crew: Optional[Crew] = None,
                 assigned_start_time: Optional[datetime] = None):
        self.id = id
        self.task_id = task_id
        self.status = status
        self.created_date = created_date
        self.est_cmp_date = est_cmp_date
        self.est_cmp_time = est_cmp_time
        self.severity = severity
        self.priority = priority
        self.area_code = area_code
        self.sand_volume = sand_volume
        self.time_taken_for_cleaning = time_taken_for_cleaning
        self.crew = crew
        self.assigned_start_time = assigned_start_time

    # Planning variable: changes during planning, between score calculations.
    @optapy.planning_variable(Crew, ["crew"])
    def get_crew(self):
        return self.crew

    def set_crew(self, crew):
        self.crew = crew

    # Planning variable: changes during planning, between score calculations.
    @optapy.planning_variable(Crew, ["crew"])
    def get_assigned_start_time(self):
        return self.assigned_start_time

    def set_assigned_start_time(self, assigned_start_time):
        self.assigned_start_time = assigned_start_time


@optapy.planning_solution
class Schedule:
    def __init__(self, work_orders: List[WorkOrder], vehicles: List[Vehicle], crews: List[Crew], score=None):
        self.work_orders = work_orders
        self.vehicles = vehicles
        self.crews = crews
        self.score = score

    @optapy.planning_entity_collection_property(WorkOrder)
    def get_work_orders(self):
        return self.work_orders

    @optapy.problem_fact_collection_property(Vehicle)
    def get_vehicles(self):
        return self.vehicles

    @optapy.problem_fact_collection_property(Crew)
    def get_crews(self):
        return self.crews

    @optapy.planning_score(HardMediumSoftScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
