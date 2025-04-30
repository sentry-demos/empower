#!/bin/bash

# envsubst on steroids

strict_mode=0
strict_allow_empty_mode=0
list_mode=0
script_mode=0
ignore_prefix=""
from_file=""
passed_flags=()
# Track variables defined in stdin for script mode (using space-separated string for compatibility)
script_defined_vars=""
# Track variables already output in list mode to prevent duplicates
list_output_vars=""

# Function to validate an argument is safe (no command injection)
validate_argument() {
  local arg="$1"
  local type="$2"
  # Check if argument contains any potentially dangerous characters
  if [[ "$arg" =~ [\|\&\;\(\)\<\>\"\'\$] ]]; then
    echo "[ERROR] Invalid characters in the value of '$type'" >&2
    exit 1
  fi
}

# Function to check if a variable has already been output in list mode
is_var_already_output() {
  local var_name="$1"
  [[ " $list_output_vars " =~ " $var_name " ]]
}

# Function to mark a variable as output in list mode
mark_var_as_output() {
  local var_name="$1"
  if ! is_var_already_output "$var_name"; then
    list_output_vars="$list_output_vars $var_name"
  fi
}

# Function to determine if a variable should be ignored during substitution
should_ignore() {
  local var_name="$1"
  
  # In script mode without list mode, completely ignore script-defined variables
  if [ "$script_mode" -eq 1 ] && [[ " $script_defined_vars " =~ " $var_name " ]]; then
    return 0  # true - should ignore
  fi
  
  # Check ignore prefix
  if [ -n "$ignore_prefix" ] && [[ "$var_name" == "$ignore_prefix"* ]]; then
    return 0  # true - should ignore
  fi
  
  return 1  # false - should not ignore
}

# Helper function to check if a variable is defined or list it
# Assumes we already checked if the variable should be ignored
check_var_defined_or_list() {
  local var_name="$1"

  if [ "$list_mode" -eq 1 ]; then
    if ! is_var_already_output "$var_name"; then
      echo "$var_name"
      mark_var_as_output "$var_name"
    fi
  elif [ "${!var_name+_}" != "_" ]; then
    # Variable is not defined
    if [ "$strict_mode" -eq 1 ] || [ "$strict_allow_empty_mode" -eq 1 ]; then
      echo "[ERROR] bin/envsubst.sh: Variable '$var_name' is not defined" >&2
      exit 1
    fi
  elif [ -z "${!var_name}" ] && [ "$strict_mode" -eq 1 ]; then
    # Variable is defined but empty
    echo "[ERROR] bin/envsubst.sh: Variable '$var_name' is empty" >&2
    exit 1
  fi
}

envsubst_() {
  local input="$1"
  # First, replace \$ with a unique placeholder that won't appear in normal text
  local placeholder=$'\x01ESCAPED_DOLLAR\x02'
  input="${input//\\\$/$placeholder}"

  local output=""
  local i=0
  local len=${#input}
  local in_var=0 # 0 = not in variable, 1 = in ${VAR} syntax, 2 = in $VAR syntax
  local var_name=""

  while [ "$i" -lt "$len" ]; do
    local char="${input:$i:1}"

    if [ "$in_var" -eq 1 ]; then
      if [[ "$char" =~ [a-zA-Z0-9_] ]]; then
        var_name="$var_name$char"
      elif [ "$char" = '}' ]; then
        if [ -n "$var_name" ]; then
          if should_ignore "$var_name"; then
            output="$output\${$var_name}" # output variable name's characters but not the value
          else
            check_var_defined_or_list "$var_name"
            output="$output${!var_name}" # in --list mode we still do this but discard the output later
          fi
          var_name=""
        fi
        in_var=0
      else
        output="$output\${$var_name}$char"
        var_name=""
        in_var=0
      fi
    elif [ "$char" = '$' ]; then
      local next_char="${input:$((i+1)):1}"
      if [ "$next_char" = '{' ]; then
        i=$((i+1))
        in_var=1
      elif [[ "$next_char" =~ [a-zA-Z_] ]]; then
        in_var=2
        var_name="$next_char"
        i=$((i+1))
      else
        output="$output$"
      fi
    elif [ "$in_var" -eq 2 ]; then
      if [[ "$char" =~ [a-zA-Z0-9_] ]]; then
        var_name="$var_name$char"
      else
        if should_ignore "$var_name"; then
          output="$output\${$var_name}$char"
        else
          check_var_defined_or_list "$var_name"
          output="$output${!var_name}$char"
        fi
        var_name=""
        in_var=0
      fi
    else
      output="$output$char"
    fi
    i=$((i+1))
  done

  if [ "$in_var" -eq 2 ]; then
    if should_ignore "$var_name"; then
      output="$output\${$var_name}"
    else
      check_var_defined_or_list "$var_name"
      output="$output${!var_name}"
    fi
  fi

  # Only print output if not in list mode
  if [ "$list_mode" -eq 0 ]; then
    # Convert the placeholder back to $ and print to stdout
    printf "%s\n" "${output//$placeholder/$}"
  fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict)
      strict_mode=1
      passed_flags+=("--strict")
      shift
      ;;
    --strict-allow-empty)
      strict_allow_empty_mode=1
      passed_flags+=("--strict-allow-empty")
      shift
      ;;
    --list)
      list_mode=1
      passed_flags+=("--list")
      shift
      ;;
    --script)
      script_mode=1
      passed_flags+=("--script")
      shift
      ;;
    --ignore-prefix=*)
      ignore_prefix="${1#*=}"
      validate_argument "$ignore_prefix" "--ignore-prefix"
      passed_flags+=("$1")
      shift
      ;;
    --from=*)
      from_file="${1#*=}"
      validate_argument "$from_file" "--from"
      # Don't add --from to passed_flags to prevent infinite recursion
      shift
      ;;
    *)
      echo "Usage: $0 [--strict | --strict-allow-empty | --list] [--script] [--ignore-prefix=<prefix>] [--from=<file>]" >&2
      exit 1
      ;;
  esac
done

# Validate options
if [ $((strict_mode + strict_allow_empty_mode + list_mode)) -gt 1 ]; then
  echo "[ERROR] Only one of --strict, --strict-allow-empty, or --list can be used" >&2
  exit 1
fi
if [ -n "$from_file" ] && [ "$list_mode" -eq 1 ]; then
  echo "[ERROR] --from=<file> and --list cannot be used together" >&2
  exit 1
fi

if [ -n "$SCRIPT_DEFINED_VARS" ]; then
  # Initialize script_defined_vars from environment if available (script called recursively from --from re-execution)
  script_defined_vars="$SCRIPT_DEFINED_VARS"
else
  script_defined_vars=""
  # For script mode, we need to process stdin twice:
  # First pass: collect variable assignments
  # Second pass: find template variables and filter out the assigned ones
  if [ "$script_mode" -eq 1 ]; then
    # Read stdin into a temporary file so we can process it twice
    temp_file=$(mktemp)
    trap 'rm -f "$temp_file"' EXIT
    
    # First pass: collect variable assignments from stdin
    while IFS= read -r line || [ -n "$line" ]; do
      echo "$line" >> "$temp_file"
      # Check if this line is a variable assignment
      if [[ "$line" =~ ^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*=[[:space:]]* ]]; then
        # Extract variable name
        var_name=$(echo "$line" | sed 's/^[[:space:]]*\([a-zA-Z_][a-zA-Z0-9_]*\)[[:space:]]*=.*/\1/')
        # Add to script_defined_vars if not already present
        if ! [[ " $script_defined_vars " =~ " $var_name " ]]; then
          script_defined_vars="$script_defined_vars $var_name"
        fi
      fi
    done
  fi
fi

# If --from is specified, source the file and create a clean environment
if [ -n "$from_file" ]; then
  if [ ! -f "$from_file" ]; then
    echo "Error: File '$from_file' does not exist" >&2
    exit 1
  fi
  
  # Create a clean environment and export variables from the file
  exec env -i bash -c "
    # Export variables from the file
    while IFS='=' read -r var value || [ -n \"\$var\" ]; do
      # Skip empty lines and comments
      [[ -z \"\$var\" || \"\$var\" =~ ^# ]] && continue
      value=\$(echo \"\$value\" | sed 's/ #.*$//')
      export \"\$var=\$value\"
    done < \"$from_file\"
    
    # Export script_defined_vars if available
    export SCRIPT_DEFINED_VARS=\"$script_defined_vars\"
    
    # Export temp_file if available
    export TEMP_FILE=\"$temp_file\"
    
    # Re-execute the script with the new environment and all flags except for --from to prevent infinite recursion
    exec \"$0\" $(
      printf '%q ' "${passed_flags[@]}"
    )
  "
  exit 0
fi

# Initialize temp_file from environment if available (from --from re-execution)
if [ -n "$TEMP_FILE" ]; then
  temp_file="$TEMP_FILE"
fi

if [ "$script_mode" -eq 1 ]; then
  # Second pass: find template variables and filter out assigned ones
  while IFS= read -r line || [ -n "$line" ]; do
    envsubst_ "$line"
  done < "$temp_file"
else
  # Process the entire input file normally
  while IFS= read -r line || [ -n "$line" ]; do
    envsubst_ "$line"
  done
fi
