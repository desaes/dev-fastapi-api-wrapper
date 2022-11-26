from fastapi import APIRouter
from fastapi import Request, Response, status, HTTPException
from fastapi import Query, Path
from app.src.libs.json_utils import json_mapper
import requests
import urllib3

#APIRouter creates path operations for user module
router = APIRouter(
    #prefix="/api/itsm/aranda",
    tags=["ITSM ARANDA"],
    responses={404: {"description": "Not found"}},
)

@router.get("/v1/whoami",
    summary="Aranda User Information",
    response_description="Aranda User Information")
async def whoami(
        request: Request,
        response: Response,
        timeout: float = Query(default=None, description='Wait timeout for underline requests', example=60)
    ):
    """
    ### This route is used get if a token is still valid
    
    - **timeout**: Wait timeout for underline requests.

    #### Call example: http(s)://{api-server}/automation/itsm/aranda-api-auther/v1/whoami

    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    me = 'whoami'
    request.app.aranda.token()
    if request.app.aranda:
        try:
            _response = request.app.aranda.request(obj_type=me, method='get', timeout=timeout)
        except requests.exceptions.ReadTimeout as e:
            raise HTTPException(status_code=408, detail=f'Timeout when attempting to read {me} from underline Aranda instance: {e}')
        except Exception as e:
            raise HTTPException(status_code=503, detail=f'Unknow server error: {e}')
        if _response:
            response.status_code = _response.status_code
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    data = _response.json()
                except Exception as e:
                    raise HTTPException(status_code=503, detail=f'Unable to retrieve valid JSON response from Aranda instance')
                if not data.get('id'):
                    raise HTTPException(status_code=404, detail=f"Item not found")
                return data
            else:
                raise HTTPException(status_code=503, detail=f'Unable to retrieve data from Aranda instance')
        else:
            raise HTTPException(status_code=503, detail=f'Unable to retrieve data from Aranda instance')
    else:
        raise HTTPException(status_code=503, detail=f'Not authenticated on Aranda instance yet, retry again later')