import pandas as pd


class Rules:
    """
    1	cheap, good food	    busy	    True	1	a cheap restaurant with good food is busy
    2	spanish	                long time	True	1	Spanish restaurants serve extensive dinners that take a long time to finish
    3	busy	                long time	True	2	you spend a long time in a busy restaurant (waiting for food)
    4	long time	            children	False	2	spending a long time is not advised when taking children
    5	busy	                romantic	False	2	a busy restaurant is not romantic
    6	long time	            romantic	True	2	spending a long time in a restaurant is romantic

    Our rules:
    7   [cheap, !centre]        busy        False   1   a cheap restaurant outside the centre is not busy
    8   [expensive]             long time   True    1   you spend a lot of time in an expensive restaurant
    9   [cheap, international]  fast food   True    1   cheap international food is fast food
    10  [steakhouse]            vegetarian  False   1   a steakhouse is not vegetarian
    11  [fast food]             romantic    False   2   fast food is not romantic
    12  [fast food]             children    True    2   children like fast food
    13  [vegetarian, cheap]     busy        True    2   a cheap vegetarian restaurant is busy
    """

    def __init__(self):
        self.consequents = {
            'busy': None,
            'long time': None,
            'children': None,
            'romantic': None,
            'fast food': None,
            'vegetarian': None
        }
        self.asked_consequents = {
            'busy': False,
            'long time': False,
            'children': False,
            'romantic': False,
            'fast food': False,
            'vegetarian': False
        }
        self.reason = {
            'busy': '',
            'long time': '',
            'children': '',
            'romantic': '',
            'fast food': '',
            'vegetarian': ''
        }
        # numbers indicating the priority of the rule. A higher number means that it is more important
        self.priorities = {
            'busy': 0,
            'long time': 0,
            'children': 0,
            'romantic': 0,
            'fast food': 0,
            'vegetarian': 0
        }
        # self.consequents_df = pd.DataFrame(self.consequents, index=[0])

    def extract_implications(self, string):
        string = string.lower()

        # Preference extraction by pricerange, area and food

        for pref in self.asked_consequents.keys():
            if pref in string:
                self.asked_consequents[pref] = True

        print(self.asked_consequents)
        return self.asked_consequents

    def __solve_rule(self, restaurant, consequents):
        # set antecedents known from the data set
        cheap = True if restaurant['pricerange'] == 'cheap' else False
        good = True if restaurant['foodquality'] == 'good' else False
        spanish = True if restaurant['food'] == 'spanish' else False
        centre = True if restaurant['area'] == 'centre' else False
        expensive = True if restaurant['pricerange'] == 'expensive' else False
        international = True if restaurant['food'] == 'international' else False
        steakhouse = True if (restaurant['food'] == 'steakhouse' \
                              or 'steakhouse' in restaurant['restaurantname']) else False

        # copy status from previous iteration
        new_consequents = consequents.copy()

        # check if previous consequence is either empty or current priority is higher
        if consequents['busy'] is None or 1 > self.priorities['busy']:
            # update new consequence
            new_consequents['busy'] = True if cheap and good else new_consequents['busy']
            # check if new consequence was updated
            # don't use if new_consequents['busy'] == True as that can be true from previous rules in this iteration
            if cheap and good:
                # update priority and set reason
                self.priorities['busy'] = 1
                self.reason['busy'] = "It is busy because it is good and cheap"

        if consequents['long time'] is None or 1 > self.priorities['long time']:
            new_consequents['long time'] = True if spanish else new_consequents['long time']
            if spanish:
                self.priorities['long time'] = 1
                self.reason['long time'] = "It takes a long time because it is spanish food"

        if consequents['long time'] is None or 3 > self.priorities['long time']:
            new_consequents['long time'] = True if consequents['busy'] is True else new_consequents['long time']
            if consequents['busy'] is True:
                self.priorities['long time'] = 3
                self.reason['long time'] = "It takes a long time because it is a busy restaurant"

        if consequents['children'] is None or 2 > self.priorities['children']:
            new_consequents['children'] = False if consequents['long time'] is True else new_consequents['children']
            if consequents['long time'] is True:
                self.priorities['children'] = 2
                self.reason['children'] = "It is not recommended with children because it takes long"

        if consequents['romantic'] is None or 2 > self.priorities['romantic']:
            new_consequents['romantic'] = False if consequents['busy'] is True else new_consequents['romantic']
            if consequents['busy'] is True:
                self.priorities['romantic'] = 2
                self.reason['romantic'] = "It is not romantic because it is busy"

        if consequents['romantic'] is None or 1 > self.priorities['romantic']:
            new_consequents['romantic'] = True if consequents['long time'] is True else new_consequents['romantic']
            if consequents['long time']:
                self.priorities['romantic'] = 1
                self.reason['romantic'] = "It is romantic because you usually spend a long time there"

        # Own rules
        if consequents['busy'] is None or 3 > self.priorities['busy']:
            new_consequents['busy'] = False if cheap and not centre else new_consequents['busy']
            if cheap and not centre:
                self.priorities['busy'] = 3
                self.reason['busy'] = "Since the restaurant is not in the centre, it is not busy"

        if consequents['long time'] is None or 2 > self.priorities['long time']:
            new_consequents['long time'] = True if expensive else new_consequents['long time']
            if expensive:
                self.priorities['long time'] = 2
                self.reason['long time'] = "Since the restaurant is expensive, people usually spend a long time there"

        if consequents['fast food'] is None or 1 > self.priorities['fast food']:
            new_consequents['fast food'] = True if cheap and international else new_consequents['fast food']
            if cheap and international:
                self.priorities['fast food'] = 1
                self.reason['fast food'] = "The restaurant serves fast food, as it is cheap and international"

        if consequents['vegetarian'] is None or 1 > self.priorities['vegetarian']:
            new_consequents['vegetarian'] = False if steakhouse else new_consequents['vegetarian']
            if steakhouse:
                self.priorities['vegetarian'] = 1
                self.reason['vegetarian'] = "As the restaurant is a steakhouse, it is not vegetarian"

        if consequents['romantic'] is None or 3 > self.priorities['romantic']:
            new_consequents['romantic'] = False if consequents['fast food'] is True else new_consequents['romantic']
            if consequents['fast food'] is True:
                self.priorities['romantic'] = 3
                self.reason['romantic'] = "The restaurant serves fast food, therefore, it is not romantic"

        if consequents['children'] is None or 1 > self.priorities['children']:
            new_consequents['children'] = True if consequents['fast food'] is True else new_consequents['children']
            if consequents['fast food'] is True:
                self.priorities['children'] = 1
                self.reason['children'] = "The restaurant serves fast food, therefore, children like it"

        if consequents['busy'] is None or 2 > self.priorities['busy']:
            new_consequents['busy'] = True if consequents['vegetarian'] is True and cheap else new_consequents['busy']
            if consequents['vegetarian'] is True and cheap:
                self.priorities['busy'] = 2
                self.reason['busy'] = "The restaurant is busy, because it serves cheap vegetarian food"

        return new_consequents

    def solve_rule(self, restaurant):
        # set consequents
        consequents = {
            'busy': None,
            'long time': None,
            'children': None,
            'romantic': None,
            'fast food': None,
            'vegetarian': None
        }

        not_changed = False

        # loop until new consequents are the same as previous consequents (closure under implication)
        while not_changed is False:
            new_consequents = self.__solve_rule(restaurant, consequents)
            if new_consequents == consequents:
                # quit if no change happened in this iteration
                not_changed = True
            else:
                # otherwise update consequents
                consequents = new_consequents

        self.consequents = new_consequents
        return self.consequents, self.reason


if __name__ == '__main__':
    rule = Rules()
    # rule.set_rules()
    # restaurant = {"restaurantname": "pizza express", "pricerange": "cheap", "area": "centre",
    #               "food": "spanish", "phone": "01223 324033", "addr": "", "post": "c.b 2", "foodquality": "moderate"}
    restaurant = {"restaurantname": "pizza express", "pricerange": "expensive", "area": "centre",
                  "food": "spanish", "phone": "01223 324033", "addr": "", "post": "c.b 2", "foodquality": "good"}

    print(rule.consequents)
    answer, reason = rule.solve_rule(restaurant)
    print(answer)
    print(reason)
    print(rule.priorities)
