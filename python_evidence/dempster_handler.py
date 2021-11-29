"""
TODO (Fabi):
    * Checks for types.
    * Beautify / document code.
    * Unit tests.
"""

def get_decimals(x: float) -> int:
    return len(str(x).split(".")[1])


class Measure:
    """represents a Measure"""
    categories = None
    probability = 0

    def __init__(self, categories: list, probability: float):
        """initialize measure, using the categories and the corresponding probability """
        self.categories = categories
        self.probability = probability

    def __str__(self):
        """return string, which contains both attributes of the measure"""
        return F"{self.categories}, {self.probability}"

    def __eq__(self, other):
        """check if given measure is the same as this measure"""
        if type(other) is not Measure:
            return False

        return self.categories == other.categories


class _MeasureCollector:
    """collects measures in list"""
    collection = []

    def __init__(self, collection: list, omega: list = None):
        """initialize measure collector, using the collection list and omega"""
        self.collection = collection

        # Add omega
        if omega is not None:
            self.add_omega(omega)

    def add_omega(self, omega: list):
        """add omega to measure collector"""
        p_omega = 1

        for measure in self.collection:
            p_omega -= measure.probability
            p_omega = round(p_omega, get_decimals(measure.probability))
            
        if p_omega < 0.0:
            raise Exception("Defined categories have a to high probability in sum!")
        
        self.collection.append(Measure(omega, p_omega))

    def accumulate_measures(self, other):
        """accumulate measures of a given measure collector and the own ones"""
        if type(other) is not _MeasureCollector:
            raise Exception("Other has to be the same type!")
        
        combined = []
        for own_measure in self.collection:
            for other_measure in other.collection:
                m = Measure(list(set(own_measure.categories) & set(other_measure.categories)),
                            own_measure.probability * other_measure.probability)
                if m not in combined:
                    combined.append(m)
                else:
                    for measure in combined:
                        if measure == m:
                            measure.probability += m.probability
        
        # Check if correction is needed.
        correction = self.check_correction(combined)
        if correction != -1:
            print("Correcting with ", correction)
            self.correct(combined, correction)

        return _MeasureCollector(combined)

    def correct(self, collection: list, correction: float):
        """correct all measure's probability within a collection by a given float value"""
        for measure in collection:
            if measure.categories == []:
                measure.probability = 0
            else:
                measure.probability *= correction

    def check_correction(self, collection: list):
        correction = -1
        for measure in collection:
            if measure.categories == []:
                correction = 1 / (1 - measure.probability)
        return correction

    def doubt(self, key: str):
        return 1 - self.__plausibility_single(key)

    def plausibility(self, x: list or str):
        if type(x) is list:
            return self.__plausibility_multi(x)
        else:
            return self.__plausibility_single(x)

    def __plausibility_single(self, key: str):
        plausibility = 0
        for measure in self.collection:
            if key in measure.categories:
                plausibility += measure.probability
        return plausibility

    def __plausibility_multi(self, collection: list):
        plausibility = 0
        collection = set(collection)
        for measure in self.collection:
            if len(collection & set(measure.categories)) > 0:
                plausibility += measure.probability
        return plausibility
    
    def belief(self, x: list or str):
        if type(x) is list:
            return self.__belief_multi(x)
        else:
            return self.__belief_single(x)

    def __belief_single(self, key: str):
        for measure in self.collection:
            if [key] == measure.categories:
                return measure.probability
        return 0
    
    def __belief_multi(self, collection: list):
        belief = 0
        for key in collection:
            belief += self.__belief_single(key)
        return belief

    def __str__(self):
        ret = ""
        for measure in self.collection:
            ret += str(measure)
            ret += "\n"
        return ret


class DempsterHandler:
    categories = None
    omega = None
    measures = []

    def __init__(self):
        """initialize Dempster handler"""
        pass
    
    def __get_omega(self):
        return self.omega.copy()

    def add_categories(self, categories: list):
        """add new list of categories to dempster handler"""
        self.categories = categories
        self.omega = self.categories.copy()

    def add_measure(self, measures: list):
        """add new list of measures to dempster handler"""
        # test if all categories in measure defined.
        for measure in measures:
            assert all(category in self.categories for category in measure.categories), "Category not defined!"

        # add measure collections
        measure_collector = _MeasureCollector(measures, self.__get_omega())
        self.measures.append(measure_collector)
        return measure_collector

    def accumulate_all_measures(self):
        """accumulate all measures and return them"""
        if len(self.measures) < 2:
            raise Exception("Cannot accumulate less than two measure sets.")

        accumulated_measures = self.measures[0]
        for ix in range(1, len(self.measures)):
            accumulated_measures = accumulated_measures.accumulate_measures(self.measures[ix])
        return accumulated_measures

    def __str__(self):
        ret = "______________\n"
        for measure_collection in self.measures:
            ret += str(measure_collection)
            ret += "\n______________\n\n"
        return ret