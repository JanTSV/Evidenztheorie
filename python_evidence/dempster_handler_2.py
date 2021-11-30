

def get_decimals(x: float) -> int:
    return len(str(x).split(".")[1])


class Measure:
    categories = None
    probability = 0

    def __init__(self, categories, probability):
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

    def copy(self):
        return Measure(self.categories, self.probability)


class DempsterHandler:
    _all_categories = None
    all_measures = []

    def __init__(self, categories):
        self.clear()
        self._all_categories = categories
    
    def __get_omega(self):
        return self._all_categories.copy()

    def categories(self):
        return self._all_categories.copy()

    def __calculate_omega(self, measures):
        omega = self.__get_omega()
        p_omega = 1

        for measure in measures:
            p_omega -= measure.probability
            p_omega = round(p_omega, get_decimals(measure.probability))
            
        if p_omega < 0.0:
            raise Exception("Defined categories have a to high probability in sum!")

        return Measure(omega, p_omega)

    def add_measure(self, measures: list):
        measure_copy = self.__copy_measures(measures) 
        measure_copy.append(self.__calculate_omega(measures))

        self.all_measures.append(measure_copy)

    def __copy_measures(self, measures):
        measure_copy = []
        for measure in measures:
            measure_copy.append(measure.copy())
        return measure_copy

    def accumulate(self):
        accumulated = self.__accumulate(self.__copy_measures(self.all_measures))
        correction =  self.__check_correction(accumulated)
        if correction is not None:
            print("Correcting with ", correction)
            self.__correct(accumulated, correction)
        return accumulated

    def __accumulate(self, measures):
        while len(measures) > 1:
            accumulated = self.__accumulate_two(measures[0], measures[1])   
            measures.pop(0)
            measures.pop(0)
            measures.insert(0, accumulated)
        return measures[0]

    def __accumulate_two(self, collection_a, collection_b):
        accumulated = []
        for a in collection_a:
            for b in collection_b:
                m = Measure(list(set(a.categories) & set(b.categories)), a.probability * b.probability)
                if m not in accumulated:
                    accumulated.append(m)
                else:
                    for measure in accumulated:
                        if measure == m:
                            measure.probability += m.probability
        return accumulated

    def __correct(self, collection: list, correction: float):
        """correct all measure's probability within a collection by a given float value"""
        for measure in collection:
            if measure.categories == []:
                measure.probability = 0
            else:
                measure.probability *= correction

    def __check_correction(self, collection: list):
        """calculate correction for given collection of measures"""
        correction = None
        for measure in collection:
            if measure.categories == []:
                correction = 1 / (1 - measure.probability)
        return correction

    def print(self, measures: list):
        if len(measures) > 0 and (type(measures[0]) is not list):
            measures = [measures]
        print(self.__stingify(measures))

    def plausibility(self, accumulated: list, x: list or str):
        """call correct method to calculate plausibility of single or several measures"""
        if type(x) is list:
            return self.__plausibility_multi(accumulated, x)
        else:
            return self.__plausibility_single(accumulated, x)

    def __plausibility_single(self, accumulated: list, key: str):
        """calculate plausibility of single measure"""
        plausibility = 0
        for measure in accumulated:
            if key in measure.categories:
                plausibility += measure.probability
        return plausibility

    def __plausibility_multi(self, accumulated: list, collection: list):
        """calculate plausibility of multiple measures"""
        plausibility = 0
        collection = set(collection)
        for measure in accumulated:
            if len(collection & set(measure.categories)) > 0:
                plausibility += measure.probability
        return plausibility
    
    def belief(self, accumulated: list, x: list or str):
        """call correct method to calculate belief of single or multiple measures"""
        if type(x) is list:
            return self.__belief_multi(accumulated, x)
        else:
            return self.__belief_single(accumulated, x)

    def __belief_single(self, accumulated: list, key: str):
        """calculate belief of single measure"""
        for measure in accumulated:
            if [key] == measure.categories:
                return measure.probability
        return 0
    
    def __belief_multi(self, accumulated: list, collection: list):
        """calculate belief of multiple measures"""
        belief = 0
        for key in collection:
            belief += self.__belief_single(accumulated, key)
        return belief

    def doubt(self, accumulated: list, key: str):
        """calculate doubt"""
        return 1 - self.__plausibility_single(accumulated, key)

    def __stingify(self, measures: list):
        ret = "--------------------------------\n"
        for measure_coll in measures:
            ret += "++\n"
            for measure in measure_coll:
                ret += str(measure) + "\n"
            ret += "++\n\n"
        ret += "-------------------------------- \n\n"
        return ret
    
    def clear(self):
        self.all_measures = []

    def __str__(self):
        return self.__stingify(self.all_measures)
        
        
