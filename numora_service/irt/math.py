"""Independent D=1 probability, posterior and reference-score calculations."""
from decimal import Decimal, ROUND_HALF_UP
import math


def probabilities(theta, a, steps):
    if not math.isfinite(theta) or not math.isfinite(a) or a <= 0 or not steps:
        raise ValueError('INVALID_PARAMETERS')
    logits = [0.0]
    for step in steps:
        if not math.isfinite(step):
            raise ValueError('INVALID_PARAMETERS')
        logits.append(logits[-1] + a * (theta - step))
    peak = max(logits)
    values = [math.exp(x - peak) for x in logits]
    total = sum(values)
    return [p / total for p in values]


def posterior_grid(parameters,points=1201):
    grid=[-8+16*i/(points-1) for i in range(points)]
    tables={qid:[[math.log(max(p,1e-300)) for p in probabilities(t,a,steps)] for t in grid]
            for qid,(a,steps) in parameters.items()}
    return grid,tables


def eap(observations, parameters, points=1201,prepared=None):
    # Independent trapezoid integration, common N(0,1), not group-specific priors.
    if not observations:
        raise ValueError('NO_OBSERVATIONS')
    grid,tables=prepared if prepared is not None else posterior_grid(parameters,points)
    points=len(grid)
    logs = []
    for i, theta in enumerate(grid):
        value = -theta * theta / 2
        if i in (0, points - 1):
            value += math.log(0.5)
        for qid, category in observations:
            value += tables[qid][i][category]
        logs.append(value)
    peak = max(logs)
    weights = [math.exp(x - peak) for x in logs]
    total = sum(weights)
    mean = sum(w * t for w, t in zip(weights, grid)) / total
    variance = sum(w * (t - mean)**2 for w, t in zip(weights, grid)) / total
    return mean, math.sqrt(variance)


def reference_score(theta, items, parameters):
    maximum = sum(Decimal(i['maxPoints']) for i in items)
    if maximum <= 0:
        raise ValueError('NO_VALID_ITEMS')
    predicted = Decimal(0)
    for item in items:
        a, steps = parameters[item['questionVersionId']]
        p = probabilities(theta, a, steps)
        expected = sum(k * v for k, v in enumerate(p))
        predicted += Decimal(str(expected)) / Decimal(item['maximumScoreCategory']) * Decimal(item['maxPoints'])
    return float((100 * predicted / maximum).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def convert(a, intercepts, covariance):
    """mirt cumulative category intercepts -> absolute thresholds, full delta method.

    covariance order is [a,d1,...,dm]; d0=0 is fixed. No ordered-step assumption.
    """
    if a <= 0 or len(covariance) != len(intercepts) + 1:
        raise ValueError('INVALID_PARAMETERS')
    previous = 0.0
    values, errors = [], []
    for i, value in enumerate(intercepts):
        difference = value - previous
        gradient = [0.0] * (len(intercepts) + 1)
        gradient[0] = difference / (a*a)
        gradient[i+1] = -1/a
        if i:
            gradient[i] = 1/a
        variance = sum(x * covariance[j][k] * y for j,x in enumerate(gradient)
                       for k,y in enumerate(gradient))
        if variance < -1e-10 or not math.isfinite(variance):
            raise ValueError('INVALID_COVARIANCE')
        values.append(-difference/a)
        errors.append(math.sqrt(max(0, variance)))
        previous = value
    return values, errors
