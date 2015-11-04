#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import ascii_letters
from subprocess import check_output


def process_url(url):

    # check if document is html
    #header = check_output(['ls'])
    header = check_output(['/usr/bin/lynx', '-head', '-dump', url])

    if 'text/html' not in header:
        return ()
    content = check_output(['/usr/bin/lynx', '-dump', url])
    index_reference = content.find('\nReferences\n')

    if index_reference > -1:
        content = content[:index_reference]

    # get to lower case
    content = content.lower()
    list_content = list(content)

    # eliminate special characters
    for i in range(len(list_content)):
        if list_content[i] not in ascii_letters:
            list_content[i] = ' '

    inside_bracket = False
    i = 0
    while True:
        try:
            # if we are inside brackets
            if inside_bracket:
                list_content.pop(i)
            else:
                i += 1

            # test when we are switching from
            # test when we are switching from
            # inside to outside brackets
            if list_content[i] == '[':
                inside_bracket = True
            if list_content[i] == ']':
                list_content.pop(i)
                inside_bracket = False
        except IndexError:
            break

    # remove extra whitespaces
    content = ''.join(list_content)
    list_content = content.split()
    return(set(list_content))
