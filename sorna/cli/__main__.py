from sorna.cli import global_argparser

import sorna.cli.run  # noqa


args = global_argparser.parse_args()
args.function(args)
