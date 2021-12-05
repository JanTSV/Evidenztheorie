

def get_decimals(x: float) -> int:
    """
    Calculate number of decimal points.

    Args:
        x (float): Number.
    
    Returns:
        int: Number of decimal points.
    """
    return len(str(x).split(".")[1])


class Measure:
    """
    Class to represent an evidence measure.
    """
    categories = None
    probability = 0

    def __init__(self, categories: list, probability: float):
        """
        Initialize with categories and probability.
        """
        if probability > 1.0:
            raise ValueError("Probability cannot be greater than 1.0")
        self.categories = categories
        self.probability = probability
    
    def __str__(self):
        """
        Return string, which contains both attributes of the measure

        Returns:
            str: String representation of object.
        """
        return F"{self.categories}, {self.probability}"

    def __eq__(self, other):
        """
        Check if given measure is the same as this measure
        
        Args:
            other: Other measure.
        
        Returns: 
            bool: Equal or not.
        """
        if type(other) is not Measure:
            return False

        return self.categories == other.categories

    def copy(self):
        """
        Copy this measure.

        Returns:
            Measure: Copied new object.
        """
        return Measure(self.categories, self.probability)


class DempsterHandler:
    """
    Class for handling measures:
        * Save measures.
        * Accumulate measures.
        * Calculate belief, plausibility and doubt.
    """
    _all_categories = None
    all_measures = []

    def __init__(self, categories: list):
        """
        Init.
        """
        self.clear()
        self._all_categories = categories
    
    def __get_omega(self):
        """
        Get the omega measure.

        Returns:
            list: Omega.
        """
        return self._all_categories.copy()

    def categories(self):
        """
        Get all possible categories.

        Returns:
            list: Categories.
        """
        return self._all_categories.copy()

    def __calculate_omega(self, measures: list):
        """
        Calculate omega measure.

        Args:
            measures (list): List of measures.
        """
        omega = self.__get_omega()
        p_omega = 1.0

        for measure in measures:
            p_omega -= measure.probability
            p_omega = round(p_omega, get_decimals(measure.probability))
            
        if p_omega < 0.0:
            raise ValueError("Defined categories have a to high probability in sum!")

        return Measure(omega, p_omega)

    def add_measure(self, measures: list):
        """
        Add measure to handler.

        Args:
            measures (list): List of measures.
        """
        # Check if all given categories exist.
        for measure in measures:
            for category in measure.categories:
                if category not in self._all_categories:
                    raise KeyError(F"Category {category} is not defined in dempster handler.")

        measure_copy = self.__copy_measures(measures) 
        measure_copy.append(self.__calculate_omega(measures))

        self.all_measures.append(measure_copy)

    def __copy_measures(self, measures: list):
        """
        Copy list of measures.

        Args:
            measures (list): List of measures.
        """
        measure_copy = []
        for measure in measures:
            measure_copy.append(measure.copy())
        return measure_copy

    def accumulate(self):
        """
        Accumulate all defined measures and correct them if necessary.

        Returns:
            list: Accumulated measures.
        """
        accumulated = self.__accumulate(self.__copy_measures(self.all_measures))
        correction =  self.__check_correction(accumulated)
        if correction is not None:
            print("Correcting with ", correction)
            self.__correct(accumulated, correction)
        return accumulated

    def __accumulate(self, measures: list):
        """
        Accumulate all meaasures and pop them until there is only one left.

        Args:
            measures (list): List of measures to accumulate.

        Returns:
            list: Accumulated measures.
        """
        while len(measures) > 1:
            accumulated = self.__accumulate_two(measures[0], measures[1])   
            measures.pop(0)
            measures.pop(0)
            measures.insert(0, accumulated)
        return measures[0]

    def __accumulate_two(self, measures_a: list, measures_b: list):
        """
        Accumulate two measures.

        Args:
            measures_a (list): List of a evidence measure.
            measures_b (list): List of other evidence measure

        Returns:
            list: Accumulated.
        """
        accumulated = []
        for a in measures_a:
            for b in measures_b:
                m = Measure(list(set(a.categories) & set(b.categories)), a.probability * b.probability)
                if m not in accumulated:
                    accumulated.append(m)
                else:
                    for measure in accumulated:
                        if measure == m:
                            measure.probability += m.probability
        return accumulated

    def __correct(self, collection: list, correction: float):
        """
        Correct all measure's probability within a collection by a given float value
        
        Args:
            collection (list): List of measures to correct.
            correction (float): Correction factor.
        """
        for measure in collection:
            if measure.categories == []:
                measure.probability = 0
            else:
                measure.probability *= correction

    def __check_correction(self, collection: list) -> float or None:
        """
        Calculate correction for given collection of measures
        
        Args:
            collection (list): List of measures.

        Returns:
            float: Correction factor.
        """
        correction = None
        for measure in collection:
            if measure.categories == []:
                correction = 1 / (1 - measure.probability)
        return correction

    def print(self, measures: list):
        """
        Pretty print all measures.

        Args:
            measures (list): List of measures to print.
        """
        if len(measures) > 0 and (type(measures[0]) is not list):
            measures = [measures]
        print(self.__stingify(measures))

    def plausibility(self, accumulated: list, x: list or str):
        """
        Call correct method to calculate plausibility of single or several measures
        
        Args:
            accumulated (list): List of accumulated measures.
            x (list or str): Key(s) for plausibility calculation.

        Returns:
            float: Plausibility.
        """
        if type(x) is list:
            return self.__plausibility_multi(accumulated, x)
        else:
            return self.__plausibility_single(accumulated, x)

    def __plausibility_single(self, accumulated: list, key: str):
        """
        Calculate plausibility of single measure
        
        Args:
            accumulated (list): List of accumulated measures.
            x (str): Key for plausibility calculation.

        Returns:
            float: Plausibility.
        """
        plausibility = 0
        for measure in accumulated:
            if key in measure.categories:
                plausibility += measure.probability
        return plausibility

    def __plausibility_multi(self, accumulated: list, collection: list):
        """
        Calculate plausibility of multiple measures.
        
        Args:
            accumulated (list): List of accumulated measures.
            x (list): Keys for plausibility calculation.

        Returns:
            float: Plausibility.
        """
        plausibility = 0
        collection = set(collection)
        for measure in accumulated:
            if len(collection & set(measure.categories)) > 0:
                plausibility += measure.probability
        return plausibility
    
    def belief(self, accumulated: list, x: list or str):
        """
        Call correct method to calculate belief of single or multiple measures
        
        Args:
            accumulated (list): List of accumulated measures.
            x (list or str): Key for belief calculation.

        Returns:
            float: Belief.
        """
        if type(x) is list:
            return self.__belief_multi(accumulated, x)
        else:
            return self.__belief_single(accumulated, x)

    def __belief_single(self, accumulated: list, key: str):
        """
        Calculate belief of single measure
        
        Args:
            accumulated (list): List of accumulated measures.
            x (str): Key for belief calculation.

        Returns:
            float: Belief.
        """
        for measure in accumulated:
            if [key] == measure.categories:
                return measure.probability
        return 0
    
    def __belief_multi(self, accumulated: list, collection: list):
        """
        Calculate belief of multiple measures
        
        Args:
            accumulated (list): List of accumulated measures.
            x (list): Keys for belief calculation.

        Returns:
            float: Belief.
        """
        belief = 0
        for key in collection:
            belief += self.__belief_single(accumulated, key)
        return belief

    def doubt(self, accumulated: list, key: str):
        """
        Calculate doubt
        
        Args:
            accumulated (list): List of accumulated measures.
            x (str): Key for doubt calculation.

        Returns:
            float: Doubt.
        """
        return 1 - self.__plausibility_single(accumulated, key)

    def __stingify(self, measures: list):
        """
        Stringify measures.

        Args:
            measures (list): List of measures.

        Returns:
            str: String representation of measures.
        """
        ret = "--------------------------------\n"
        for measure_coll in measures:
            ret += "++\n"
            for measure in measure_coll:
                ret += str(measure) + "\n"
            ret += "++\n\n"
        ret += "-------------------------------- \n\n"
        return ret
    
    def clear(self):
        """
        Clear.
        """
        self.all_measures = []

    def __str__(self):
        """
        Stringify.

        Returns:
            str: String representation of this.
        """
        return self.__stingify(self.all_measures)
        
        
