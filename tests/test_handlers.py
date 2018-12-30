from tests import utils
from aiojsonrpc2.handlers import handlers


async def beuha():
    pass


class A:
    def __init__(self, name):
        self.name = name
    async def hello(self):
        return "Hello %s" % self.name
    async def bonjour(self):
        return "Bonjour %s" % self.name


async def test_handlers(loop):
    h = handlers(utils, beuha, A("Alice"))
    assert 'tests.utils.hello' in h
    assert 'tests.utils.let_it_crash' in h
    assert 'beuha' in h
    assert 'A.hello' in h
    assert 'A.bonjour' in h
    assert len(h) == 5
