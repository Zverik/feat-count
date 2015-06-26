#!/bin/bash
set -u

if [ $# -lt 3 ]; then
  echo "Compare mwm files in two directories. Prints CSV."
  echo "Usage: $0 <config.txt> <dir_old> <dir_new> [threshold]"
  exit 1
fi

THRESHOLD=0
[ $# -gt 3 ] && THRESHOLD=$4

echo "Критерий;Было;Стало;Ед.;Разница;Ед.;В процентах"
for old in "$2"/*.mwm; do
  BASE_NAME="$(basename "$old" .mwm)"
  if [ -f "$3/$BASE_NAME.mwm" ]; then
    echo
    echo "$BASE_NAME"
    bash calc_stat.sh --csv "$1" "$2/$BASE_NAME.mwm" x $THRESHOLD "$3/$BASE_NAME.mwm"
  fi
done
