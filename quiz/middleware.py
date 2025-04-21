from django.http import JsonResponse
from rest_framework.response import Response
from django.utils.deprecation import MiddlewareMixin

class Force200Middleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)

            if response.status_code != 200:
                message = getattr(response, 'reason_phrase', 'An error occurred')
                data = {}

                # DRF response might have .data
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
            # Catch unhandled Python errors
            return JsonResponse({
                "type": "error",
                "message": str(e),
                "data": {}
            }, status=200)
