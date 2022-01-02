from django.utils.translation import gettext_lazy as _

from cv import settings

from .cite import CSLError, CSLKeyError, CSLCitation, CSLStyle

import re


class ISBNError(ValueError):
    pass

def check_isbn(isbn_raw):
    """
    Returns ISBN for well-formated ISBN candidates and throws
    ``ValueError`` otherwise.

    The function checks that the formatting of the ISBN to follows standards
    and that the final checksum digit is correct.

    9780195325720
    """

    isbn = re.findall('[\dX]', isbn_raw.upper())
    isbn = "".join(isbn)
    if not re.fullmatch(r'\d{9}[0-9xX]|\d{13}', isbn):
        raise ISBNError(_('Improperly formatted ISBN'))
    # isbn = m.group()
    if len(isbn) == 13:
        mult = [i for item in range(6) for i in [1, 3]]
        summed = sum([int(n) * v for n, v in zip(isbn[0:12], mult)])
        check_digit = '%02.0f' % (10 - (summed % 10))
        if check_digit[1] == isbn[-1]:
            return isbn_raw
    elif len(isbn) == 10:
        summed = sum([int(n) * v for n, v in zip(isbn[0:9], range(10, 0, -1))])
        check_digit = str(11 - summed % 11).replace('10', 'X')
        # check_digit = str(check_digit) if check_digit != 10 else "X"
        if check_digit == isbn[-1]:
            return isbn_raw
    raise ISBNError(_('Inproper checksum digit for ISBN, check '
                      'that you entered the ISBN correctly'))


def construct_name(obj,
                   given_first=True, highlight_key_authors=True,
                   initials=False, initial_char='.'):
    """Constructs a formatted string representation of a name."""
    from cv.models import Collaborator
    key_contributors = settings.CV_KEY_CONTRIBUTOR_LIST

    print_middle = False
    # Following checks to see if the object passed is a Collaborator
    if type(obj) != Collaborator:
        collab = obj.collaborator
        print_middle = obj.print_middle
    else:
        collab = obj
    given_part = collab.first_name
    if print_middle and collab.middle_initial:
        given_part = '{} {}'.format(given_part, collab.middle_initial)
    if initials:
        initial_sep = '{}'.format(initial_char)
        given_part = initial_sep.join(re.findall(r'(?:^|\s)(\w)', given_part))
        given_part = '{}{}'.format(given_part, initial_char)

    start_text, end_text = "", ""
    if highlight_key_authors and collab.email in key_contributors:
        start_text, end_text = "<span class='author-emphasis'>", "</span>"
    else:
        start_text, end_text = "", ""

    if given_first:
        return '{}{} {}{}'.format(
            start_text, given_part, collab.last_name, end_text)
    return '{}{}, {}{}'.format(
        start_text, collab.last_name, given_part, end_text)
