
from jsonrpc.exceptions import (
    JSONRPCInvalidParams,
    JSONRPCInvalidRequest,
    JSONRPCInvalidRequestException,
    JSONRPCMethodNotFound,
    JSONRPCParseError,
    JSONRPCServerError,
    JSONRPCDispatchException,
)

__exceptions = dict()
for e in [
    JSONRPCInvalidParams,
    JSONRPCInvalidRequest,
    JSONRPCMethodNotFound,
    JSONRPCParseError,
    JSONRPCServerError,
]:
    __exceptions[e.CODE] = e


def from_data(data):
    data = data['error']
    return __exceptions[data['code']](
            code=data["code"], message=data["message"], data=data.get("data"))
