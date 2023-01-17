from fastapi import APIRouter
from fastapi import Request, Response, status, HTTPException
from fastapi import Query, Path
from app.src.libs.json_utils import json_mapper
import requests
import urllib3

#APIRouter creates path operations for user module
router = APIRouter(
    #prefix="/api/itsm/aranda",
    tags=["EXAMPLE"],
    responses={404: {"description": "Not found"}},
)

@router.get("/v1/example",
    summary="Makes a request that returns data from a remote REST api",
    response_description="Makes a request that returns data from a remote REST api")
async def whoami(
        request: Request,
        response: Response,
        timeout: float = Query(default=None, description='Wait timeout for underline requests', example=60)
    ):
    """
    ### This route is make a request that returns data from a remote REST api
    
    - **timeout**: Wait timeout for underline requests.

    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    me = 'example'
    try:
        _response = requests.get('https://httpbin.org/json', timeout=timeout)
    except requests.exceptions.ReadTimeout as e:
        raise HTTPException(status_code=408, detail=f'Timeout when attempting to read {me} from underline api: {e}')
    except Exception as e:
        raise HTTPException(status_code=503, detail=f'Unknow server error: {e}')
    if _response:
        response.status_code = _response.status_code
        if response.status_code >= 200 and response.status_code < 300:
            try:
                data = _response.json()
            except Exception as e:
                raise HTTPException(status_code=503, detail=f'Unable to retrieve valid JSON response from Aranda instance')
            return data
        else:
            raise HTTPException(status_code=503, detail=f'Unable to retrieve data from api')
    else:
        raise HTTPException(status_code=503, detail=f'Unable to retrieve data from api')
