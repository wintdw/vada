from fastapi import Request


async def get_flows(request: Request):
    """Get flows from application state"""
    return request.app.state.flows
