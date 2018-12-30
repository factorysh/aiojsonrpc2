from tests import utils
from aiojsonrpc2.handlers import handlers


async def beuha():
    pass


def test_handlers():
    h = handlers(utils, beuha)
    assert 'tests.utils.hello' in h
    assert 'tests.utils.let_it_crash' in h
    assert 'beuha' in h
    assert len(h) == 3
