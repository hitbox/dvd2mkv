import argparse
import collections
import os
import subprocess

from argparse import ArgumentParser

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


def handbrake(input, dry=False, **kwargs):
    hbopts = CommandOptions({
        'preset': 'Super HQ 1080p30 Surround',
        'x264-preset': 'slow',
        'x264-tune': 'film',

        'drc': '3.0',
        'subtitle': ','.join(map(str,range(1,11))),
        'audio': ','.join(map(str,range(1,11))),
        'markers': True,
        'optimize': True,
        'two-pass': True,
        'turbo': True,
        'main-feature': True,

        'input': input,
        'output': '%s.mkv' % (input.rstrip('/'), ),
    })

    for key, value in kwargs.items():
        hbopts[key] = value

    if not hbopts['output'].endswith('.mkv'):
        hbopts['output'] += '.mkv'

    if 'main-feature' in hbopts and 'title' in hbopts:
        del hbopts['main-feature']

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


def main(argv=None):
    """
    Encode dvd dirs with favorite HandBrakeCLI settings.
    """
    parser = argparse.ArgumentParser(prog=__name__, description=main.__doc__)

    #parser.add_argument('inputs', nargs='+', type=directory,
    #                    help='The directories to encode.')
    parser.add_argument('input')
    parser.add_argument('-n', '--dry', action='store_true',
                        help='Dry run. Just print HandBrakeCLI command line.'
                        ' Must appear before `inputs` list.')
    parser.add_argument('extra', nargs=argparse.REMAINDER, action=ExtraAction,
                        help='Extra HandBrakeCLI options. Must be at the end.'
                        ' Does NOT capture flags.')

    args = parser.parse_args(argv)

    if 'output' in args.extra and len(args.inputs) > 1:
        parser.exit('Cannot accept more than one input if the output option is given.')

    #for dirname in args.inputs:
    #    handbrake(dirname, args.dry, **args.extra)
    handbrake(args.input, args.dry, **args.extra)
