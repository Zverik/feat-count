#!/bin/bash
set -u -e

usage() {
  echo "This script calculates statistics for a given MWM file."
  echo "It requires a configuration file for classificator types."
  echo
  echo "Usage: $0 [--csv] <config.txt> <file.mwm> [<file2.mwm> ...] [ x [<threshold>] <new.mwm> [<new2.mwm> ...] ]"
  echo
  echo "Threshold is for printing values in percents, default is 1, must be integer"
  exit 1
}

[ $# -lt 2 ] && usage

if [ $# -gt 0 -a ( "$1" == "--csv" -o "$1" == "--csvh" ) ]; then
  CSV=--csv
  if [ "$1" == "--csvh" ]; then
    echo "sep=;"
    echo "Критерий;Было;Стало;Ед.;Разница;Ед.;В процентах"
  fi
  shift
  [ $# -lt 2 ] && usage
fi

CONFIG="$1"
shift
FORMAT_PY="$(dirname "$0")/format_stat.py"
SUM_PY="$(dirname "$0")/sum_stat.py"
THRESHOLD=1
[ ! -f "$FORMAT_PY" ] && echo "Cannot find $FORMAT_PY" && exit 1
export OMIM_PATH="${OMIM_PATH:-$(cd "$(dirname "$0")/../omim"; pwd)}"
source "$OMIM_PATH/tools/unix/find_generator_tool.sh" 1>&2

if [ "$(uname)" == "Darwin" ]; then
  INTDIR=$(mktemp -d -t calcstat)
else
  INTDIR=$(mktemp -d)
fi
trap "rm -rf \"${INTDIR}\"" EXIT SIGINT SIGTERM

TARGET="$INTDIR/old"
TMP="$INTDIR/tmp"

while [ $# -gt 0 ]; do
  if [ "$1" == "x" ]; then
    TARGET="$INTDIR/new"
    if [ $# -gt 1 -a -n "${2##*[!0-9.]*}" ]; then
      THRESHOLD=$2
      shift
    fi
  elif [[ $1 == *.mwm ]]; then
    SOURCE_PATH="$(dirname "$1")"
    SOURCE_NAME="$(basename "$1" .mwm)"
    [ ! -f "$SOURCE_PATH/$SOURCE_NAME.mwm" ] && fail "Cannot find $SOURCE_PATH/$SOURCE_NAME.mwm" && exit 2
    "$GENERATOR_TOOL" --data_path="$SOURCE_PATH" --user_resource_path="$OMIM_PATH/data/" --calc_statistics --output="$SOURCE_NAME" > "$TMP" 2>&1
    if [ -e "$TARGET" ]; then
      python "$SUM_PY" "$TARGET" "$TMP" > "$TARGET.2"
      mv "$TARGET.2" "$TARGET"
      rm "$TMP"
    else
      mv "$TMP" "$TARGET"
    fi
  fi
  shift
done

if [ -e "$INTDIR/new" ]; then
  python "$FORMAT_PY" ${CSV-} "$CONFIG" "$INTDIR/old" "$INTDIR/new" $THRESHOLD
else
  python "$FORMAT_PY" ${CSV-} "$CONFIG" "$INTDIR/old"
fi
