# The MIT License (MIT)
#
# Copyright (c) 2014-2021 Paul Sokolovsky
# Copyright (c) 2014-2020 pycopy-lib contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""A very minimal 'implementation' of the Python Typing library.

Used to avoid import errors, and taken from the
[pcopy-lib](https://github.com/pfalcon/pycopy-lib/blob/master/typing/typing.py) library.
"""


class _Subscriptable:
    def __getitem__(self, sub):
        return None


_SubSingleton = _Subscriptable()


def TypeVar(new_type, *types):
    return None


class Any:
    pass


Text = str


class NoReturn:
    pass


class ClassVar:
    pass


Union = _SubSingleton
Optional = _SubSingleton
Generic = _SubSingleton
NamedTuple = _SubSingleton


class Hashable:
    pass


class Awaitable:
    pass


class Coroutine:
    pass


class AsyncIterable:
    pass


class AsyncIterator:
    pass


class Iterable:
    pass


class Iterator:
    pass


class Literal:
    pass


class Reversible:
    pass


class Sized:
    pass


class Container:
    pass


class Collection:
    pass


Callable = _SubSingleton
AbstractSet = _SubSingleton
MutableSet = _SubSingleton
Mapping = _SubSingleton
MutableMapping = _SubSingleton
Sequence = _SubSingleton
MutableSequence = _SubSingleton


class ByteString:
    pass


Tuple = _SubSingleton
List = _SubSingleton


class Deque:
    pass


Set = _SubSingleton
FrozenSet = _SubSingleton


class MappingView:
    pass


class KeysView:
    pass


class ItemsView:
    pass


class ValuesView:
    pass


class ContextManager:
    pass


class AsyncContextManager:
    pass


Dict = _SubSingleton
DefaultDict = _SubSingleton


class Counter:
    pass


class ChainMap:
    pass


class Generator:
    pass


class AsyncGenerator:
    pass


class Type:
    pass


IO = _SubSingleton
TextIO = IO[str]
BinaryIO = IO[bytes]

AnyStr = TypeVar("AnyStr", str, bytes)


def cast(typ, val):
    return val


def _overload_dummy(*args, **kwds):
    """Raise `NotImplementedError` for @overload when called.

    Parameters
    ----------

    *args:
        Function name to overload.
    **kwds:
        Function parameters

    Raises
    ------

    NotImplementedError:
        This is a stub and cannot be called directly,

    """
    msg = (
        "You should not call an overloaded function. "
        "A series of @overload-decorated functions "
        "outside a stub module should always be followed "
        "by an implementation that is not @overload-ed."
    )
    raise NotImplementedError(msg)


def overload(fun):
    return _overload_dummy
