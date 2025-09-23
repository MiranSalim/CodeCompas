# app/utils/jwt_utils.py

def set_jwt_cookie(resp, access_token: str):
    """
    Zet JWT in een HttpOnly cookie zodat frontend hem automatisch meestuurt.
    """
    resp.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,  # in productie: True (werkt alleen met HTTPS)
        samesite="Lax"
    )
    return resp
