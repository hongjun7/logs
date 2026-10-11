#!/usr/bin/env python3
"""Recompute the articles' numerical examples and finite probability identities."""
from fractions import Fraction as F
from itertools import permutations
from math import exp, isclose, log

# Characteristic sets: average products need not equal product of averages.
assert sum(a*b for a,b in [(1,1),(3,3)]) == 10
assert 2 * ((1+3)/2) * ((1+3)/2) == 8
assert sum(a*b for a,b in [(1,3),(3,1)]) == 6
triples = [(1,1,1),(1,2,2),(2,1,2),(2,2,1)]
assert sum(a*b*c for a,b,c in triples) == 13
assert 4*F(3,2)**3 == F(27,2)
for i,j in [(0,1),(0,2),(1,2)]:
    assert sum(F(row[i])*row[j] for row in triples)/4 == F(9,4)

# WanderJoin: one path of weight 2, three paths of weight 6.
paths = [(F(1,2),2)] + [(F(1,6),6)] * 3
mean = sum(prob*weight for prob,weight in paths)
assert mean == 4
assert sum(prob*(weight-mean)**2 for prob,weight in paths) == 4
assert F(100,101)*F(101,100)+F(1,101)*101 == 2
# Choose two of three elements uniformly: HT count is always three.
inclusion = F(2,3)
ht_variance = sum(((inclusion if a==b else F(1,3))-inclusion**2)/inclusion**2 for a in range(3) for b in range(3))
assert ht_variance == 0

# PWIL: fractional masses sum correctly; greedy matching can be suboptimal.
assert F(1,3)+F(1,6) == F(1,2)
agent, expert = [0,3], [1,-4]
costs = [sum(abs(agent[i]-match[i]) for i in range(2))/2 for match in permutations(expert)]
assert costs == [4,3]
assert isclose(1+exp(-2)-2*exp(-1), (1-exp(-1))**2)

# BlockRank: stated full-block pair convention, not a timing estimate.
p,q,n,length = 32,32,100,128
assert (p+q+n*length)**2 == 165482496
assert p*p+n*(length*length+p*length)+q*(p+q+n*length) == 2460672

# Amdahl: preserve the unaffected component.
assert isclose(1/(.8+.2/5), 1.1904761904761905)
assert 1/.8 == 1.25

# Graph decision example: exhaustive four-cycle cut confirms the upper bound.
edges = [(0,1),(1,2),(2,3),(3,0)]
cuts = [sum(((bits>>u)&1) != ((bits>>v)&1) for u,v in edges) for bits in range(16)]
assert max(cuts) == 4
# Nested-learning conflict example at the old optimum.
eta = F(1,10)
theta_new = 1-2*eta
assert F(1,2)*(theta_new-1)**2 == 2*eta**2

# Proper scoring identities: enumerate all true labels independently.
pred,truth = [.6,.3,.1],[.1,.2,.7]
expected_brier = sum(truth[y]*sum((pred[k]-int(k==y))**2 for k in range(3)) for y in range(3))
identity = sum((pred[k]-truth[k])**2 for k in range(3))+1-sum(q*q for q in truth)
assert isclose(expected_brier,identity)
entropy = -sum(q*log(q) for q in truth)
kl = sum(q*log(q/p) for q,p in zip(truth,pred))
assert isclose(-sum(q*log(p) for q,p in zip(truth,pred)),entropy+kl)
assert isclose(sum(x*x for x in [.6,.4]),.52)

# Jev's summaries and probability thresholds.
assert isclose((.6-1/3)/(1-1/3),.4)
assert isclose(1-.43/(2/3),.355)
assert isclose(.57+2*.43,1.43)
assert isclose(1/3+.9*(1-1/3),14/15)
assert isclose((.9-1/3)/(1-1/3),.85)
assert isclose(1-.05**(1/100),.029513049607039932)
for levels in range(2,30):
    direct = sum(abs(i-(levels-1)/2) for i in range(levels))/levels
    closed = levels/4 if levels%2==0 else (levels*levels-1)/(4*levels)
    assert isclose(direct,closed)

print('Verified: characteristic-set counterexamples, sampling expectation/variance,')
print('PWIL mass/cost example, BlockRank pair counts, Amdahl bounds, proper-score')
print('identities, confidence/threshold examples, and exact binomial upper limit.')
