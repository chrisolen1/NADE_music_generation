#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 12:32:30 2019

@author: chrisolen
"""


from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

hello()


class Pizza(object):
    def __init__(self):
        self.toppings = []

    def __call__(self, topping):
        # When using '@instance_of_pizza' before a function definition
        # the function gets passed onto 'topping'.
        self.toppings.append(topping())

    def __repr__(self):
        return str(self.toppings)

pizza = Pizza()

@pizza
def cheese():
    return 'cheese'
@pizza
def sauce():
    return 'sauce'

print(pizza)
# ['cheese', 'sauce']


class Distance(object):
    def __init__(self):
        # This private attribute will store the distance in metres
        # All units provided using setters will be converted before
        # being stored
        self._distance = 0.0

    @property
    def in_metres(self):
        return self._distance

    @in_metres.setter
    def in_metres(self, val):
        try:
            self._distance = float(val)
        except:
            raise ValueError("The input you have provided is not recognised "
                             "as a valid number")

    @property
    def in_feet(self):
        return self._distance * 3.2808399

    @in_feet.setter
    def in_feet(self, val):
        try:
            self._distance = float(val) / 3.2808399
        except:
            raise ValueError("The input you have provided is not recognised "
                             "as a valid number")

    @property
    def in_parsecs(self):
        return self._distance * 3.24078e-17

    @in_parsecs.setter
    def in_parsecs(self, val):
        try:
            self._distance = float(val) / 3.24078e-17
        except:
            raise ValueError("The input you have provided is not recognised "
                             "as a valid number")
            
distance = Distance()
distance.in_metres = 1000
distance.in_metres
distance.in_feet
distance.in_parsecs
distance.in_metres = "well fuckkkk you"

