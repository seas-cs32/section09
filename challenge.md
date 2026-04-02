### Introduction to today's lab

Last week, you completed a simulation of a ride-hailing service built on driverless vehicles. While Python is an object-oriented programming language, we didn't define any classes in what we wrote. Today's challenge asks you to reimagine last week's code base using classes. This work will allow you to experience the difference in the programming styles.

We will focus on the main subset of files from last week: `offline.py` that defines the data structures for our Waylo cars; `online.py` that defines the data structures for Waylo riders and their hails; and `simulate.py` that uses these data structures. This week's code distribution also contains `consts.py` and `city.py`, which we need to run the simulator but won't touch in this lab.

> NOTE: Professor Smith used OpenAI's GPT4.1, Anthropic's Claude 4, and Anysphere's Cursor AI in producing the Python code in this week's lab. He did it less for the code-writing help (as he enjoys coding) and more for an exploration of alternatives.

Open the "Section Week #9" assignment on Gradescope, which contains questions you'll answer as you work through these steps.

----

### Step 1: Headache #1 in the procedure-based approach

You've heard the instructors say that you should avoid _global variables_ unless they are read-only constants, such as those capitalized names in `consts.py`. 

> **Example:** When a rider first appears on the map awaiting an assignment to a Waylo car, their `car` attribute is set to `NO_CAR`, which has the value `-1`. This chosen value is arbitrary; it needs to only be something that isn't a valid car identifier. This should remind you of our discussion (in Chapter 2) of the `-1` value returned from `str.find` when the substring you sought wasn't found. By giving this special value a name (i.e., `NO_CAR`), our code is one step better than what we wrote in `chap02/script32.py`.

Global variables are definitions like `NO_CAR` in `consts.py` and `car_setup` in `section08/offline.py`. While we know that the Python interpreter reads a script from top to bottom noting statements like the definition of `CARS` and `car_setup` in `section08/offline.py`, we think of our scripts' execution as beginning in a `main` function, where we typically start interacting with the script's user and manipulating the program's internal state.

> **Example:** Inside the `main` routine of `section08/offline.py`, the script defines a local name `v` and then redefines it. This is manipulating the program's internal state. It is something you cannot do to a global variable because Python considers any name that is assigned a value within a function to be a local variable of that function. The only exceptions to this rule are when the name appears as one of the function's formal parameters or in a `global` statement.

The name `next_rider` in `section08/online.py` is an example of a global variable that we update during execution. It is updated in the functions `rider_setup` and `add_hails`, which both include the statement `global next_rider`.

**CHANGE THE CODE:**

1.  Find the `global` statement in the `add_hails` function in `section08/online.py`, and review the uses of this name in that function. As it says in the commment at the top of the file, `next_rider` keeps track of the identifier that the simulation will give to the next hailing rider.

2.  Comment out the `global` statement in the `add_hails` function in `section08/online.py`, and run (in your `section08` directory) `python3 simulate.py`. You can answer the questions with car layout 1, hail stream 1, and 15 simulation steps. Do you understand why you got an `UnboundLocalError` message? If not, ask a member of the teaching staff.

3.  Make sure you remove the comment character from the `global` statement before proceeding.

**Lesson:** Keeping track of what's local and what's global as your program grows in size and complexity is hard and errorprone.

> To avoid using a non-read-only global variable in a procedural programming language, you're typically told to pass the value as a parameter to the functions that need it and return the updated value (if the function updates it).
> 
> Although it is a fairly simple example, `timestep` is a variable like `next_rider` that is incremented during the simulation and used in several functions (but updated in only one). Notice how `timestep` is passed as a parameter to those functions that need it. If it was defined as a global variable, we wouldn't need to pass it as a parameter, but we would need to put a `global timestep` in the function `simulate` in `section08/simulate.py`.
> 
> We bring this up because you'll see in a later step how object-oriented programming solves this situation, which currently has no good choice.

----

### Step 2: Headache #2 in the procedure-based approach

>**Answer on Gradescope:** Write the names of all of the global variables that are defined in the files `section08/offline.py`, `section08/online.py`, and `section08/simulate.py`. We're not asking about functions; we're only asking about variables like `next_rider`.

The names spelled in all caps are all read-only global variables. You can verify this by checking to see if any function contains a `global` statement with these names. HINT: You won't find any.

But you know that the simulation adds riders to the variable `RIDERS` as it computes what takes place in a day. How does this work?

This variable and its brethren are read-only globals because _the script changes only the elements of these mutable sequences._

**CHANGE THE CODE:**

You might think, "That's not a headache." But let's change the first non-comment statement in `car_setup` (in `section08/offline.py`).

1.  Replace `CARS.clear()` with `CARS = {}`. If we want an empty dictionary, simply make `CARS` point to one, right?

2.  Run (in your `section08` directory) `python3 simulate.py`. You can answer the simulator's questions with car layout 1, hail stream 1, and 15 simulation steps. 

> **Answer on Gradescope:** Why don't you ever see a car on the map?

3.  Undo this edit before proceeding.

**Lesson:** Keeping track of what's local and what's global as your program grows in size and complexity is hard and errorprone. Yea, same lesson but with a different example.

----

### Step 3: Using classes for cars

We have started the conversion of last week's simulator into one that uses classes. Let's start with `offline.py`, which defines the data structures for our Waylo cars. 

Open up `section08/offline.py` and `section09/offline.py` in side-by-side editor windows, and work through the following three observations:

1.  Instead of a global `CARS` dictionary and a comment describing the fields for each dictionary entry (i.e., each Waylo car), you'll find two classes.

    * `class Car` allows you to build an object that represents an individual Waylo car. Notice that we no longer need to create a dictionary of dictionaries. With this new class, our inner dictionary in `section08` has become objects with data attributes named for that inner dictionary's keys. The outer dictionary's key (i.e., the car id) is also stored as a data attribute in `Car`.
    * `class CarManager` has a data attribute called `cars` that is the new dictionary of Waylo cars, i.e., it replaces the `CARS` dictionary. It might sound silly to bury this dictionary inside a class, but notice that we can define other data attributes (e.g., `city`) in the `class CarManager`. These data attributes act like global variables for every method in the class. What was the function `car_setup` has become the class method `setup`, which now takes only a single formal parameter `config` (ignoring the ubiquitous `self` parameter). The function `car_setup` needed `city` as a formal parameter, but in `class CarManager`, the data attribute `city` acts like a global variable to all methods of `class CarManager`. Sweet!
    
2.  Inside the method `CarManager.setup`, look at what happened to the statement that made sure we began with an empty `CARS` dictionary. It is now `self.cars = {}`. Either this or `self.cars.clear()` would work just fine. `self.cars` says that we want the class's data attribute and not a local variable of the method `CarManager.setup`. This is much better solution than an easy-to-forget-about `global` statement.

3.  Finally, compare the two `main` functions (i.e., the ones in `section08/offline.py` and `section09/offline.py`). The code now creates a `CarManager` object (without a `city`) and then calls `setup` on that object with a configuration. Take a moment to understand the faking of an assignment to Car 1, but we want you to focus on the printing loop. All of the detail of printing a Waylo car has been encapsulated in the magic `__str__` method in `class Car`. This is a more modular design.

**RUN THE CODE:** In `section09`, run `python3 offline.py` and verify that you get the same output as you'd see running that command in `section08`. Two different implementations with the same behavior.

----

### Step 4: Using classes for riders

With the help of a LLM, we performed a similar transformation on `section08/online.py` to create `section09/online.py`. In the new file, you'll find a `class Rider` and a `class RiderManager`. 

1.  Notice which functions became not just methods, but methods marked by the leading-single-underbar convention, which in Python means "for internal use."

    * The function `rider_icon` became the method `icon` of `class Rider`, since it deals with a single rider.
    * The functions `rider_setup` and `add_hails`, which `simulate.py` imports from `online.py` became the public methods `setup` and `add_hails` of `class RiderManager`.
    * The functions `rand_locs` and `rand_schedule` became the "internal-use" methods `_rand_locs` and `_rand_schedule`. The `_` at the start of these method names is a Python convention that says these methods are helpers to other methods in the class, and we don't expect them to be used outside of it (although they might be used by subclasses). This information wasn't at all obvious in `section08/online.py`.

2.  Look at the implementation of `rand_locs` in `section08/online.py` and `_rand_locs` in `section09/online.py`. You'll notice that both scripts define `rand_loc` as an _inner function_, i.e., it sits inside the definition of the function `rand_locs` and similarly inside the definition of the method `_rand_locs`. It performs the same in both cases: the name `rand_loc` acts like any other local variable name inside the lexical scoping of `rand_locs` and `_rand_locs` (e.g., like the local variable `max_x`). This means that you cannot call `rand_loc` outside the function or method, and if you do, you'll get a `NameError`. If you don't understand the term "lexical scoping," ask a member of the teaching staff.

3.  We won't touch on every change, but spend a moment looking at the two implementations of rider setup.

    * The global variable `next_rider` has become a data attribute of the `class RiderManager`, which removes the annoying global variable issues discussed above.
    * The method `setup` doesn't have to clear the `hails` list because it can just create a new list and name it `self.hails`.

The result of these changes is a module that's easier to understand and less likely to contain errors.

----

### Step 5: There's even a `simulate` class

Object-oriented programmers take what we've been doing in `offline.py` and `online.py` one step further. Look in `section09/simulate.py`, and you'll see that this file starts with a `class Simulator`, which includes all functions in `section08/simulate.py` as methods.

A positive outcome is that the things the simulation depends upon have become data attributes of a simulation object (i.e., a city grid in `city`, a car layout in `CarManager`, a rider schedule in `RiderManager`, and the simulation duration in `timesteps`).

The `_timesteps` data attribute of `class Simulator` is defined with a leading underbar in `Simulator.__init__`, which takes us back to the for-internal-use convention. But we want users of this simulator class to set this data attribute, as we'll see in next step. To understand what's going on read on!

----

### Step 6: Python decorators and using properties

Open `section09/simulate.py` in your IDE's code editor and look at the start of its `main` function. It prints a welcome message, builds a `Simulator` object, and asks the user for an offline car setup, rider-request stream, and how many timesteps to run the simulation. Focus on the code that grabs the desired number of timesteps.

You'll see that we've used the infinite-loop pattern that keeps asking the user for a timesteps value until it gets a valid one. You know that the built-in function `int` throws a `ValueError` if the user types a string that isn't an integer in a string suit, but:

*   How does this loop make sure that `sim.timesteps` is a positive integer? It doesn't make sense to run the simulation for zero or a negative number of timesteps.
*   What is `sim.timesteps` anyway? The data attribute you saw in `Simulator.__init__` is `self._timesteps`, i.e., the data attribute name is `_timesteps` not `timesteps`.

What's going on here is that we don't want users of `class Simulator` to update its timesteps data attribute with any value. We want to allow only certain updates. To enforce this, the code uses [Python decorators](https://realpython.com/primer-on-python-decorators/) and [properties](https://realpython.com/python-property/). (The links take you to tutorials on RealPython.com, in case you want to learn more than what follows.)

Quoting ChatGPT 5, "a _property_ is a special kind of attribute that lets you define methods that act like attributes. It's a way to _control access_ to instance variables (attributes) without changing how they're accessed by code that uses the class. In other words, properties let you use dot notation (obj.attribute) while still allowing logic like validation, computation, or read-only enforcement under the hood."

In other words, when we write `sim.timesteps = int(ans)` in `main`, Python knows that we're actually calling the `timesteps` method that takes a `value` and is decorated with `@timesteps.setter`. Notice that this method raises a `ValueError` if `value` is less than or equal to 0. There's our check. If not, it sets `self._timesteps` to the value. There's our assignment to the "for-internal-use" data attribute.

The other method in `class Simulator` named `timesteps` is the "getter," which returns the "for-internal-use" data attribute `_timesteps`.

Don't let the syntax in the class definition confuse you. We're simply hiding some extra work in this class definition that we'd like done so that the user of our class can write simpler code.

----

### Step 7: Build a class for hails

It's time to try your hand at converting generic data structures into your own class-based ones. In particular, the code in `RiderManager.setup` and `RiderManager._rand_schedule` in `section09/online.py` still build rider hails using Python tuples. This means that the method `RiderManager.add_hails` converts a hail into a `Rider` object using code like `self.hails[self.next_rider][1]`. This expression says that we want to grab some part of the hail at the `next_rider` index, but what part of a hail does the magic number `1` represent? It's too easy to make an error in such code!

**Your task:** Create a new `Hail` class in `section09/online.py` and replace any code that creates a hail tuple with a `Hail` object. In addition to creating the `class Hail`, you will need to:

*   Update the `RiderManager` class and its methods to use `Hail` objects instead of tuples.
*   Fix the comment on `class RiderManager`, since you've invalidated some of what it currently says.
*   Modify the unit test code in `main`.
*   Run `python3 online.py` in `section09` to verify that the unit test continues to work.
*   Run `python3 simulate.py` in `section09` with a random rider stream to verify you haven't made any other mistakes.

**Key benefits of your work (a before-and-after view):**

Before (tuple-based approach):
```python
# Creating a hail
hail = (1, (3, 8), (6, 6))

# Accessing hail data
timestep = hail[0]      # Magic number indexing
location = hail[1]      # Hard to remember which index is what
destination = hail[2]   # Error-prone
```

After (class-based approach):
```python
# Creating a hail
hail = Hail(timestep=1, loc=(3, 8), dest=(6, 6))

# Accessing hail data
timestep = hail.timestep   # Clear, self-documenting
location = hail.loc        # No magic numbers
destination = hail.dest    # Type-safe access
```

>**When you're finished, upload** your final version of `online.py` to the last question on Gradescope.

Version 20260324
