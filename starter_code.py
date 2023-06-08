from datetime import datetime
import optapy
from optapy.score import HardSoftScore, HardMediumSoftScore
from optapy.constraint import Joiners, ConstraintFactory
import networkx as nx
from networkx.classes.graph import Graph
from typing import List
from typing import Optional
from datetime import timedelta
import pandas as pd
from datetime import datetime, timedelta
from optapy.config import solver
from optapy.types import Duration
from optapy import solver_factory_create
from optapy import constraint_provider


# Vehicle class definition
@optapy.planning_entity
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

# WorkOrder class definition
@optapy.problem_fact
class WorkOrder:
    def __init__(self,
                 work_order_id: int,
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
        self.work_order_id = work_order_id
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

        
        
    
@constraint_provider
def scheduling_constraints(constraint_factory):
    return [
        # Hard constraints
        vehicle_capacity(constraint_factory),
        shift_time(constraint_factory),
        weekend_and_breaks(constraint_factory),
        no_overlapping_jobs(constraint_factory),
        
        # Soft constraints
        maximize_sand_cleaning(constraint_factory),
        avoid_too_many_tasks_in_a_row(constraint_factory),
    ]

def vehicle_capacity(constraint_factory):
    return constraint_factory \
        .from_(WorkOrder) \
        .filter(lambda work_order: work_order.sand_volume > work_order.crew.vehicle_capacity) \
        .penalize("Vehicle capacity", HardMediumSoftScore.ONE_HARD)

def shift_time(constraint_factory):
    return constraint_factory \
        .from_(WorkOrder) \
        .filter(lambda work_order: 
                work_order.assigned_start_time < work_order.crew.vehicle_shift_start or
                work_order.assigned_start_time + timedelta(hours=work_order.time_taken_for_cleaning) > 
                work_order.crew.vehicle_shift_start + timedelta(hours=work_order.crew.shift_time)
        ) \
        .penalize("Shift time", HardMediumSoftScore.ONE_HARD)

def weekend_and_breaks(constraint_factory):
    return constraint_factory \
        .from_(WorkOrder) \
        .filter(lambda work_order: 
                work_order.assigned_start_time.weekday() >= 5 or
                work_order.assigned_start_time.hour == 14
        ) \
        .penalize("Weekend and breaks", HardMediumSoftScore.ONE_HARD)

def no_overlapping_jobs(constraint_factory):
    return constraint_factory \
        .from_(WorkOrder) \
        .join(WorkOrder) \
        .filter(lambda wo1, wo2: 
                wo1.crew == wo2.crew and 
                wo1.assigned_start_time < wo2.assigned_start_time < 
                wo1.assigned_start_time + timedelta(hours=wo1.time_taken_for_cleaning)
        ) \
        .penalize("No overlapping jobs", HardMediumSoftScore.ONE_HARD)

def maximize_sand_cleaning(constraint_factory):
    return constraint_factory \
        .from_(WorkOrder) \
        .reward("Maximize sand cleaning", HardMediumSoftScore.ONE_SOFT, lambda work_order: work_order.get_sand_volume())


def avoid_too_many_tasks_in_a_row(constraint_factory):
    return constraint_factory \
        .from_(WorkOrder) \
        .join(WorkOrder) \
        .filter(lambda wo1, wo2: 
                wo1.crew == wo2.crew and 
                wo1.assigned_start_time + timedelta(hours=wo1.time_taken_for_cleaning) == wo2.assigned_start_time
        ) \
        .penalize("Avoid too many tasks in a row", HardMediumSoftScore.ONE_SOFT)




"""PREPARE DATA STAGE"""
vehicle_df = pd.read_csv('D:/CVRP_May/Scheduling/Data/crew_data.csv')
work_order_df = pd.read_csv('D:/CVRP_May/Scheduling/Data/scheduling_data.csv')

# Convert vehicle_shift_start from string to datetime.time
vehicle_df['vehicle_shift_start'] = pd.to_datetime(vehicle_df['vehicle_shift_start']).dt.time
vehicle_data = vehicle_df.to_dict('records')  # This will give a list of dictionaries

work_order_df['created_date'] = pd.to_datetime(work_order_df['created_date']).dt.date
work_order_df['est_cmp_date'] = pd.to_datetime(work_order_df['est_cmp_date']).dt.date
work_order_df['est_cmp_time'] = pd.to_datetime(work_order_df['est_cmp_time']).dt.time
work_order_data = work_order_df.to_dict('records')  # This will give a list of dictionaries


vehicles = [Vehicle(**data) for data in vehicle_data]
crews = [Crew([vehicle]) for vehicle in vehicles]
work_orders = [WorkOrder(crew=None, assigned_start_time=None, **data) for data in work_order_data]



"""SOLVE STAGE"""

# Define the problem
problem = Schedule(work_orders, vehicles, crews)

# Configure and load the solver config
timeout = 10
solver_config = solver.SolverConfig()
solver_config.withSolutionClass(Schedule).withEntityClasses(Vehicle).withConstraintProviderClass(
    scheduling_constraints).withTerminationSpentLimit(Duration.ofSeconds(timeout))


solver_factory = solver_factory_create(solver_config)
solution = solver_factory.buildSolver().solve(problem)
print("Score Explanation.")
print("Final Score: {}".format(solution.get_score()))
