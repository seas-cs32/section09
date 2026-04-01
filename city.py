### section08/city.py
import sys, os

# Add chap11 to import path
sys.path.append(os.path.abspath("../chap11"))
import maze

class CitySqGrid(maze.Maze):
    """Abstraction: A CitySqGrid object represents a grid-like layout of
       a city with the same number of blocks in the north-south direction
       as it has in the east-west direction.

       Interface attributes:

       reset(): Resets all the city's state to the state when this
       instance was first created.

       The rest of the instance attributes are defined in class Maze.
    """
    # Implementation details:  Nothing important for this subclass, but
    # see class `Maze` important implementation details.

    def __init__(self, size):
        '''Initializes the instance as a {size}-by-{size} maze object'''

        # Sanity checks
        if size < 2 or size > 20:
            assert False, 'CitySqGrid size must be between 2 and 20 buildings'

        # Create the string that describes the configuration.  The actual
        # configuration written out is one of the test cases in maze.py.
        row1 = 'f5' * (size - 1) + 'f\n'
        row2 = 'a0' * (size - 1) + 'a\n'
        # Finally, put it all together with no trailing newline
        config = (row1 + row2) * (size - 1) + row1[0:-1]
        # print(f'DEBUG: config = {config}')

        # Put start in city center, which is just the point (size,size)
        # when we double size to make maze rows and columns!  We don't
        # care about the goal point in this application.
        endpts = f'{str(maze.NO_LOC).replace(" ","")} {str(maze.NO_LOC).replace(" ","")}'
        # print(f'DEBUG: endpts = {endpts}')
        
        maze.Maze.__init__(self, config, endpts)

        # Fill in the buildings.  Only seen on first build.  maze.reset
        # won't refill these buildings.
        for i in range(1, size * 2, 2):
            for j in range(1, size * 2, 2):
                self.mark((i, j), '#')


def main():
    # Just some tests

    print('\nBuilding a 3x3 city grid with Cosmo')
    city = CitySqGrid(3)
    city.print()

    print('\nBuilding a 4x4 city grid')
    city = CitySqGrid(4)
    city.print()

    print('\nBuilding a 5x5 city grid with Cosmo')
    city = CitySqGrid(5)
    city.print()

    print('\nBuilding a large city grid')
    city = CitySqGrid(16)
    city.print()

if __name__ == '__main__':
    main()