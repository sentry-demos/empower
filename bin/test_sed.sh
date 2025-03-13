#!/bin/bash

# Function to run the sed command and compare output
test_sed() {
  input="$1"
  expected_output="$2"
  actual_output=$(echo "$input" | sed -E 's/([[:alnum:]_]*(password|PASSWORD|token|TOKEN|secret|SECRET)[[:alnum:]_]*)[[:space:]]*[=:][[:space:]]*(.{4}).*/\1: \3****/g')

  if [[ "$actual_output" == "$expected_output" ]]; then
    echo "PASS: $input"
  else
    echo "FAIL: $input"
    echo "  Expected: $expected_output"
    echo "  Actual:   $actual_output"
    exit 1
  fi
}

# Test cases
test_sed "DB_PASSWORD: mysecretpassword123" "DB_PASSWORD: myse****"
test_sed "DB_PASSWORD:mysecretpassword123" "DB_PASSWORD: myse****"
test_sed "DB_PASSWORD=mysecretpassword123" "DB_PASSWORD: myse****"
test_sed "DB_PASSWORD = mysecretpassword123" "DB_PASSWORD: myse****"
test_sed "PASSWORD_FOR_DB: mysecretpassword123" "PASSWORD_FOR_DB: myse****"
test_sed "MY_SECRET: mysecretvalue" "MY_SECRET: myse****"
test_sed "AUTH_TOKEN_2=mytokenvalue" "AUTH_TOKEN_2: myto****"
test_sed "secret_key : verysecret" "secret_key: very****"
test_sed "PASSWORD: supersecret" "PASSWORD: supe****"
test_sed "TOKEN = mytoken" "TOKEN: myto****"
test_sed "SECRET: supersecret" "SECRET: supe****"
test_sed "MY_PASSWORD_KEY=12345678" "MY_PASSWORD_KEY: 1234****"
test_sed "MY_TOKEN_VAR : abcdef" "MY_TOKEN_VAR: abcd****"
test_sed "MY_SECRET_KEY = 12345678" "MY_SECRET_KEY: 1234****"
test_sed "Not a matching line" "Not a matching line"
test_sed "PASSWORD_KEY=123" "PASSWORD_KEY=123"
