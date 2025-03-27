#!/bin/bash

envsubst_() {
  local input="$1"
  # First, replace \$ with a unique placeholder that won't appear in normal text
  local placeholder=$'\x01ESCAPED_DOLLAR\x02'
  input="${input//\\\$/$placeholder}"

  local output=""
  local i=0
  local len=${#input}
  local in_var=0
  local var_name=""

  while [ "$i" -lt "$len" ]; do
    local char="${input:$i:1}"

    if [ "$in_var" -eq 1 ]; then
      if [[ "$char" =~ [a-zA-Z0-9_] ]]; then
        var_name="$var_name$char"
      elif [ "$char" = '}' ]; then
        if [ -n "$var_name" ]; then
          output="$output${!var_name}"
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
          output="$output${!var_name}$char"
          var_name=""
          in_var=0
      fi
    else
      output="$output$char"
    fi
    i=$((i+1))
  done

  if [ "$in_var" -eq 2 ]; then
    output="$output${!var_name}"
  fi

  # Convert the placeholder back to $
  printf "%s\n" "${output//$placeholder/$}"
}

# Process the entire input file
while IFS= read -r line; do
  envsubst_ "$line"
done
