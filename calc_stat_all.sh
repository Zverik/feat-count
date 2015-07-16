#!/bin/bash
set -u

if [ $# -lt 3 ]; then
  echo "Compare mwm files in two directories. Prints CSV."
  echo "Usage: $0 <config.txt> <dir_old> <dir_new> [threshold]"
  exit 1
fi

THRESHOLD=0
[ $# -gt 3 ] && THRESHOLD=$4

HEAD=h
for old in "$2"/*.mwm; do
  BASE_NAME="$(basename "$old" .mwm)"
  if [ -f "$3/$BASE_NAME.mwm" ]; then
    echo
    echo "$BASE_NAME"
    bash "$(dirname "$0")/calc_stat.sh" --csv$HEAD "$1" "$2/$BASE_NAME.mwm" x $THRESHOLD "$3/$BASE_NAME.mwm"
    HEAD=
  fi
done
