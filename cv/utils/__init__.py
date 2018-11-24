from django.utils.translation import ugettext_lazy as _

import re

from .cite import CSLError, CSLKeyError, CSLCitation, CSLStyle


def check_isbn(isbn_raw):
    """
    Returns ISBN for well-formated ISBN candidates and throws
    ``ValueError`` otherwise.

    The function checks that the formatting of the ISBN to follows standards
    and that the final checksum digit is correct.
    """
    isbn = re.findall('[\dX]', isbn_raw.upper())
    isbn = "".join(isbn)
    m = re.fullmatch(r'\d{9}[0-9xX]|\d{13}', isbn)
    print(isbn)
    if m:
        isbn = m.group()
        if len(isbn) == 13:
            info = isbn[0:12]
            mult = [i for item in range(6) for i in [1, 3]]
            summed = sum([int(n) * v for n, v in zip(info, mult)])
            check_digit = 10 - (summed % 10)
            check_digit = str(check_digit) if check_digit != 10 else 0
            if check_digit == isbn[-1]:
                return isbn
        else:
            info = isbn[0:9]
            summed = sum([int(n) * v for n, v in zip(info, range(10, 0, -1))])
            check_digit = 11 - summed % 11
            check_digit = str(check_digit) if check_digit != 10 else "X"
            if check_digit == isbn[-1]:
                return isbn
        raise ValueError(_("Inproper checksum digit for ISBN, check "
                           "that you entered the ISBN correctly"))
    raise ValueError(_("Improperly formatted ISBN"))

