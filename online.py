### section09/online.py
import random
from consts import NO_CAR, NOTHING


class Rider:
    '''Data structure for an individual Waymo riders.
    
    Each rider has:
    *  An number (id) that uniquely identifies the rider. That
       id number will be turned into a letter when printed.
    *  A current location (loc) on the city map.
    *  A destination (dest) where rider wishes to go.
    *  A car (car) transporting this rider.
    *  A flag (waiting), which is True if waiting for pickup.
    '''
    def __init__(self, id, loc, dest):
        self.id = id
        self.loc = loc
        self.dest = dest
        self.car = NO_CAR
        self.waiting = True

    def icon(self):
        '''Turns the rider's identifier (an int) into
           a rider icon (a letter).'''
        return chr(ord('a') + self.id)


class RiderManager:
    '''Manage riders and their assignments to cars'''
    def __init__(self, city):
        self.city = city

        # Initially, there are no riders on the city map
        self.riders = {}

        # Hails is a schedule of when riders enter the map. Its
        # format is: (timestep, loc, dest). The list that
        # represents this schedule must be ordered in increasing
        # timestep. Each hailing rider is automatically given an
        # id, which is the index of that rider in the HAILS list.
        # The total number of riders must be less than 26, which
        # is a limitation due to how we print the map.
        self.hails = []

        # Track of the next rider to appear from the hails list
        self.next_rider = 0

    def _rand_locs(self):
        '''Hidden helper method that returns a pair of random
           start and destination locations in the city. It
           guarantees that the locations are within the city
           and not inside a building.'''
        max_x = self.city.width + 1
        max_y = self.city.height + 1

        def rand_loc():
            '''Generates a single random location in the city'''
            # These maximums are weird due to implementation of maze.py
            loc_x = random.randint(0, max_x)
            if loc_x & 1 == 0:
                loc_y = random.randint(0, max_y)
            else:
                # x is odd so force y to be even
                loc_y = random.randint(0, max_y // 2) * 2
            return (loc_x, loc_y)
        
        # Create a random starting location
        start_loc = rand_loc()

        # Create a random destination that isn't the start_loc
        while True:
            dest_loc = rand_loc()
            if dest_loc != start_loc:
                return (start_loc, dest_loc)

    def _rand_schedule(self):
        '''Hidden helper method that randomly creates a hails list.
           It is hardwired with constants that define:
       
           *  what's the first timeslot for a hail
           *  how many hails will be produced
           *  how far apart can hails be

           Feel free to change these ranges.
        '''
        schedule = []

        # Generate a random starting timeslot
        timeslot = random.randint(1, 3)

        # Generate a random number of hailing riders
        num_riders = random.randint(1, 10)

        # Generate the schedule with a randomly generated
        # distance between hails.
        for _ in range(num_riders):
            # Generate random start and dest locations
            start_loc, dest_loc = self._rand_locs()

            # Add the new hail to the schedule's end
            schedule.append((
                timeslot,
                start_loc,
                dest_loc
            ))

            # Randomly move the timeslot forward
            timeslot += random.randint(0,7)

        return schedule

    def setup(self, config):
        '''Allows the user to select a ride-request stream
        '''
        # Clear the riders list and the tracker variable
        self.riders = {}
        self.next_rider = 0

        # Available configurations, which set the hails list
        if config == '1':
            self.hails = [( 1, (3,8), (6,6))]
        elif config == '2':
            self.hails = [
                ( 1, (3,8), (6,6)),
                ( 8, (8,7), (2,1)),
                (12, (9,2), (0,6)),
            ]
        elif config == 'r':
            # Randomly generate a schedule of rider hails
            self.hails = self._rand_schedule()
        else:
            print('Invalid choice. Valid responses: 1-2, r')
            return False

        # Validate hail stream
        assert len(self.hails) < 26, 'Too many riders in hail stream'
    
        if self.city:
            # Validate starting rider locations
            for rider_id, hail in enumerate(self.hails):
                try:
                    self.city.get_mark(hail[1])
                except AssertionError:
                    assert False, \
                        f"Bad loc {hail[1]} for Rider {rider_id}"
                try:
                    self.city.get_mark(hail[2])
                except AssertionError:
                    assert False, \
                        f"Bad dest {hail[2]} for Rider {rider_id}"                

        return True

    def add_hails(self, timestep, show):
        '''Adds new riders, if any at the given timestep'''

        # For reasons of rider-icon encoding and limits on
        # simulation time, don't generate more than 26 riders.
        if self.next_rider > 25:
            return

        # Pull hails from HAILS list for this timestep
        while self.next_rider < len(self.hails) \
            and timestep == self.hails[self.next_rider][0]:

            # Create a new rider
            rider = Rider(
                id=self.next_rider,
                loc=self.hails[self.next_rider][1],
                dest=self.hails[self.next_rider][2]
            )

            # Add new rider to the map
            self.riders[self.next_rider] = rider

            if show > NOTHING:
                # Document the action
                print(f'{timestep}: Rider {rider.icon()} hails a car')

            # Bump tracker
            self.next_rider += 1


def main():
    '''Run a simple unit test'''

    manager = RiderManager(None)
    
    # Pick a configuration
    manager.setup('2')

    # Show schedule of rider hails
    indent = 2
    for rider_id, hail in enumerate(manager.hails):
        rider = Rider(rider_id, hail[1], hail[2])
        print(f'Rider {rider_id} ({rider.icon()})')
        print(' ' * indent, 'timestep:', hail[0])
        print(' ' * indent, 'location:', rider.loc)
        print(' ' * indent, 'destination:', rider.dest)

if __name__ == "__main__":
    main()
