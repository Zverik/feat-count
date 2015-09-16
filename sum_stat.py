#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, re

RE_STAT = re.compile(r'(?:\d+\. )?([\w:|-]+?)\|: size = \d+; count = (\d+); length = ([0-9.e+-]+) m; area = ([0-9.e+-]+) m²\s*')

if len(sys.argv) < 3:
  print "Usage: {0} <first> <second> [etc etc]".format(sys.argv[0])
  sys.exit(1)

result = {}
order = []
with open(sys.argv[1], 'r') as f:
  for line in f:
    m = RE_STAT.match(line)
    if m:
      k = m.group(1)
      order.append(k)
      result[k] = [int(m.group(2)), float(m.group(3)), float(m.group(4))]

for i in range(2, len(sys.argv)):
  with open(sys.argv[i], 'r') as f:
    for line in f:
      m = RE_STAT.match(line)
      if m:
        k = m.group(1)
        if not k in result:
          order.append(k)
          result[k] = [0, 0.0, 0.0]
        result[k][0] += int(m.group(2))
        result[k][1] += float(m.group(3))
        result[k][2] += float(m.group(4))

for k in order:
  print "{0}|: size = 0; count = {1}; length = {2} m; area = {3} m²".format(k, result[k][0], result[k][1], result[k][2])
