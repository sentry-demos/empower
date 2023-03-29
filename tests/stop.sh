#!/bin/bash

# Here is what the process tree looks like:
#
# 23271 /bin/bash ./loop.sh ./jobs/desktop_web.sh
# 23414  \_ /bin/bash ./jobs/desktop_web.sh
# 23415      \_ /home/kosty_maleyev/tests/env/bin/python3.8 /home/kosty_maleyev/tests/env/bin/pytest -s -n 6 desktop_web
# 23418          \_ /home/kosty_maleyev/tests/env/bin/python3.8 -u -c import sys;exec(eval(sys.stdin.readline()))
# 23421          \_ /home/kosty_maleyev/tests/env/bin/python3.8 -u -c import sys;exec(eval(sys.stdin.readline()))
# 23425          \_ /home/kosty_maleyev/tests/env/bin/python3.8 -u -c import sys;exec(eval(sys.stdin.readline()))
# 23427          \_ /home/kosty_maleyev/tests/env/bin/python3.8 -u -c import sys;exec(eval(sys.stdin.readline()))
# 23272 /bin/bash ./loop.sh ./jobs/mobile_native.sh
# 23274  \_ /bin/bash ./jobs/mobile_native.sh
# 23275      \_ /home/kosty_maleyev/tests/env/bin/python3.8 /home/kosty_maleyev/tests/env/bin/pytest -s mobile_native

if pgrep -f '[p]ython.*pytest'; then
    # Need to kill parent (sh ./loop.sh) otherwise the infinite loop will keep on
    # spawning new pytest processes
    # `pgrep -f 'command'` -> `pgrep -f '[c]ommand'` to prevent it from matching itself
    # sudo because may have been started by different user
    sudo kill -9 $(ps -ho pid,ppid `pgrep -f '[b]ash \./jobs/.*\.sh'` | xargs);
    sudo pkill -f '[p]ython.*pytest';
else 
    echo "No process found"; 
fi