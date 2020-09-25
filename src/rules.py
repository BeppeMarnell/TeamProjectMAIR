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
    9   [cheap, international]  fast food   True    1   cheap internationational food is fast food
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
        # self.consequents_df = pd.DataFrame(self.consequents, index=[0])

    def extract_implications(self, string):
        string = string.lower()

        # Preference extraction by pricerange, area and food

        for pref in self.asked_consequents.keys():
            if pref in string:
                self.asked_consequents[pref] = True

        print(self.asked_consequents)
        return self.asked_consequents

    def solve_rule(self, restaurant):
        # TODO set priorities of rules
        # print(self.consequents)
        # print(restaurant['pricerange'])
        cheap = True if restaurant['pricerange'] == 'cheap' else False
        good = True if restaurant['foodquality'] == 'good' else False
        spanish = True if restaurant['food'] == 'spanish' else False
        centre = True if restaurant['area'] == 'centre' else False
        expensive = True if restaurant['pricerange'] == 'expensive' else False
        international = True if restaurant['food'] == 'international' else False
        steakhouse = True if (restaurant['food'] == 'steakhouse' \
                             or 'steakhouse' in restaurant['restaurantname']) else False

        if self.consequents['busy'] is None:
            self.consequents['busy'] = True if cheap and good else None
            if self.consequents['busy']:
                self.reason['busy'] = "It is busy because it is good and cheap"

        if self.consequents['long time'] is None:
            self.consequents['long time'] = True if spanish else None
            if self.consequents['long time']:
                self.reason['long time'] = "It takes a long time because it is spanish food"

        if self.consequents['long time'] is None:
            self.consequents['long time'] = True if self.consequents['busy'] is True else None
            if self.consequents['long time']:
                self.reason['long time'] = "It takes a long time because it is a busy restaurant"

        if self.consequents['children'] is None:
            self.consequents['children'] = False if self.consequents['long time'] is True else None
            if self.consequents['children'] is False:
                self.reason['children'] = "It is not recommended with children because it takes long"

        if self.consequents['romantic'] is None:
            self.consequents['romantic'] = False if self.consequents['busy'] is True else None
            if self.consequents['romantic'] is False:
                self.reason['romantic'] = "It is not romantic because it is busy"

        if self.consequents['romantic'] is None:
            self.consequents['romantic'] = True if self.consequents['long time'] is True else None
            if self.consequents['romantic']:
                self.reason['romantic'] = "It is romantic because you usually spend a long time there"

        # Own rules
        if self.consequents['busy'] is None:
            self.consequents['busy'] = False if cheap and not centre else None
            if self.consequents['busy'] is False:
                self.reason['busy'] = "Since the restaurant is not in the centre, it is not busy"

        if self.consequents['long time'] is None:
            self.consequents['long time'] = True if expensive else None
            if self.consequents['long time']:
                self.reason['long time'] = "Since the restaurant is expensive, people usually spend a long time there"

        if self.consequents['fast food'] is None:
            self.consequents['fast food'] = True if cheap and international else None
            if self.consequents['fast food']:
                self.reason['fast food'] = "The restaurant serves fast food, as it is cheap and international"

        if self.consequents['vegetarian'] is None:
            self.consequents['vegetarian'] = False if steakhouse else None
            if self.consequents['vegetarian'] is False:
                self.reason['vegetarian'] = "As the restaurant is a steakhouse, it is not vegetarian"

        if self.consequents['romantic'] is None:
            self.consequents['romantic'] = False if self.consequents['fast food'] else None
            if self.consequents['romantic'] is False:
                self.reason['romantic'] = "The restaurant serves fast food, therefore, it is not romantic"

        if self.consequents['children'] is None:
            self.consequents['children'] = True if self.consequents['fast food'] else None
            if self.consequents['children']:
                self.reason['children'] = "The restaurant serves fast food, therefore, children like it"

        if self.consequents['busy'] is None:
            self.consequents['busy'] = True if self.consequents['vegetarian'] and cheap else None
            if self.consequents['busy']:
                self.reason['busy'] = "The restaurant serves busy, because it serves cheap vegetarian food"

        return self.consequents, self.reason

    # def solve_rule(self, rule, expected_result, restaurants):
    #     results = []
    #     for restaurant in restaurants:
    #         consequents, reason = self.__solve_rule(restaurant)
    #         results.append((consequents, reason))


if __name__ == '__main__':
    rule = Rules()
    # rule.set_rules()
    # restaurant = {"restaurantname": "pizza express", "pricerange": "cheap", "area": "centre",
    #               "food": "spanish", "phone": "01223 324033", "addr": "", "post": "c.b 2", "foodquality": "moderate"}
    restaurant = {"restaurantname": "steakhouse express", "pricerange": "cheap", "area": "centre",
                  "food": "international", "phone": "01223 324033", "addr": "", "post": "c.b 2", "foodquality": "moderate"}

    restaurant = pd.DataFrame(restaurant, index=[0])
    print(rule.consequents)
    answer, reason = rule.solve_rule('romantic', restaurant)
    print(answer)
    print(reason)
