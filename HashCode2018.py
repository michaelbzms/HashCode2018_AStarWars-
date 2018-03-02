"""
Choose i/o filename here:
- a_example
- b_should_be_easy
- c_no_hurry
- d_metropolis
- e_high_bonus
"""

filename = 'b_should_be_easy'     # choose input and output file names here

ride_pool = []
ride_id = 0
with open(filename + '.in', 'r') as file:
    args = file.readline().split()
    for line in file:
        r = line.split()
        ride_pool.append((ride_id, (int(r[0]), int(r[1])), (int(r[2]), int(r[3])), int(r[4]), int(r[5])))
        ride_id += 1
R = int(args[0])
C = int(args[1])
F = int(args[2])
N = int(args[3])
B = int(args[4])
T = int(args[5])

# RIDE: ((rideID, (startx, starty), (endx, endy), start_time, finish_time)

finished_cars_IDs = []         # this will contain all the cars that have no more eligible rides


class Car:
    def __init__(self, id):
        self.carID = id
        self.currRide = None
        self.posx = 0
        self.posy = 0
        self.ride_dist = 0        # distance till current ride is finished
        self.pickup_dist = 0    # distance till the pickup spot - (startx, starty) of ride

    def assignRide(self, Ride):
        self.currRide = Ride
        self.ride_dist = manhattanDistance((Ride[1][0], Ride[1][1]), (Ride[2][0], Ride[2][1]))
        self.pickup_dist = manhattanDistance((self.posx, self.posy), (Ride[1][0], Ride[1][1]))

    def chooseRideBasedOnStartTime(self, t):     # greedily minimize start_time for rides
        global R, C, ride_pool
        if self.carID in finished_cars_IDs:
            return
        mintimes = float('inf')
        minride = None
        finished = True
        for ride in ride_pool:
            dt = calculate_start_time((self.posx, self.posy), t, ride)
            if ride_would_be_in_vain(ride, dt, t):
                continue
            finished = False
            if dt < mintimes:
                mintimes = dt
                minride = ride
        if finished:
            finished_cars_IDs.append(self.carID)
        if minride is None:               # better pass
            return
        ride_pool.remove(minride)
        self.assignRide(minride)

    def chooseRideBasedOnMixedScore(self, t):     # greedily maximaze the ratio of score / start_time for rides
        global R, C, ride_pool, B
        if self.carID in finished_cars_IDs:
            return
        maxmixedscore = float('-inf')
        maxride = None
        finished = True
        for ride in ride_pool:
            mixed_score = calculate_mixed_score((self.posx, self.posy), t, ride)
            if ride_would_be_in_vain_2(ride, (self.posx, self.posy), t):
                continue
            finished = False
            if mixed_score > maxmixedscore:
                maxmixedscore = mixed_score
                maxride = ride
        if finished:
            finished_cars_IDs.append(self.carID)
        if maxride is None:  # better pass
            return
        ride_pool.remove(maxride)
        self.assignRide(maxride)

    def act(self, t):
        if self.currRide is None:         # no rides assigned
            self.chooseRideBasedOnMixedScore(t)         # greedy choice -> we have implemented 2 options
        if self.currRide is None:         # choose returned none -> pass this round
            return None

        if self.pickup_dist > 0:           # hasn't reached the pickup spot yet
            self.pickup_dist -= 1
        elif self.pickup_dist == 0:      # has reached the pickup spot
            if t < self.currRide[3]:        # time to start is not here yet
                pass   # wait
            elif self.ride_dist > 0:        # still working on given ride
                self.ride_dist -= 1
            elif self.ride_dist == 0:
                res = self.currRide
                self.currRide = None
                return res
            else:
                print("Unexpected Error")
        else:
            print("Unexpected Error")

        return None


def manhattanDistance( xy1, xy2 ):
    """Returns the Manhattan distance between points xy1 and xy2"""
    return abs( xy1[0] - xy2[0] ) + abs( xy1[1] - xy2[1] )


def calculate_start_time(pos, t, ride):
    pickuptime = manhattanDistance(pos, ride[1])
    wait_time = ride[3] - (t + pickuptime)
    if wait_time < 0:
        wait_time = 0
    # journey_time = manhattanDistance(ride[1], ride[2])
    return pickuptime + wait_time


def calculate_mixed_score(pos, t, ride):
    pickuptime = manhattanDistance(pos, ride[1])
    wait_time = ride[3] - (t + pickuptime)
    if wait_time < 0:
        wait_time = 0
    journey_time = manhattanDistance(ride[1], ride[2])
    completion_time = pickuptime + wait_time + journey_time
    score = 0
    if t + pickuptime <= ride[3]:
        score += B
    if t + completion_time < ride[4]:
        score += journey_time
    if float(pickuptime + wait_time) != 0:
        ratio = float(score) / (float(pickuptime + wait_time))
    else:
        ratio = float(score)
    return ratio


def ride_would_be_in_vain(ride, start_time,  t):
    completion_time = start_time + manhattanDistance(ride[1], ride[2])
    return t + completion_time >= ride[4]


def ride_would_be_in_vain_2(ride, pos, t):          # second version of this
    pickuptime = manhattanDistance(pos, ride[1])
    wait_time = ride[3] - (t + pickuptime)
    if wait_time < 0:
        wait_time = 0
    completion_time = pickuptime + wait_time + manhattanDistance(ride[1], ride[2])
    return t + completion_time >= ride[4]


def simulation():
    global T, F, N, B, R, C
    car_history = {}              # the solution
    cars = []
    for i in range(0, F):
        cars.append(Car(i))
        car_history[i] = []
    for t in range(0, T):
        # print(t)
        for car in cars:
            finished_ride = car.act(t)
            if finished_ride is not None:
                car_history[car.carID].append(finished_ride[0])
    return car_history


# main():
car_history = simulation()
with open(filename + '.out', 'w') as file:
    for carID in range(0, F):
        num_of_rides = len(car_history[carID])
        file.write(str(num_of_rides))
        for ridenum in range(0, num_of_rides):
            file.write(' ' + str(car_history[carID][ridenum]))
        file.write('\n')
