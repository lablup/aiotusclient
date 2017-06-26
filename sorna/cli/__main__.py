import configargparse

from sorna.cli import global_argparser
import sorna.cli.run


args = global_argparser.parse_args()
args.function(args)
