from django.http import JsonResponse

def JR(data, **karg):
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False}, **karg)
