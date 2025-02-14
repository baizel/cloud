#!/usr/bin/env python3.7
from enum import Enum
from types import FunctionType

import math
import random
import threading
import time
import requests
import argparse

normalDistributionData = {}
poissonDistributionData = {}


class Distribution(Enum):
    Poisson = "poisson"
    Normal = "normal"

    def __str__(self):
        return self.value


def callToUrl(url):
    res = requests.get(url)
    print(str(res.content))


def getPoissonDistribution(lamb: float, numberOfEvents: float) -> float:
    lambK = math.pow(lamb, numberOfEvents)
    kFact = math.factorial(numberOfEvents)
    eMinusLamb = math.pow(math.e, -1 * numberOfEvents)
    return (lambK * eMinusLamb) / kFact


def getRandomPoisson(lamb: float, sampleSize: int):
    if poissonDistributionData.get((lamb, sampleSize), None) is None:
        population = []
        weights = []
        for i in range(0, int(sampleSize)):
            population.append(i)
            weights.append(getPoissonDistribution(lamb, i))

        poissonDistributionData[(lamb, sampleSize)] = (population, weights)
        return random.choices(population, weights)[0]
    population, weights = poissonDistributionData.get((lamb, sampleSize))
    return random.choices(population, weights)[0]


def getNormalDistribution(mean: float, stdev: float, x: int) -> float:
    denom = stdev * math.sqrt(2 * math.pi)
    fraction = 1 / denom
    power = (-1 * math.pow((x - mean), 2)) / (2 * math.pow(stdev, 2))
    e = math.pow(math.e, power)
    return fraction * e


def getRandomNormal(mean: float, stdev: float) -> float:
    if normalDistributionData.get((mean, stdev), None) is None:
        population = []
        weights = []
        for i in range(1, int(mean * 2) + 1):
            population.append(i)  # in ms
            weights.append(getNormalDistribution(mean, stdev, i))

        normalDistributionData[(mean, stdev)] = (population, weights)
        return random.choices(population, weights)[0]

    population, weights = normalDistributionData.get((mean, stdev))
    return random.choices(population, weights)[0]


def createLoad(url: str, randomGenerator: FunctionType, genArgs: tuple, numberOfIterations, isVerbose: bool) -> None:
    intervals = []
    for i in range(0, numberOfIterations):
        print("Executing HTTP GET to URL " + url)
        threading.Thread(target=callToUrl, args=(url,)).start()
        interval = randomGenerator(*genArgs)
        intervals.append(interval)
        print("Sleeping for " + str(interval) + "ms")
        time.sleep(interval / 1000)  # ms to seconds

    if isVerbose:
        for key in normalDistributionData.keys():
            mean, stdev = key
            population, distribution = normalDistributionData[key]
            for count, dist in enumerate(distribution):
                print("{},{}".format(population[count], dist))
            print(stdev, mean)
        for key in poissonDistributionData.keys():
            lamb, sampleSize = key
            population, distribution = poissonDistributionData[key]
            for count, dist in enumerate(distribution):
                print("{},{:.2e}".format(population[count], dist))
        [print("{},{}".format(count, val)) for count, val in enumerate(intervals)]


if __name__ == "__main__":

    choicesOfDistribution = [i.value for i in Distribution]

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", "-u", type=str, help="Url of the target to load test on", required=True)
    parser.add_argument("--dist", "-d", type=Distribution, help="Distribution, choose one of {}".format(choicesOfDistribution), choices=list(Distribution), required=True)
    parser.add_argument("--iter", "-i", type=int, help="Number of iteration to call the url before the program terminates}", required=True)

    parser.add_argument("--mean", "-m", type=float, help="Mean for the normal distribution in milliseconds")
    parser.add_argument("--stdev", "-s", type=float, help="Standard deviation for the normal distribution in milliseconds")
    parser.add_argument("--lamb", "-l", type=float, help="Lambda for Poisson distribution")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable for verbose output of distribution and values")

    args = parser.parse_args()

    generator = None
    generatorArgs = ()

    if Distribution(args.dist) == Distribution.Normal:
        if args.stdev is None or args.mean is None:
            raise ValueError("Mean or Standard deviation value missing")
        generator = getRandomNormal
        generatorArgs = (args.mean, args.stdev)

    elif Distribution(args.dist) == Distribution.Poisson:
        if args.lamb is None:
            raise ValueError("Lambda value missing")
        generator = getRandomPoisson
        generatorArgs = (args.lamb, args.iter)

    createLoad(args.url, generator, generatorArgs, args.iter, args.verbose)
