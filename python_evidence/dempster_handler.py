

def get_decimals(x: float) -> int:
    return len(str(x).split(".")[1])


class Measure:
    categories = None
    probability = 0

    def __init__(self, categories: list, probability: float):
        self.categories = categories
        self.probability = probability

    def __str__(self):
        return F"{self.categories}, {self.probability}"

    def __eq__(self, other):
        if type(other) is not Measure:
            return False

        return self.categories == other.categories


class _MeasureCollector:
    collection = []

    def __init__(self, collection: list, omega: list = None):
        self.collection = collection

        # Add omega
        if omega is not None:
            self.add_omega(omega)

    def add_omega(self, omega):
        p_omega = 1

        for measure in self.collection:
            p_omega -= measure.probability
            p_omega = round(p_omega, get_decimals(measure.probability))
            
        if p_omega < 0.0:
            raise Exception("Defined categories have a to high probability in sum!")
        
        self.collection.append(Measure(omega, p_omega))

    def accumulate_measures(self, other):
        if type(other) is not _MeasureCollector:
            raise Exception("Other has to be the same type!")
        
        combined = []
        for own_measure in self.collection:
            for other_measure in other.collection:
                m = Measure(list(set(own_measure.categories) & set(other_measure.categories)),
                            own_measure.probability * other_measure.probability    
                           )
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
       pass
    
    def __get_omega(self):
        return self.omega.copy()

    def add_categories(self, categories: list):
        self.categories = categories
        self.omega = self.categories.copy()

    def add_measure(self, measures: list):
        # test if all categories in measure defined.
        for measure in measures:
            assert all(category in self.categories for category in measure.categories), "Category not defined!"

        # add measure collections
        mc = _MeasureCollector(measures, self.__get_omega())
        self.measures.append(mc)
        return mc

    def __str__(self):
        ret = "______________\n"
        for measure_collection in self.measures:
            ret += str(measure_collection)
            ret += "\n______________\n\n"
        return ret