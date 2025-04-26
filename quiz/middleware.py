# from django.utils.deprecation import MiddlewareMixin
# from django.http import JsonResponse

# class Force200Middleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Skip middleware for admin, static, and media paths
#         if request.path.startswith('/admin') or request.path.startswith('/static') or request.path.startswith('/media'):
#             return self.get_response(request)

#         # Extract Bearer token from Authorization header
#         auth_header = request.headers.get("Authorization")
#         bearer_token = None
#         if auth_header and auth_header.startswith("Bearer "):
#             bearer_token = auth_header.split("Bearer ")[1].strip()

#         # Determine guest token (from session or headers or bearer token)
#         guest_token = (
#             request.session.get("guest_id") or
#             request.headers.get("Guest-Token") or
#             request.META.get("HTTP_GUEST_TOKEN") or
#             bearer_token  # Assume bearer token might be a guest token
#         )

#         # Restrict specific paths if neither user nor guest token is present
#         restricted_paths = [
#             '/api/private/',  # Example restricted path
#             '/quiz/leader_board/',  # Example restricted path
#         ]
#         if not guest_token and not request.user.is_authenticated:
#             for path in restricted_paths:
#                 if request.path.startswith(path):
#                     return JsonResponse({
#                         "type": "error",
#                         "message": "Authentication or guest token required",
#                         "data": {}
#                     }, status=200)  # Forbidden

#         try:
#             # Process the response for the request
#             response = self.get_response(request)

#             # If the response status code is not 200, wrap it with error details
#             if response.status_code != 200:
#                 message = getattr(response, 'reason_phrase', 'An error occurred')
#                 data = {}

#                 # Check for data inside the response
#                 if hasattr(response, 'data'):
#                     if isinstance(response.data, dict):
#                         message = response.data.get('detail') or str(response.data)
#                         data = response.data
#                     else:
#                         message = str(response.data)

#                 # Return a custom error response with message and data
#                 return JsonResponse({
#                     "type": "error",
#                     "message": message,
#                     "data": data if isinstance(data, dict) else {}
#                 }, status=response.status_code)

#             return response

#         except Exception as e:
#             # Catch all unexpected errors and return a 200 OK response with error message
#             return JsonResponse({
#                 "type": "error",
#                 "message": str(e),
#                 "data": {}
#             }, status=200)  # Internal Server Error (but using 200 as per requirement)



from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

class Force200Middleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip admin, static, media
        if request.path.startswith('/admin') or request.path.startswith('/static') or request.path.startswith('/media'):
            return self.get_response(request)

        # Get bearer token
        auth_header = request.headers.get("Authorization")
        bearer_token = None
        if auth_header and auth_header.startswith("Bearer "):
            bearer_token = auth_header.split("Bearer ")[1].strip()

        # Guest token
        guest_token = (
            request.session.get("guest_id") or
            request.headers.get("Guest-Token") or
            request.META.get("HTTP_GUEST_TOKEN") or
            bearer_token
        )

        # Restricted paths
        restricted_paths = [
            '/api/private/',
            '/quiz/leader_board/',
        ]
        if not guest_token and not request.user.is_authenticated:
            for path in restricted_paths:
                if request.path.startswith(path):
                    return JsonResponse({
                        "type": "error",
                        "message": "Authentication or guest token required",
                        "data": {}
                    }, status=200)

        try:
            # Normal processing
            response = self.get_response(request)

            if response.status_code != 200:
                message = getattr(response, 'reason_phrase', 'An error occurred')
                data = {}

                if hasattr(response, 'data'):
                    if isinstance(response.data, dict):
                        message = response.data.get('detail') or str(response.data)
                        data = response.data
                    else:
                        message = str(response.data)

                return JsonResponse({
                    "type": "error",
                    "message": message,
                    "data": data if isinstance(data, dict) else {}
                }, status=200)

            return response

        except Exception as e:
            return JsonResponse({
                "type": "error",
                "message": str(e),
                "data": {}
            }, status=200)
