### section09/simulate.py
import time
from city import CitySqGrid
from consts import NO_CAR, NO_DEST, NO_RIDER, NOTHING, EVERYTHING, DELAY
from offline import Car, CarManager
from online import Rider, RiderManager


class Simulator:
    def __init__(self, blocks_per_side):
        self.city = CitySqGrid(blocks_per_side)
        self.car_mgr = CarManager(self.city)
        self.rider_mgr = RiderManager(self.city)

        self._timesteps = 0   # default value

    @property
    def timesteps(self):
        return self._timesteps
    
    @timesteps.setter
    def timesteps(self, value):
        if value <= 0:
            raise ValueError
        self._timesteps = value


    def simulate(self, delay=1.0, show=EVERYTHING):
        '''Run the Waylo simulator to test your make_assignments
           routine. Returns None since all updates made to our_city,
           cars, and riders.
        
           delay:     seconds to wait between timesteps
           show:      Constant from online.py that says what to print
        '''
        
        # Initialize statistic variables. These are totals across all
        # cars and riders.
        miles_driven = 0
        mins_waiting = 0
        mins_idle = 0

        for timestep in range(1, self.timesteps + 1):
            if show == EVERYTHING:
                print(f'TIMESTEP {timestep}')

            # Assign free cars to waiting riders -- STUDENT WORK
            self.make_assignments(timestep, show)

            # Move cars one time step
            self.move_cars(timestep, show)

            # New rider hails in this timestep?
            self.rider_mgr.add_hails(timestep, show)

            # Update statistics
            for rider in self.rider_mgr.riders.values():
                if rider.waiting:
                    mins_waiting += 1

            for car in self.car_mgr.cars.values():
                if car.rider == NO_RIDER:
                    mins_idle += 1
                else:
                    miles_driven += 1

            # Update the map
            self.update_map()

            if show == EVERYTHING:
                # Display updated map
                print(self.city)

            time.sleep(delay)    # slow down the simulation to human time

        return (mins_waiting, mins_idle, miles_driven)


    def move_cars(self, timestep, show):
        '''Figures out where to move each car that is headed
           toward a waiting rider or taking a rider to their
           destination. Returns None because it modifies the
           contents of RIDERS and CARS.'''
        for car in self.car_mgr.cars.values():
            if car.rider == NO_RIDER:
                continue    # car remains stationary awaiting a rider

            # This car has a rider or is going to pickup a rider...

            # Grab this car's current location and its destination,
            # which is either where to find a waiting rider or drop off
            # the current rider.
            loc = car.loc
            orig_loc = loc
            dest = car.dest

            # Compute how far in east-west and north-south blocks we
            # are between the car's current location and its
            # destination.
            delta_x = dest[0] - loc[0]
            delta_y = dest[1] - loc[1]
            # print('DEBUG:', f'delta = {delta_x, delta_y}')

            # This statement block assumes we know the indexing of the
            # city (i.e., north-south avenues and east-west streets run
            # on even indices).
            if delta_x == 0 and delta_y == 0:
                # Car is where next rider needs to be picked up. Don't
                # move and just do the pickup below.
                pass
            if (delta_x == 0 and dest[0] & 1 == 0) \
            or (abs(delta_x) == 1 and dest[0] & 1 == 1 and abs(delta_y) > 0):
                # Move north/south to hit destination
                if delta_y > 0:
                    loc = (loc[0], loc[1] + 1)    # move north
                else:
                    loc = (loc[0], loc[1] - 1)    # move south
            elif (delta_y == 0 and dest[1] & 1 == 0) \
            or (abs(delta_y) == 1 and dest[1] & 1 == 1 and abs(delta_x) > 0):
                # Move east/west to hit destination
                if delta_x > 0:
                    loc = (loc[0] + 1, loc[1])    # move east
                else:
                    loc = (loc[0] - 1, loc[1])    # move west
            elif delta_x == 0 and dest[0] & 1 == 1:
                # Move to an avenue
                loc = (loc[0] + 1, loc[1])        # move east
            elif delta_y == 0 and dest[1] & 1 == 1:
                # Move to a street
                loc = (loc[0], loc[1] + 1)        # move north
            else:
                # delta_x and delta_y are big in some sense
                if delta_x > 0 and loc[1] & 1 != 1:
                    loc = (loc[0] + 1, loc[1])    # move east
                elif delta_x < 0 and loc[1] & 1 != 1:
                    loc = (loc[0] - 1, loc[1])    # move west
                elif delta_y > 0 and loc[0] & 1 != 1:
                    loc = (loc[0], loc[1] + 1)    # move north
                else:
                    assert loc[0] & 1 != 1, 'Oops, I still missed something'
                    loc = (loc[0], loc[1] - 1)    # move south
            assert loc[0] & 1 == 0 or loc[1] & 1 == 0, \
                f"Car {car.id} moved into a building at {loc}"
            assert loc[0] >= 0 and loc[1] >= 0, \
                f"Car {car.id} at {orig_loc} going to {dest} moved to {loc}"
            car.loc = loc

            # Time to play with the car's rider's data structure too
            rider = self.rider_mgr.riders[car.rider]

            if not rider.waiting:
                # Once we know a car's new location, we update the
                # location of the car's rider.
                rider.loc = loc

            # Check to see if the car arrived at its destination
            if loc == dest:
                if rider.waiting:
                    if show > NOTHING:
                        print(f'{timestep}: Car {car.id} picked up rider {rider.icon()}')

                    # Update the car's destination and rider's waiting flag
                    car.dest = rider.dest
                    rider.waiting = False
                
                else:
                    if show > NOTHING:
                        print(f'{timestep}: Car {car.id} dropped off rider {rider.icon()}')

                    # Update the car's destination and delete rider
                    car.dest = NO_DEST
                    car.rider = NO_RIDER
                    del self.rider_mgr.riders[rider.id]


    def update_map(self):
        '''Helper routine for marking the location of all cars and
           riders on the city map. It first empties the map since
           this routine notes when more than one car or rider
           shares a map location. Returns None as the modifications
           are all done in the city map data structure.'''
        
        # Clear city before marking new positions
        self.city.reset()
        
        for rider in self.rider_mgr.riders.values():
            # print('DEBUG:', f'{rider.id}: loc = {rider.loc}, car = {rider.car}')

            if self.city.get_mark(rider.loc) != ' ':
                # Location contains at least one other rider
                mark = '*'
            else:
                # Convert rider's number into a letter
                mark = rider.icon()

            if rider.waiting:
                # Waiting riders are printed as little letters
                self.city.mark(rider.loc, mark)
            else:
                # Picked-up riders are printed as capital letters
                self.city.mark(rider.loc, mark.upper())    

        for car in self.car_mgr.cars.values():
            # print('DEBUG:', f'{car.id}: loc = {car.loc}, rider = {car.rider}')

            if self.city.get_mark(car.loc) != ' ':
                # Location contains another car and/or rider
                mark = '*'
            else:
                mark = car.id

            # Empty cars are printed with their identifiers while full
            # cars are printed with the rider's capitalized letter.
            if car.rider == NO_RIDER or self.rider_mgr.riders[car.rider].waiting:
                self.city.mark(car.loc, mark)
            else:
                # Printing done already in rider loop
                pass


    def _assign(self, rider, car):
        '''Updates the appropriate entries in cars and riders
           so that rider is assigned to car. Returns None.'''

        # For the rider, note the assigned car
        assert rider.car == NO_CAR, \
            f'Rider {rider.id} already assigned'
        rider.car = car.id

        # For the assigned car, note the rider to pick up
        # and where the rider is starting their trip.
        assert car.rider == NO_RIDER, \
            f'Car {car.id} already assigned'
        car.rider = rider.id
        car.dest = rider.loc


    def make_assignments(self, timestep, show):
        '''Figures out a good assignment of waiting riders to empty
           cars. For each waiting rider you want to assign to an
           empty car, you should call the method `assign`, which
           will update the appropriate fields in riders and cars.
           Returns None, since all work recorded in riders and cars.'''

        # DUMB DEFAULT IMPLEMENTATION (to be replaced): Walk through
        # the cars dictionary and put the empty cars into the `free`
        # list. Then, for each waiting rider in riders, assign the
        # first car in free to this rider until we run out of free
        # cars or waiting riders.

        # Make a list of the free-car objects
        free = []
        for car in self.car_mgr.cars.values(): 
            if car.rider == NO_RIDER:
                free.append(car)
        
        # Assign new rider to free car until no free cars
        for rider in self.rider_mgr.riders.values():
            if len(free) == 0:
                break    # no more free cars

            if rider.car == NO_CAR:
                car = free.pop()
                self._assign(rider, car)
                if show > NOTHING:
                    print(f'{timestep}: Rider {rider.icon()} assigned car {car.id}')


def main():
    print('   ### WELCOME to the Waylo simulator! ###\n')

    # Build a city and the managers
    sim = Simulator(6)

    # Grab an offline car setup from the user
    while True:
        ans = input('Which car layout would you like to use? ')
        success = sim.car_mgr.setup(ans)
        if success:
            break

    # Grab a rider-request stream
    while True:
        ans = input('Which hail stream would you like to use? ')
        success = sim.rider_mgr.setup(ans)
        if success:
            break

    # Grab desired timesteps in simulation
    while True:
        try:
            ans = input('How long would you like the simulation to run? ')
            sim.timesteps = int(ans)
            break
        except ValueError:
            print('Must be a positive integer. Try again...')

    # Print some helpful comments for the user
    welcome_msg = f'''
This simulator will run for {sim.timesteps} time steps, which
represents an entire day of activity. What follows are
the car locations at the start of the day. When ready,
hit the return key, and the simulation will start. 
'''

    print(welcome_msg)

    # Set car locations for start of day (computed offline)
    sim.update_map()
    print(sim.city)

    # Start the simulation when the user is ready
    input('Press the return key to start...')

    # Run simulation
    w, i, d = sim.simulate(DELAY)

    # Print results
    print('### Simulation Results ###')
    print(f'Total mins waiting = {w}')
    print(f'Total mins idle    = {i}')
    print(f'Total miles driven = {d}')

if __name__ == "__main__":
    main()

# Interesting runs
#
# - car_setup 1, rider_setup 1: 1 rider, 2 cars. Done in 12 timesteps.
#   Just a simulation to get you started.
#
# - car_setup 2, rider_setup 2: 3 riders, 2 cars. Done in 36 timesteps.
# - car_setup 1, rider_setup 2: 3 riders, 2 cars. Done in 33 timesteps.
#   The first of these looks like a good car setup, but its performance
#   is worse than the original silly setup.
#
# - car_setup 3, rider_setup 2: 3 riders, 2 cars. Done in 33 timesteps.
#   An even sillier car setup with good performance.
#
# - car_setup 3, rider_setup r: random riders, 2 cars. Unclear how long
#   it will run, but try at least 40 timesteps.
