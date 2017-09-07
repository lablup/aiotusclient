'''
A standalone script to generate some loads to the public API server.
It assumes that you have already configured the access key and secret key
as environment variables.
'''

import argparse
import logging
import multiprocessing
from statistics import mean, median, stdev
import sys
import time

import pytest

from ai.backend.client.kernel import create_kernel, destroy_kernel, execute_code, restart_kernel

log = logging.getLogger('ai.backend.client.test.load')

sample_code = '''
import os
print('ls:', os.listdir('.'))
with open('test.txt', 'w') as f:
    f.write('hello world')
'''

sample_code_julia = '''
println("wow")
'''


def print_stat(msg, times_taken):
    print('{}: mean {:.2f} secs, median {:.2f} secs, stdev {:.2f}'.format(
        msg, mean(times_taken), median(times_taken), stdev(times_taken)
    ))


def run_create_kernel(_idx):
    begin = time.monotonic()
    try:
        kid = create_kernel('python3')
    except:
        log.exception('run_create_kernel')
        kid = None
    finally:
        end = time.monotonic()
    t = end - begin
    return t, kid


def create_kernels(concurrency, parallel=False):
    kernel_ids = []
    times_taken = []

    if parallel:
        pool = multiprocessing.Pool(concurrency)
        results = pool.map(run_create_kernel, range(concurrency))
        for t, kid in results:
            times_taken.append(t)
            kernel_ids.append(kid)
    else:
        for _idx in range(concurrency):
            t, kid = run_create_kernel(_idx)
            times_taken.append(t)
            kernel_ids.append(kid)

    print_stat('create_kernel', times_taken)
    return kernel_ids


def run_execute_code(kid):
    # 2nd params is currently ignored.
    if kid is not None:
        begin = time.monotonic()
        result = execute_code(kid, sample_code)
        print(result['stdout'])
        end = time.monotonic()
        return end - begin
    return None


def execute_codes(kernel_ids, parallel=False):
    times_taken = []

    if parallel:
        pool = multiprocessing.Pool(len(kernel_ids))
        results = pool.map(run_execute_code, kernel_ids)
        for t in results:
            if t is not None:
                times_taken.append(t)
    else:
        for kid in kernel_ids:
            t = run_execute_code(kid)
            if t is not None:
                times_taken.append(t)

    print_stat('execute_code', times_taken)


def run_restart_kernel(kid):
    # 2nd params is currently ignored.
    if kid is not None:
        begin = time.monotonic()
        restart_kernel(kid)
        end = time.monotonic()
        return end - begin
    return None


def restart_kernels(kernel_ids, parallel=False):
    times_taken = []

    if parallel:
        pool = multiprocessing.Pool(len(kernel_ids))
        results = pool.map(run_restart_kernel, kernel_ids)
        for t in results:
            if t is not None:
                times_taken.append(t)
    else:
        for kid in kernel_ids:
            t = run_restart_kernel(kid)
            if t is not None:
                times_taken.append(t)

    print_stat('restart_kernel', times_taken)


def run_destroy_kernel(kid):
    if kid is not None:
        begin = time.monotonic()
        destroy_kernel(kid)
        end = time.monotonic()
        return end - begin
    return None


def destroy_kernels(kernel_ids, parallel=False):
    times_taken = []

    if parallel:
        pool = multiprocessing.Pool(len(kernel_ids))
        results = pool.map(run_destroy_kernel, kernel_ids)
        for t in results:
            if t is not None:
                times_taken.append(t)
    else:
        for kid in kernel_ids:
            t = run_destroy_kernel(kid)
            if t is not None:
                times_taken.append(t)

    print_stat('destroy_kernel', times_taken)


@pytest.mark.integration
@pytest.mark.parametrize('concurrency,parallel,restart', [
    (5, False, False),
    (5, True,  False),
    (5, False, True),
    (5, True,  True),
])
def test_high_load_requests(capsys, defconfig, concurrency, parallel, restart):
    # Show stdout for timing statistics
    with capsys.disabled():
        kids = create_kernels(concurrency, parallel)
        execute_codes(kids, parallel)
        if restart:
            restart_kernels(kids, parallel)
            execute_codes(kids, parallel)
        destroy_kernels(kids, parallel)
