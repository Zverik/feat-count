#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, re

RE_STAT = re.compile(r'(?:\d+\. )?([\w:|-]+?)\|: size = \d+; count = (\d+); length = ([0-9.e+-]+) m; area = ([0-9.e+-]+) m²\s*')

def read_stat(f):
  stats = []
  for line in f:
    m = RE_STAT.match(line)
    if m:
      stats.append({ "name": m.group(1).replace('|', '-'), "cnt": int(m.group(2)), "len": float(m.group(3)), "area": float(m.group(4)) })
  return stats

def read_config(f):
  config = []
  for line in f:
    columns = [c.strip() for c in line.split(';', 2)]
    if len(columns) == 3 and len(columns[0]) > 1:
      columns[0] = re.compile(columns[0])
      columns[1] = columns[1].lower()
      config.append(columns)
  return config

def process_stat(config, stats):
  result = {}
  for param in config:
    res = 0
    for typ in stats:
      if param[0].match(typ['name']):
        if param[1] == 'len':
          res += typ['len']
        elif param[1] == 'area':
          res += typ['area']
        else:
          res += typ['cnt']
    result[param[0]] = res
  return result

def format_res(res, typ):
  if typ == 'len':
    if abs(res) < 1:
      res *= 100
      unit = 'см'
    elif abs(res) < 1000:
      unit = 'м'
    elif abs(res) < 1000000:
      res /= 1000
      unit = 'км'
    else:
      res /= 1000000
      unit = 'тыс. км'
    if res != 0:
      res = '{0:.2f}'.format(res)
  elif typ == 'area':
    if abs(res) < 10000:
      unit = 'м²'
    elif abs(res) < 1000000000:
      res /= 1000000
      unit = 'км²'
    else:
      res /= 1000000000
      unit = 'тыс. км²'
    if res != 0:
      res = '{0:.2f}'.format(res)
  else:
    unit = 'шт.'
  return (res, unit)

if len(sys.argv) > 1 and sys.argv[1] == '--csv':
  csv = True
  del sys.argv[1]
else:
  csv = False

if len(sys.argv) <= 2:
  print "Usage: {0} [--csv] <config.txt> <stats.txt> [new_stats.txt] [threshold]".format(sys.argv[0])
  sys.exit(1)

with open(sys.argv[1], 'r') as f:
  config = read_config(f)
with open(sys.argv[2], 'r') as f:
  stats = process_stat(config, read_stat(f))
if len(sys.argv) > 3:
  with open(sys.argv[3], 'r') as f:
    new_stats = process_stat(config, read_stat(f))
  threshold = 0 if len(sys.argv) <= 4 else int(sys.argv[4])
else:
  threshold = -1

for param in config:
  st = format_res(stats[param[0]], param[1])
  if threshold < 0:
    if st[0] > 0.0:
      if csv:
        #print ';'.join([str(c) for c in (param[2], stats[param[0]], param[1])])
        print ';'.join([str(c) for c in (param[2], st[0], st[1])])
      else:
        print "{0}: {1} {2}".format(param[2], st[0], st[1])
  else:
    nst = format_res(new_stats[param[0]], param[1])
    diff = format_res(new_stats[param[0]] - stats[param[0]], param[1])
    percent = 0 if stats[param[0]] <= 0 else (new_stats[param[0]] - stats[param[0]]) * 100.0 / stats[param[0]]
    if abs(percent) >= threshold:
      if csv:
        print ';'.join([str(c) for c in (param[2], st[0], nst[0], st[1], diff[0], diff[1], percent / 100)])
        #print ';'.join([str(c) for c in (param[2], stats[param[0]], new_stats[param[0]], param[1], new_stats[param[0]] - stats[param[0]], percent)])
      else:
        print "{0}: было {1} {2}, стало {3} {4} ({5}{6} {7}, {8:.1f}%)".format(param[2], st[0], st[1], nst[0], nst[1], '+' if float(diff[0]) > 0 else '', diff[0], diff[1], percent)
