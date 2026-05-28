from rest_framework.response import Response


def success_response(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})
