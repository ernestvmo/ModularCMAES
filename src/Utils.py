from datetime import datetime
from functools import wraps
from time import time
import numpy as np

from bbob import bbobbenchmarks, fgeneric
from Constants import DEFAULT_TARGET_DISTANCES, DISTANCE_TO_TARGET


def timeit(func):
    @wraps(func)
    def inner(*args, **kwargs):
        start = time()
        res = func(*args, **kwargs)
        print("Time elapsed", time() - start)
        return res
    return inner


def ert(evals, budget):
    try:
        _ert = evals.sum() / (evals < budget).sum()
    except:
        _ert = float('inf')
    return _ert, np.std(evals)


def bbobfunction(ffid, logging=False, label='', iinstance=1, d=5):
    func, target = bbobbenchmarks.instantiate(
        ffid, iinstance=iinstance)
    if not logging:
        return func, target
    label = 'D{}_{}_{}'.format(
        d, label, datetime.now().strftime("%m%d"))
    fitness_func = fgeneric.LoggingFunction(
        "/home/jacob/Code/thesis/data/{}".format(label), label)
    target = fitness_func.setfun(
        *(func, target)
    ).ftarget
    return fitness_func, target


@timeit
def evaluate(ffid, d, optimizer_class, *args, iterations=50, label='', logging=False, all_funcs=False, **kwargs):
    evals, fopts = np.array([]), np.array([])
    _, target = bbobfunction(ffid)
    print("Optimizing function {} in {}D for target {} + {}".format(ffid, d, target,
                                                                    DISTANCE_TO_TARGET[ffid - 1]))
    if logging:
        label = 'D{}_{}_{}'.format(
            d, label, datetime.now().strftime("%m"))
        fitness_func = fgeneric.LoggingFunction(
            "/home/jacob/Code/thesis/data/{}".format(label), label)
    for i in range(iterations):
        func, target = bbobbenchmarks.instantiate(ffid, iinstance=1)
        if not logging:
            fitness_func = func
        else:
            target = fitness_func.setfun(
                *(func, target)
            ).ftarget
        optimizer = optimizer_class(fitness_func, target, d, *args,
                                    rtol=DISTANCE_TO_TARGET[ffid - 1],
                                    ** kwargs)
        optimizer.run()
        evals = np.append(evals, optimizer.parameters.used_budget)
        fopts = np.append(fopts, optimizer.parameters.fopt)

    print("FCE:\t{:10.8f}\t{:10.4f}\nERT:\t{:10.4f}\t{:10.4f}".format(
        np.mean(fopts), np.std(fopts), *ert(evals, optimizer.parameters.budget)
    ))
    return evals, fopts


def plot_cumulative_target(fitness_over_time, abs_target, label=None, log=False):
    # Don't include the points that have hit a target and than decrease.
    fitness_over_time = to_matrix(fitness_over_time)
    bins = np.digitize(fitness_over_time - abs_target,
                       DEFAULT_TARGET_DISTANCES, right=True)

    bins = np.maximum.accumulate(bins, axis=1)
    line = [i.sum() / (len(DEFAULT_TARGET_DISTANCES) * len(i)) for i in bins.T]
    plt.semilogx(line, label=label)
    plt.ylabel("Proportion of function+target pairs")
    plt.xlabel("Function Evaluations")
    plt.legend()


def to_matrix(array):
    max_ = len(max(array, key=len))
    return np.array([
        row + [row[-1]] * (max_ - len(row)) for row in array])


class Descriptor:
    def __init__(self, name=''):
        self.name = name

    def __get__(self, instance, instance_type):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class NoneTypeDescriptor(Descriptor):
    def __get__(self, instance, instance_type):
        return instance.__dict__.get(self.name)


class Boolean(NoneTypeDescriptor):
    def __get__(self, instance, instance_type):
        return super().__get__(instance, instance_type) or False

    def __set__(self, instance, value):
        if type(value) != bool:
            raise TypeError("{} should be bool".format(self.name))
        super().__set__(instance, value)


class NpArray(Descriptor):
    def __set__(self, instance, value):
        if type(value) != np.ndarray:
            raise TypeError("{} should be numpy.ndarray".format(self.name))
        instance.__dict__[self.name] = value.copy()


class AnyOf(NoneTypeDescriptor):
    def __init__(self, name='', options=None):
        self.name = name
        self.options = options

    def __set__(self, instance, value):
        if value not in self.options:
            raise TypeError("{} should any of {}".format(
                self.name, self.options
            ))
        super().__set__(instance, value)


class InstanceOf(NoneTypeDescriptor):
    def __init__(self, name='', iclass=None):
        self.name = name
        self.iclass = iclass

    def __set__(self, instance, value):
        if not isinstance(value, self.iclass):
            raise TypeError("Value should be of type {}".format(
                self.iclass))
        super().__set__(instance, value)
