"""COVID SIMULATOR"""

from __future__ import annotations
from random import random
from math import sin, cos, pi, sqrt
from turtle import Turtle, Screen, _Screen, done
from typing import Any
from time import time_ns

# constants
BOUNDS_WIDTH: int = 400
MAX_X: float = BOUNDS_WIDTH / 2
MIN_X: float = -MAX_X
VIEW_WIDTH: int = BOUNDS_WIDTH + 20

BOUNDS_HEIGHT: int = 400
MAX_Y: float = BOUNDS_HEIGHT / 2
MIN_Y: float = -MAX_Y
VIEW_HEIGHT: int = BOUNDS_HEIGHT + 20

CELL_RADIUS: int = 15
CELL_COUNT: int = 50
CELL_SPEED: float = 5.0

VULNERABLE: int = 0
INFECTED: int = 1

NUM_INFECTED: int = 3

IMMUNE: int = -1
RECOVERY_PERIOD: int = 90

# model

class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)

    def distance(self, second: Point) -> float:
        """Distance between two points."""
        xs: float = (self.x - second.x)**2
        ys: float = (self.y - second.y)**2
        distance: float = sqrt(xs + ys)
        return distance


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction
        self.sickness = VULNERABLE

    # Part 1) Define a method named `tick` with no parameters.
    # Its purpose is to reassign the object's location attribute
    # the result of adding the self object's location with its
    # direction. Hint: Look at the add method.

    def tick(self) -> None:
        """Reassign the object's location + direction."""
        self.location = self.location.add(self.direction)
        if self.is_infected() is True:
            self.sickness += 1
        if self.sickness > RECOVERY_PERIOD:
            self.immunize()

    def color(self) -> str:
        """Return the color representation of a cell."""
        if self.is_infected() is True:
            return "red"
        elif self.is_vulnerable() is True:
            return "gray"
        elif self.is_immune() is True:
            return "orange"
    
    def contract_disease(self) -> None:
        """Assigns INFECTED constant to the sickness attribute."""
        self.sickness = INFECTED
        return

    def is_vulnerable(self) -> bool:
        """Is the cell vulnerable to disease?"""
        if self.sickness == VULNERABLE:
            return True
        elif self.sickness == INFECTED:
            return False
        
    def is_infected(self) -> bool:
        """Is the cell infected?"""
        if self.sickness >= INFECTED:
            return True
        elif self.sickness == VULNERABLE:
            return False

    def contact_with(self, second: Cell) -> None:
        """Cells that make contact."""
        if self.is_vulnerable() is True:
            if second.is_infected() is True:
                self.contract_disease()
        elif self.is_infected() is True:
            if second.is_vulnerable() is True:
                second.contract_disease()
        return

    def immunize(self) -> None:
        """Assigns IMMUNE constant to sickness attribute."""
        self.sickness = IMMUNE
        return

    def is_immune(self) -> bool:
        """Checks to see if cell is immune."""
        if self.sickness == IMMUNE:
            return True
        else:
            return False


class Model:
    """The state of the simulation."""

    population: list[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float, infected: int, immune: int = 0):
        """Initialize the cells with random locations and directions."""
        self.population = []
        if infected >= cells:
            raise ValueError("Number of infected cells cannot exceed the population.")
        elif infected <= 0:
            raise ValueError("Number of infected cells must be greater than zero.")

        if immune >= cells:
            raise ValueError("Number of immune cells cannot exceed the population.")
        elif immune < 0:
            raise ValueError("Number of immune cells cannot be less than zero.")

        for i in range(infected, cells):
            start_location: Point = self.random_location()
            start_direction: Point = self.random_direction(speed)
            cell: Cell = Cell(start_location, start_direction)
            self.population.append(cell)
        for i in range(0, infected):
            start_location: Point = self.random_location()
            start_direction: Point = self.random_direction(speed)
            sick: Cell = Cell(start_location, start_direction)
            sick.contract_disease()
            self.population.append(sick)
    
    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)

    def random_location(self) -> Point:
        """Generate a random location."""
        start_x: float = random() * BOUNDS_WIDTH - MAX_X
        start_y: float = random() * BOUNDS_HEIGHT - MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle: float = 2.0 * pi * random()
        direction_x: float = cos(random_angle) * speed
        direction_y: float = sin(random_angle) * speed
        return Point(direction_x, direction_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > MAX_X:
            cell.location.x = MAX_X
            cell.direction.x *= -1.0
        if cell.location.x < MIN_X:
            cell.location.x = MIN_X
            cell.direction.x *= -1.0
        if cell.location.y > MAX_Y:
            cell.location.y = MAX_Y
            cell.direction.y *= -1.0
        if cell.location.y < MIN_Y:
            cell.location.y = MIN_Y
            cell.direction.y *= -1.0
            
    def check_contacts(self) -> None:
        """See if two cells come into contact with each other."""
        i: int = 0
        j: int = 1
        while i < len(self.population):
            while j < len(self.population):
                if self.population[i].location.distance(self.population[j].location) < CELL_RADIUS:
                    self.population[i].contact_with(self.population[j])
                j += 1
            i += 1
        return

    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        healthy: int = 0
        for cell in self.population:
            if cell.is_vulnerable() is True:
                healthy += 1
            elif cell.is_immune() is True:
                healthy += 1
        if healthy == len(self.population):
            return True
        return False


NS_TO_MS: int = 1000000


class ViewController:
    """This class is responsible for controlling the simulation and visualizing it."""
    screen: _Screen
    pen: Turtle
    model: Model

    def __init__(self, model: Model):
        """Initialize the VC."""
        self.model = model
        self.screen = Screen()
        self.screen.setup(VIEW_WIDTH, VIEW_HEIGHT)
        self.screen.tracer(0, 0)
        self.screen.delay(0)
        self.screen.title("Contagion Simulation - EX09")
        self.pen = Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)

    def start_simulation(self) -> None:
        """Call the first tick of the simulation and begin turtle gfx."""
        self.tick()
        done()

    def tick(self) -> None:
        """Update the model state and redraw visualization."""
        start_time = time_ns() // NS_TO_MS
        self.model.tick()
        self.pen.clear()
        for cell in self.model.population:
            self.pen.penup()
            self.pen.goto(cell.location.x, cell.location.y)
            self.pen.pendown()
            self.pen.color(cell.color())
            self.pen.dot(CELL_RADIUS)
        self.screen.update()

        if self.model.is_complete():
            return
        else:
            end_time = time_ns() // NS_TO_MS
            next_tick = 30 - (end_time - start_time)
            if next_tick < 0:
                next_tick = 0
            self.screen.ontimer(self.tick, next_tick)

def main() -> None:
    """Entrypoint of simulation."""
    model: Model = Model(CELL_COUNT, CELL_SPEED, NUM_INFECTED, 2)
    view_controller: ViewController = ViewController(model)
    view_controller.start_simulation()


if __name__ == "__main__":
    main()
