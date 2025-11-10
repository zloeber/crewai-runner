# MCP Test Fix Summary

## Issue Description
The test `tests/test_mcp.py::test_add_server` was failing with a Pydantic validation error:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for MCPServer
transport
  Input should be a valid dictionary or instance of MCPTransport [type=model_type, input_value=MCPTransport(type='stdio'...ne, port=None, url=None), input_type=MCPTransport]
```

## Root Cause
The issue occurred when creating `MCPServer` instances from `MCPServerConfig` objects. Both models have a `transport: MCPTransport` field, but when passing an already-instantiated `MCPTransport` object from one Pydantic model to another, Pydantic v2 was rejecting it during validation.

This happened in two places:
1. `MCPServerManager.add_server()` - when creating new servers
2. `MCPServerManager.update_server()` - when updating existing servers

## Solution Applied

### Fix 1: add_server method
**File**: `src/engine/services/mcp_manager.py`

Changed:
```python
server = MCPServer(
    # ... other fields ...
    transport=config.transport,
    # ... other fields ...
)
```

To:
```python
server = MCPServer(
    # ... other fields ...
    transport=config.transport.model_dump(),
    # ... other fields ...
)
```

### Fix 2: update_server method
**File**: `src/engine/services/mcp_manager.py`

Changed:
```python
server.transport = config.transport
```

To:
```python
server.transport = MCPTransport(**config.transport.model_dump())
```

## Technical Details

- **Pydantic v2 Behavior**: When assigning nested Pydantic models, v2 is stricter about re-validation
- **Solution**: Convert the transport object to a dictionary using `model_dump()` and let Pydantic re-create the object
- **Alternative**: For direct assignment, reconstruct the object using `MCPTransport(**config.transport.model_dump())`

## Test Results

All MCP tests now pass:
```
tests/test_mcp.py::test_add_server PASSED
tests/test_mcp.py::test_list_servers PASSED
tests/test_mcp.py::test_get_server PASSED
tests/test_mcp.py::test_update_server PASSED
tests/test_mcp.py::test_delete_server PASSED
tests/test_mcp.py::test_delete_nonexistent_server PASSED
tests/test_mcp.py::test_get_server_status PASSED
tests/test_mcp.py::test_multiple_servers PASSED
tests/test_mcp.py::test_export_servers PASSED
tests/test_mcp.py::test_import_servers_from_claude_config PASSED
tests/test_mcp.py::test_import_invalid_json PASSED
```

## Code Quality

✅ **Linting**: All checks passed with ruff  
✅ **Formatting**: Code follows black formatting standards  
✅ **Type Safety**: No type checking issues  
✅ **Functionality**: All existing tests continue to pass  

## Impact

- ✅ **Fixed**: MCP server management functionality now works correctly
- ✅ **No Regressions**: All existing functionality preserved
- ✅ **Test Coverage**: Comprehensive test suite validates the fixes
- ✅ **Standards Compliance**: Changes follow project coding standards

This fix resolves the immediate test failure while maintaining code quality and ensuring robust MCP server management functionality.