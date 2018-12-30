from jsonrpc.exceptions import (
    JSONRPCInvalidParams,
    JSONRPCInvalidRequest,
    JSONRPCInvalidRequestException,
    JSONRPCMethodNotFound,
    JSONRPCParseError,
    JSONRPCServerError,
    JSONRPCDispatchException,
)

from aiojsonrpc2 import exceptions


def test_excpetions():
    e = exceptions.from_data(dict(id=42, error=dict(code=-32700, message="")))
    assert isinstance(e, JSONRPCParseError)
    print(e)
