### section09/offline.py
from consts import NO_DEST, NO_RIDER


class Car:
    '''Data structure for an individual Waylo car. Each car has:
        *   An character (id) that uniquely identifies the car.
        *   A current location on the city map (loc).
        *   A destination (dest), which is NO_DEST when it is
            awaiting a rider assignment, a rider's location when
            it is traveling to pick up a rider, or a rider's
            destination when it is transporting a rider.
        *   A rider (rider), which is NO_RIDER when the car is
            awaiting a rider assignment or a rider's ID when it
            has been assigned a rider.
    '''
    def __init__(self, id, loc):
        self.id = id
        self.loc = loc
        self.dest = NO_DEST
        self.rider = NO_RIDER

    def __str__(self):
        v = f'Car {self.id} is at {self.loc}\n'

        # Add dest and rider to the returned string
        v += '  heading '
        if self.dest == NO_DEST:
            assert self.rider == NO_RIDER
            v += 'nowhere and awaiting a rider assignment'
        else:
            v += f'to {self.dest} for Rider {self.rider}'

        return v


class CarManager:
    '''Manages all Waylo cars in a city. It is an example of the
       manager pattern in software design. It is responsible for
       the creation, coordination, lookup, and lifecycle of a
       set of related objects or resources, which in our case are
       Waylo cars in the given city.'''
    
    def __init__(self, city):
        self.city = city
        self.cars = {}

    def _add_car(self, car_id, loc):
        '''Hidden helper method that avoids having to repeat the
           car_id while initializing the cars dictionary.'''
        self.cars[car_id] = Car(car_id, loc)

    def setup(self, config):
        '''Allows the user to select an initial configuration
           of cars for a given city. Returns True if setup
           succeeds and False otherwise.
        '''

        # Make sure that cars is an empty dictionary
        self.cars = {}

        # Available configurations
        if config == '1':
            self._add_car('1', (2,2))
            self._add_car('2', (4,4))
        elif config == '2':
            self._add_car('1', (2,2))
            self._add_car('2', (10,10))
        elif config == '3':
            self._add_car('1', (2,5))
            self._add_car('2', (2,4))
        elif config == '4':
            self._add_car('1', (2,2))
            self._add_car('2', (10,10))
            self._add_car('3', (6,6))
        else:
            print('Invalid choice. Valid responses: 1-4')
            return False
        
        # Validate starting configuration for Waylo cars
        assert len(self.cars) < 10, f'Too many cars in selected configuration'
    
        if self.city:
            # Validate starting car locations
            for car_id, car in self.cars.items():
                try:
                    self.city.get_mark(car.loc)
                except AssertionError:
                    assert False, \
                        f"Bad loc {car.loc} for Car {car_id}"

        return True


def main():
    '''Run a simple unit test'''

    manager = CarManager(None)

    # Pick a configuration
    manager.setup('2')

    # Fake an assignment to Car 1
    car1 = manager.cars['1']
    car1.dest = (4,4)
    car1.rider = 'b'

    # Show result of offline work for this configuration
    for car in manager.cars.values():
        print(car)

if __name__ == "__main__":
    main()