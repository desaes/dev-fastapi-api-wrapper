from fastapi import APIRouter
from fastapi import Request, Response, status, HTTPException
from fastapi import Query, Path
from app.src.libs.json_utils import json_mapper

#APIRouter creates path operations for user module
router = APIRouter(
    #prefix="/api/itsm/aranda",
    tags=["ITSM ARANDA"],
    responses={404: {"description": "Not found"}},
)

@router.get("/v1/token",
    summary="Aranda Token",
    response_description="Aranda Token")
async def get_token(
        request: Request
    ):
    """
    ### This route is used get a valid Aranda authentication token
    
    - **timeout**: Wait timeout for underline requests.

    #### Call example: http(s)://{api-server}/automation/itsm/aranda-api-auther/v1/token

    """
    if request.app.aranda:
        return {"token": request.app.aranda.token()}
    else:
        raise HTTPException(status_code=503, detail=f'Not authenticated on Aranda instance yet, retry again later')