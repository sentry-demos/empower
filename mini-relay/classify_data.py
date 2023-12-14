from __future__ import annotations

import argparse
import collections
import json
import os.path
from typing import IO
from typing import NamedTuple


class Item(NamedTuple):
    header: bytes
    body: bytes

    @property
    def header_type(self) -> str:
        return json.loads(self.header)['type']

    def get_se(self) -> str | None:
        try:
            return json.loads(self.body)['tags']['se']
        except (ValueError, KeyError):
            return None


class Envelope(NamedTuple):
    project_id: int
    ts: float
    header: bytes
    items: tuple[Item, ...]

    def get_se(self) -> str | None:
        se = None
        for item in self.items:
            cand_se = item.get_se()
            if se is None and cand_se is not None:
                se = cand_se
            elif se is not None and cand_se is not None and cand_se != se:
                raise AssertionError(f'mixed se? {se=} {cand_se=}')
        return se

    def get_trace_id(self) -> str | None:
        try:
            return json.loads(self.header)['trace']['trace_id']
        except (ValueError, KeyError):
            return None

    def is_session_envelope(self) -> bool:
        return (
            self.items[0].header_type in {'session', 'sessions'} and
            all(
                item.header_type == 'client_report' for item in self.items[1:]
            )
        )

    def is_statsd_envelope(self) -> bool:
        return (
            self.items[0].header_type == 'statsd' and
            all(
                item.header_type == 'client_report' for item in self.items[1:]
            )
        )

    def debug(self) -> str:
        return f'{self.project_id}/{self.ts} {", ".join(item.header_type for item in self.items)}'


def _parse_items(bio: IO[bytes]) -> tuple[Item, ...]:
    ret = []
    while True:
        header = bio.readline()
        if not header:
            break
        contents = json.loads(header)
        if 'length' in contents:
            body = bio.read(contents['length']) + bio.read(1)
        else:
            body = bio.readline()
        ret.append(Item(header=header, body=body))
    return tuple(ret)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('dest')
    args = parser.parse_args()

    envelopes = []

    for subdir in sorted(os.listdir(args.src)):
        subdir = os.path.join(args.src, subdir)
        if not os.path.isdir(subdir):
            continue
        project_id = int(os.path.basename(subdir))

        for event_file in sorted(os.listdir(subdir), key=float):
            event_file = os.path.join(subdir, event_file)
            ts = float(os.path.basename(event_file))

            with open(event_file, 'rb') as f:
                header = f.readline()

                items = _parse_items(f)
                envelopes.append(
                    Envelope(
                        project_id=project_id,
                        ts=ts,
                        header=header,
                        items=items,
                    ),
                )

    trace_id_to_se = {}
    by_se = collections.defaultdict(list)

    # can't classify these :(
    session_envelopes = []
    stats_envelopes = []

    while envelopes:
        new = []

        for envelope in envelopes:
            se = envelope.get_se()

            trace_id = envelope.get_trace_id()

            if se is None and trace_id is not None:
                se = trace_id_to_se.get(trace_id)

            if se is not None:
                by_se[se].append(envelope)

                if trace_id is not None:
                    trace_id_to_se[trace_id] = se

            elif envelope.is_session_envelope():
                session_envelopes.append(envelope)
            elif envelope.is_statsd_envelope():
                stats_envelopes.append(envelope)
            else:
                new.append(envelope)

        if len(new) == len(envelopes):
            for envelope in new:
                print(envelope.debug())
            raise AssertionError(f'unable to classify {len(new)} envelopes')
        else:
            envelopes = new

    print(f'ignoring {len(session_envelopes)} session envelopes')
    print(f'ignoring {len(stats_envelopes)} statsd envelopes')
    os.makedirs(args.dest, exist_ok=True)
    for k, v in by_se.items():
        k = k.replace('/', '__')
        for envelope in v:
            fname = f'{args.dest}/{k}/{envelope.project_id}/{envelope.ts}'
            os.makedirs(os.path.dirname(fname), exist_ok=True)
            with open(fname, 'wb') as f:
                f.write(envelope.header)
                for item in envelope.items:
                    f.write(item.header)
                    f.write(item.body)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
