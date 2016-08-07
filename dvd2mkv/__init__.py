#!/usr/bin/env python
import argparse
import collections
import os
import subprocess

def istruefalse(thing):
    return thing is True or thing is False

class CommandOptions(collections.OrderedDict):

    def options_list(self):
        args = []
        for key, value in self.items():

            if len(key) == 1:
                key = '-%s' % key
            else:
                key = '--%s' % key

            args.append(key)
            if not istruefalse(value):
                args.append('%s' % value)
        return args

commafy = ','.join

def strrange(*args):
    return map(str, range(*args))

def commarange(*args):
    return commafy(strrange(*args))

def handbrake(input, dry=False, **kwargs):
    hbopts = CommandOptions(kwargs)

    hbopts.setdefault('preset', 'High Profile')
    hbopts.setdefault('drc', '3.0')
    hbopts.setdefault('subtitle', commarange(1, 11))
    hbopts.setdefault('audio', commarange(1, 11))
    hbopts.setdefault('markers', True)
    hbopts.setdefault('optimize', True)
    hbopts.setdefault('two-pass', True)
    hbopts.setdefault('turbo', True)
    hbopts.setdefault('main-feature', True)

    hbopts['input'] = input
    hbopts['output'] = '%s.mkv' % (input.rstrip('/'), )

    cmd = ['HandBrakeCLI'] + hbopts.options_list()
    if dry:
        print(subprocess.list2cmdline(cmd))
    else:
        subprocess.call(cmd)

def directory(name):
    if os.path.isdir(name):
        return name
    else:
        msg = '%r is not a directory' % name
        raise argparse.ArgumentTypeError(msg)

class ExtraAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        extra = { k.lstrip('-'):v for k,v in zip(values[:-1:2], values[1::2]) }
        setattr(namespace, self.dest, extra)


def parse_args():
    parser = argparse.ArgumentParser(description=main.__doc__)
    _a = parser.add_argument
    _a('inputs', nargs='+', type=directory,
       help='The directories to encode.')
    _a('-n', '--dry', action='store_true',
       help='Dry run. Just print HandBrakeCLI command line.')
    _a('extra', nargs=argparse.REMAINDER, action=ExtraAction,
       help='Extra HandBrakeCLI options. Must be at the end.')

    return parser.parse_args()

def main():
    """
    Encode dvd dirs with favorite HandBrakeCLI settings.
    """
    args = parse_args()

    for dirname in args.inputs:
        handbrake(dirname, args.dry, **args.extra)
