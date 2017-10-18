from ai.backend.client.cli.pretty import print_pretty, PrintStatus

import colorama
import time


def test_pretty_output():
    # Currently this is a graphical test -- you should show the output
    # using "-s" option in pytest and check it manually with your eyes.

    pprint = print_pretty
    colorama.init()

    print('normal print')
    pprint('wow wow wow!')
    print('just print')
    pprint('wow!')
    pprint('some long loading.... zzzzzzzzzzzzz', status=PrintStatus.WAITING)
    time.sleep(0.3)
    pprint('doing something...', status=PrintStatus.WAITING)
    time.sleep(0.3)
    pprint('done!', status=PrintStatus.DONE)
    pprint('doing something...', status=PrintStatus.WAITING)
    time.sleep(0.3)
    pprint('doing more...', status=PrintStatus.WAITING)
    time.sleep(0.3)
    pprint('failed!', status=PrintStatus.FAILED)
    print('normal print')


if __name__ == '__main__':
    test_pretty_output()
