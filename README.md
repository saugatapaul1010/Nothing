Project Overview and Problem statement in detail.
We are working on solving a scheduling problem using OptaPy. This scheduling problem is based on assigning and scheduling unassigned work orders, each of which represents a cleaning job. The reference for this task is the "scheduling dataset." Each work order has a set of features, which are:
Work Order Parameters:
•	Work_order_id: Unique identifier for each work order.
•	Task_id: Unique identifier for each task.
•	Status: The current status of the work order, indicating whether it is completed.
•	Created_date: Date and time the work order was created.
•	Est_cmp_date: The estimated date before which the work order should be completed.
•	Est_cmp_time: The estimated time on the given estimated day by when the work order should be completed.
•	Severity: This indicates the severity of the work order and can be either "LOW," "MEDIUM," or "HIGH."
•	Priority: This shows the priority of the work order, which can be "LOW," "HIGH," or "EMERGENCY."
•	Area_code: An identifier that can be considered as the area name. Each area code corresponds to a road name in a separate database.
•	Sand_volume: The amount of sand that needs to be cleaned from the designated area.
•	Time_taken_for_cleaning: The time required in hours to clean up the sand from the respective area code.
Crew/Vehicle Parameters:
The work orders are assigned to crews, which in this scenario are vehicles. The attributes of each vehicle are:
•	Vehicle_num: A unique identifier for each vehicle.
•	Speed: The average speed of the vehicle.
•	Vehicle_capacity: The amount of sand that the vehicle can carry.
•	Vehicle_depot_name: The depot where the vehicle is currently stationed.
•	Shift_time: The total working hours for the vehicle in a day. If a vehicle starts at 10 AM and has a shift time of 8 hours, it should finish its clean-up activities by 7:00 PM, taking into account a 1-hour break time.
•	Vehicle_return_depot: The depot where the vehicle must return after performing its cleaning activities.
•	Vehicle_shift_start: The time of day when the vehicle starts its job.
 
 
Problem Statement:
The goal is to utilize OptaPy for assigning individual work orders to available vehicles in a way that ensures completion of all the work orders before their estimated completion date and time. We are dealing with 35 jobs to be assigned to the available 10 vehicles as per the scheduling dataset.
Detailed Constraints and Goals:
•	Shift Time Constraints: The job assigned to a vehicle should only start at or after the vehicle shift starts. For instance, if "vehicle_shift_start" is 10:00 AM, the job can start at any time after 10 AM and finish by the estimated completion time.
•	Weekends and Breaks: The vehicles do not operate during the weekends or the lunch break time between 2:00 PM to 3:00 PM. The work orders should be assigned considering these non-working hours.
•	Overlapping Jobs: At most, one job can be assigned per crew per day, avoiding overlapping jobs for the same crew. If there are two or more jobs in the same area code, they shouldn't be performed simultaneously to prevent overlap.
•	Capacity Constraints: Each vehicle has a carrying capacity. If the sand volume in a work order exceeds the vehicle's capacity, the vehicle can do multiple trips to clean up the sand.
•	Emergency Areas: The goal is to maximize sand cleaning, prioritizing the areas marked as 'EMERGENCY'.
•	Vehicle Constraints: All operations during the day need to be completed between the shift start and end times. Additionally, avoid scheduling too many tasks in a row for one vehicle to prevent overworking.
•	Schedule Span: The schedule does not have a strict limit, but all work orders must be completed within their respective estimated completion dates and times. The time span for the schedule needs to take these factors into account.
 
Initial Code:
```
# WorkOrder class definition
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


# Vehicle class definition
@optapy.problem_fact
class Crew:
    def __init__(self,
                 vehicles: List[Vehicle]):
        self.vehicles = vehicles


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

```
