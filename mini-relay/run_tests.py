from __future__ import annotations

import argparse
import contextlib
import datetime
import os
import shlex
import shutil
import subprocess
import time
import urllib.request
from typing import Generator


_PYTEST_ENV = {
    'SLEEP_LENGTH': '0',
    'BACKENDS': 'flask',
    'TDA_CONFIG': 'tda/config.local.yaml',
}


def _print_cmd(*cmd: str, **env: str) -> None:
    env_s = ' '.join(f'{k}={shlex.quote(v)}' for k, v in env.items())
    sp = ' ' if env_s else ''
    print(f'+ {env_s}{sp}{shlex.join(cmd)}')


def _run_q(*cmd: str) -> None:
    _print_cmd(*cmd)
    ret = subprocess.call(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ret:
        raise SystemExit(f'`{shlex.join(cmd)}` raised {ret}')


def _discover_tests(args: list[str]) -> list[str]:
    cmd = ('pytest', 'tda/desktop_web', '--collect-only', '--quiet', *args)
    _print_cmd(*cmd, **_PYTEST_ENV)

    out = subprocess.run(
        cmd,
        env={**os.environ, **_PYTEST_ENV},
        capture_output=True,
        text=True,
    )
    if out.returncode:
        raise SystemExit(
            f'pytest discovery failed (exit {out.returncode}):\n'
            f'{out.stdout}{out.stderr}'.rstrip(),
        )

    tests = [s for s in out.stdout.splitlines() if s.startswith('tda/')]
    if not tests:
        raise SystemExit('did not discover any tests!')

    return tests


def _wait_for_started(url: str) -> None:
    for _ in range(10):
        try:
            urllib.request.urlopen(url).read()
        except OSError:
            print('... not started yet')
            time.sleep(.5)
        else:
            break
    else:
        raise SystemExit(f'server at {url} never started!')


@contextlib.contextmanager
def _testctx(testname: str) -> Generator[None]:
    print(f'running {testname}...')

    # clear out existing data before we collect new data
    _run_q(
        'docker', 'compose', 'run', 'mini-relay',
        'bash', '-c',
        'find /data -mindepth 1 -maxdepth 1 -type d | '
        'xargs --no-run-if-empty rm -r',
    )

    _run_q('docker', 'compose', 'up', '--wait')
    try:
        print('waiting for docker-compose to be up...')
        _wait_for_started('http://localhost:3000')
    except BaseException:
        _run_q('docker', 'compose', 'down')
        raise

    try:
        yield
    finally:
        print('... waiting for eventual consistency')
        time.sleep(10)
        print('... trying SIGINT first')
        _run_q(
            'docker', 'compose', 'kill',
            # processes are much more likely to bind SIGINT than SIGTERM
            '--signal=SIGINT',
            # specifically leaving postgres / mini-relay running
            'react', 'ruby', 'flask',
        )
        time.sleep(2)
        _run_q('docker', 'compose', 'down')

        testpart = testname.rpartition('::')[-1]
        testpart = testpart.partition('[')[0]

        print('... saving mock data')
        dt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        target = os.path.join('mini-relay', 'classified', f'{dt}_{testpart}')
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copytree('mini-relay/data', target)


def main() -> int:
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options] [PYTEST_OPTIONS]',
    )
    _, rest = parser.parse_known_args()

    if not os.path.exists('tda'):
        raise SystemExit('expected to run from root of `empower`')

    print('discovering tests...')
    testlist = _discover_tests(rest)
    print(f'=> discovered {len(testlist)} tests')

    ret = 0
    for testname in testlist:
        with _testctx(testname):
            cmd = ('pytest', '-qq', testname)
            _print_cmd(*cmd, **_PYTEST_ENV)
            ret = ret or subprocess.call(cmd, env={**os.environ, **_PYTEST_ENV})

    return ret


if __name__ == '__main__':
    raise SystemExit(main())
