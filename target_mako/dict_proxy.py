from functools import singledispatch
from types import SimpleNamespace
from typing import Any

import singer


@singledispatch
def wrap_namespace(ob):
    if ob is None:
        return SafeNone()
    else:
        return ob


@wrap_namespace.register(dict)
def _wrap_dict(ob):
    return SafeNamespace(**{k: wrap_namespace(v) for k, v in ob.items()})


@wrap_namespace.register(list)
def _wrap_list(ob):
    return [wrap_namespace(v) for v in ob]


class SafeNamespace(SimpleNamespace):
    def __getattribute__(self, name: str) -> Any:
        try:
            logger = singer.get_logger()
            value = super(SafeNamespace, self).__getattribute__(name)
            if value is None:
                logger.info("attribute : '" + name + "' is null returning empty value")
                return SafeNone
            else:
                return value
        except AttributeError:
            logger.info("attribute : '" + name + "' doesn't exists returning empty value")
            return SafeNone


#
# A wrapper for "None" that returns a SafeNone for any attribute
# avoid errors when chaining attribute ex : SafeNone.key1.key2.key3
# and appear as empty string when printed
#
class Meta(type):
    def __getattribute__(*args):
        return SafeNone()

    def __str__(self):
        return ''

    def __repr__(self):
        return ''


class SafeNone(object, metaclass=Meta):
    def __getattribute__(self, name):
        logger = singer.get_logger()
        logger.info("attribute : '" + name + "' doesn't exists returning empty value")
        return SafeNone()

    def __str__(self):
        return ''

    def __repr__(self):
        return ''
