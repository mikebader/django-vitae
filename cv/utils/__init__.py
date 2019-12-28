from django.utils.translation import ugettext_lazy as _

import re

from .cite import CSLError, CSLKeyError, CSLCitation, CSLStyle


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
    

