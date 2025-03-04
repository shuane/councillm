#!/bin/bash

# Default values
N_MODELS=6
NO_LOGGING=false
EXTRA_ARGS=()

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -n)
      N_MODELS="$2"
      shift 2
      ;;
    --no-logging)
      NO_LOGGING=true
      shift
      ;;
    *)
      # Collect any other arguments to pass to the Python script
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

# Pass arguments to the Python script
if [ "$NO_LOGGING" = true ]; then
  uv run --isolated --no-project --with-requirements councillm/cl_requirements.txt councillm/app.py -n "$N_MODELS" --no-logging "${EXTRA_ARGS[@]}"
else
  uv run --isolated --no-project --with-requirements councillm/cl_requirements.txt councillm/app.py -n "$N_MODELS" "${EXTRA_ARGS[@]}"
fi
