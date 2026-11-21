"""Research-only released-anchor equivalence; no adoption or scoring side effects.

Max-t controls all arm/component contrasts WITHIN one released model. Bonferroni
controls the five correlated leave-one-anchor-out models without inventing their
cross-model covariance. FWER is at most alpha, not an independence approximation.
"""
import math
import random


def cholesky(matrix):
    n = len(matrix)
    if not n or any(len(row) != n for row in matrix):
        raise ValueError('INVALID_COVARIANCE')
    lower = [[0.] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            x, y = matrix[i][j], matrix[j][i]
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not math.isclose(x, y, rel_tol=1e-8, abs_tol=1e-12):
                raise ValueError('INVALID_COVARIANCE')
        for j in range(i + 1):
            residual = matrix[i][j] - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if residual <= 0:
                    raise ValueError('INVALID_COVARIANCE')
                lower[i][j] = math.sqrt(residual)
            else:
                lower[i][j] = residual / lower[j][j]
    return lower


def transformed_contrasts(values, mapping, reference, arms):
    """Return contrasts and analytic Jacobian in the full free-parameter order.

    mapping[arm] contains a zero-based index for a and cumulative d1,...,dm.
    mirt's fixed d0=0 is not an estimated intercept. Constraints may reuse an
    index, hence derivatives are accumulated, never assigned independently.
    """
    size = len(values)
    if reference not in mapping or len(set(arms)) != len(arms) or reference in arms or not arms:
        raise ValueError('INVALID_PARAMETER_MAPPING')

    def item(arm):
        pin = mapping[arm]
        indexes = [pin['a']] + pin['intercepts']
        if not pin['intercepts'] or any(isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= size for i in indexes):
            raise ValueError('INVALID_PARAMETER_MAPPING')
        a = values[pin['a']]
        if a <= 0 or not all(math.isfinite(values[i]) for i in indexes):
            raise ValueError('INVALID_PARAMETERS')
        log_gradient = [0.] * size
        log_gradient[pin['a']] = 1 / a
        output = [('LOG_A', math.log(a), log_gradient)]
        previous = None
        for k, index in enumerate(pin['intercepts']):
            difference = values[index] - (values[previous] if previous is not None else 0.)
            gradient = [0.] * size
            gradient[pin['a']] += difference / a ** 2
            gradient[index] -= 1 / a
            if previous is not None:
                gradient[previous] += 1 / a
            output.append((f'STEP_{k + 1}', -difference / a, gradient))
            previous = index
        return output

    base = item(reference)
    rows, jacobian = [], []
    for arm in arms:
        target = item(arm)
        if len(base) != len(target):
            raise ValueError('INVALID_PARAMETER_MAPPING')
        for (name, value, gradient), (_, base_value, base_gradient) in zip(target, base):
            rows.append({'armId': arm, 'metric': name, 'estimate': value - base_value})
            jacobian.append([x - y for x, y in zip(gradient, base_gradient)])
    return rows, jacobian


def intervals(block, reference, arms, profile, anchor_index):
    if block.get('converged') is not True or block.get('atParameterBoundary') is not False:
        raise ValueError('RELEASE_MODEL_UNAVAILABLE')
    values, covariance = block['values'], block['covariance']
    if len(covariance) != len(values):
        raise ValueError('INVALID_COVARIANCE')
    lower = cholesky(covariance)
    rows, jacobian = transformed_contrasts(values, block['mapping'], reference, arms)
    # J*L retains cross-arm and cross-component covariance, including nuisance
    # covariance in the identified released model. Never sum marginal SEs.
    projected = [[sum(g[k] * lower[k][j] for k in range(j, len(values))) for j in range(len(values))] for g in jacobian]
    errors = [math.sqrt(sum(x * x for x in row)) for row in projected]
    if any(not math.isfinite(x) or x <= 0 for x in errors):
        raise ValueError('INVALID_CONTRAST_VARIANCE')
    # Draw from the projected covariance using the original factor: it may be
    # positive semidefinite (shared contrasts), unlike the free-model covariance.
    standardized = [[v / error for v in row] for row, error in zip(projected, errors)]
    active = [j for j in range(len(values)) if any(row[j] != 0 for row in standardized)]
    rng = random.Random(profile['anchor']['drawSeed'] + anchor_index)
    maxima = []
    for _ in range(profile['anchor']['draws']):
        normal = [rng.gauss(0., 1.) for _ in active]
        maxima.append(max(abs(sum(row[j] * z for j, z in zip(active, normal))) for row in standardized))
    maxima.sort()
    alpha = 1 - profile['anchor']['intervalLevel']
    quantile = 1 - alpha / profile['anchor']['count']
    # Conservative order statistic, no interpolation toward a smaller critical value.
    critical = maxima[min(len(maxima) - 1, math.ceil(quantile * (len(maxima) + 1)) - 1)]
    for row, error in zip(rows, errors):
        margin = profile['quality']['anchorLogSlopeTolerance'] if row['metric'] == 'LOG_A' else profile['quality']['anchorDifficultyTolerance']
        lo, hi = row['estimate'] - critical * error, row['estimate'] + critical * error
        decision = 'EQUIVALENT' if lo >= -margin and hi <= margin else 'MATERIAL_DIFFERENCE' if lo > margin or hi < -margin else 'INSUFFICIENT'
        row.update(standardError=error, lower=lo, upper=hi, margin=margin, decision=decision)
    decision = 'MATERIAL_DIFFERENCE' if any(r['decision'] == 'MATERIAL_DIFFERENCE' for r in rows) else 'EQUIVALENT' if all(r['decision'] == 'EQUIVALENT' for r in rows) else 'INSUFFICIENT'
    return {'decision': decision, 'criticalValue': critical, 'draws': len(maxima), 'blockLevel': quantile, 'contrasts': rows}


def evaluate(scientific, expected, reference, arms, profile):
    """Fail closed, including incomplete anchor evidence; never scores anyone."""
    output = {'purpose': 'RESEARCH_ONLY', 'policyVersion': profile['version'], 'passed': False,
              'decision': 'NOT_EVALUATED', 'scope': 'ALL_FITTED_ARMS', 'checks': {}}
    releases = scientific.get('released', {})
    if len(expected) != profile['anchor']['count'] or len(set(expected)) != len(expected) or set(releases) != set(expected):
        output['reason'] = 'ANCHOR_IDENTITY_MISMATCH'
        return output
    if scientific.get('converged') is not True or scientific.get('atParameterBoundary') is not False:
        output['reason'] = 'JOINT_MODEL_UNAVAILABLE'
        return output
    try:
        cholesky(scientific['joint']['covariance'])
    except (ValueError, KeyError, TypeError):
        output['reason'] = 'JOINT_COVARIANCE_UNAVAILABLE'
        return output
    for i, qid in enumerate(expected):
        try:
            check = intervals(releases[qid], reference, arms, profile, i)
        except (ValueError, KeyError, TypeError, IndexError, OverflowError) as error:
            reason = str(error) if isinstance(error, ValueError) else 'MISSING_RELEASE_DIAGNOSTICS'
            check = {'decision': 'NOT_EVALUATED', 'reason': reason, 'contrasts': []}
        output['checks'][qid] = check
    decisions = [x['decision'] for x in output['checks'].values()]
    output['decision'] = 'NOT_EVALUATED' if 'NOT_EVALUATED' in decisions else 'MATERIAL_DIFFERENCE' if 'MATERIAL_DIFFERENCE' in decisions else 'EQUIVALENT' if all(x == 'EQUIVALENT' for x in decisions) else 'INSUFFICIENT'
    output['passed'] = output['decision'] == 'EQUIVALENT'
    return output
