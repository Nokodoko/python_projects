#!/bin/env python3


odd_list = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
even_list = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]


def add_odd(*odd):
    total = 0
    for digit in odd:
        total += digit
    return total


def alt_odd(odd):
    return (len(odd) - 1) ** 2


def add_even(*even):
    total = 0
    for digit in even:
        total += digit
    return total


def add_all(odds, evens):
    return odds + evens


print(f'odd: {add_odd(odd_list)}')
print(f'\talt odd: {alt_odd(odd_list)}')
print(f'even: {add_even(even_list)}')
print(f'all: {add_all(add_odd(odd_list), add_even(even_list))}')
