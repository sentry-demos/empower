#!/bin/bash

# envsubst on steroids

show_usage() {
  cat << 'EOF'
Usage: envsubst.sh [--strict | --strict-allow-empty | --strict-allow-quoted-empty | --list] [--script] [--ignore-prefix=<prefix>] [--from=<file>] [--interpret-quotes]

DESCRIPTION:
    Enhanced environment variable substitution tool that processes templates
    containing ${VAR} or $VAR syntax and replaces them with actual values.
    Reads template from stdin and writes substituted output to stdout.

OPTIONS:
    --strict
        Strict mode: Fail if any variable referenced in the template is 
        undefined or empty, or ''/"" when --interpret-quotes.
  
    --strict-allow-quoted-empty
        Fail if any variable referenced in the template is undefined or empty, 
        but allow ''/"". Requires --interpret-quotes.

    --strict-allow-empty  
        Fail if any variable referenced in the template is undefined, 
        but allow empty values or ''/""

    --list
        List mode: Instead of substituting variables, output a list of all
        unique variable names found in the template. Useful for discovering
        what variables a template requires.

    --script
        Script mode: Ignore variables that are defined within the input itself.
        Useful when processing shell scripts that contain both variable 
        assignments and template variables that should be substituted.
        Currently not very smart - doesn't understand for loops, etc
        (consider using --ignore-prefix as workaround if having issues)

    --ignore-prefix=<prefix>
        Ignore variables whose names start with the specified prefix.
        These variables will be left as-is in the output instead of being
        substituted.

    --from=<file>
        Source environment variables from the specified file before processing
        and NOT use the current environment. The file should contain KEY=VALUE
        pairs (one per line). Comments starting with # are ignored.

    --interpret-quotes
        Quote interpretation mode: Treat environment variable values that are
        entirely surrounded by matching quotes (single or double) as literal
        values by removing the surrounding quotes. Only affects values that
        are completely quoted, not partially quoted values.

    --help, -h
        Display this help message and exit.

EXAMPLES:
    # Basic substitution
    echo 'Hello ${USER}!' | envsubst.sh

    # Strict mode - fail if any variable is undefined/empty (or ''/"" when --interpret-quotes)  
    echo 'Config: ${CONFIG_FILE}' | envsubst.sh --strict

    # List all variables in a template
    cat template.txt | envsubst.sh --list

    # Process with variables from a file
    cat template.txt | envsubst.sh --from=production.env

    # Script mode - ignore variables defined in the script itself
    cat deploy_script.sh | envsubst.sh --script

    # Ignore variables starting with 'LOCAL_'
    cat template.txt | envsubst.sh --ignore-prefix=LOCAL_

    # Interpret quoted values (THING='' becomes empty string, STUFF="don't" becomes don't)
    echo '${STUFF}${THING}' | envsubst.sh --interpret-quotes

    # Strict mode allowing quoted empty values
    echo '${EMPTY_QUOTED}' | EMPTY_QUOTED="''" ./_bin/envsubst.sh --strict-allow-quoted-empty --interpret-quotes

NOTES:
    - Only one of --strict, --strict-allow-empty, or --list can be used at once
    - --from and --list cannot be used together
    - Use \$ to escape dollar signs that should not be substituted
    - Variables can use ${VAR} or $VAR syntax
    - Variable names must start with a letter or underscore, followed by
      letters, numbers, or underscores
    - With --interpret-quotes, only completely quoted values have quotes removed

EOF
}

strict_mode=0
strict_allow_empty_mode=0
strict_allow_quoted_empty_mode=0
list_mode=0
script_mode=0
interpret_quotes=0
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

# Function to interpret quoted values if the flag is enabled
interpret_quoted_value() {
  local value="$1"
  
  if [ "$interpret_quotes" -eq 0 ]; then
    echo "$value"
    return
  fi
  
  # Check if the entire value is surrounded by matching quotes
  if [[ "$value" =~ ^\'.*\'$ ]]; then
    # Single quoted - remove first and last single quote
    if [ ${#value} -eq 2 ]; then
      echo ""  # Empty string for ''
    else
      echo "${value:1:$((${#value}-2))}"
    fi
  elif [[ "$value" =~ ^\".*\"$ ]]; then
    # Double quoted - remove first and last double quote
    if [ ${#value} -eq 2 ]; then
      echo ""  # Empty string for ""
    else
      echo "${value:1:$((${#value}-2))}"
    fi
  else
    # Not completely quoted, return as-is
    echo "$value"
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

get_variable_substitution() {
  local var_name="$1"
  
  # Check if variable is defined before substitution
  if [ "${!var_name+_}" = "_" ]; then
    local var_value=$(interpret_quoted_value "${!var_name}")
    echo "$var_value"
  else
    # Variable is undefined, leave as-is (this will happen only in non-strict mode)
    echo "\${$var_name}"
  fi
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
    if [ "$strict_mode" -eq 1 ] || [ "$strict_allow_empty_mode" -eq 1 ] || [ "$strict_allow_quoted_empty_mode" -eq 1 ]; then
      echo "[ERROR] bin/envsubst.sh: Variable '$var_name' is not defined" >&2
      exit 1
    fi
  elif [ -z "${!var_name}" ]; then 
    # Variable is defined but empty 
    if [ "$strict_mode" -eq 1 ] || [ "$strict_allow_quoted_empty_mode" -eq 1 ]; then
      echo "[ERROR] bin/envsubst.sh: Variable '$var_name' is empty. Please use ''/\"\" if intentionally empty." >&2
      exit 1
    fi
  elif [[ "$var_value" =~ ^\'\'$ ]] || [[ "$var_value" =~ ^\"\"$ ]]; then
    # Variable is ''/""
    if [ "$interpret_quotes" -eq 1 ] && [ "$strict_mode" -eq 1 ]; then
      echo "[ERROR] bin/envsubst.sh: Variable '$var_name' is an empty quoted string (''/\"\")" >&2
      exit 1
    fi
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
      if [ "$char" = '}' ]; then
        # Check if var_name is a valid shell variable name
        if [[ "$var_name" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
          if should_ignore "$var_name"; then
            output="$output\${$var_name}" # output variable name's characters but not the value
          else
            check_var_defined_or_list "$var_name"
            local substitution_result=$(get_variable_substitution "$var_name")
            output="$output$substitution_result" # in --list mode we still do this but discard the output later
          fi
        else
          # Invalid variable name - output unchanged
          output="$output\${$var_name}"
        fi
        var_name=""
        in_var=0
      else
        # Collect any character until we hit }
        var_name="$var_name$char"
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
          local substitution_result=$(get_variable_substitution "$var_name")
          output="$output$substitution_result$char"
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
      local substitution_result=$(get_variable_substitution "$var_name")
      output="$output$substitution_result"
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
    --strict-allow-quoted-empty)
      strict_allow_quoted_empty_mode=1
      passed_flags+=("--strict-allow-quoted-empty")
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
    --interpret-quotes)
      interpret_quotes=1
      passed_flags+=("--interpret-quotes")
      shift
      ;;
    --help|-h)
      show_usage
      exit 0
      ;;
    *)
      echo "Error: Unknown option '$1'. Try --help for usage information." >&2
      echo "" >&2
      show_usage
      exit 1
      ;;
  esac
done

# Validate options
if [ $((strict_mode + strict_allow_empty_mode + strict_allow_quoted_empty_mode + list_mode)) -gt 1 ]; then
  echo "[ERROR] Only one of --strict, --strict-allow-empty, --strict-allow-quoted-empty, or --list can be used" >&2
  exit 1
fi

# Validate that --strict-allow-quoted-empty requires --interpret-quotes
if [ "$strict_allow_quoted_empty_mode" -eq 1 ] && [ "$interpret_quotes" -eq 0 ]; then
  echo "[ERROR] --strict-allow-quoted-empty requires --interpret-quotes to be specified" >&2
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
