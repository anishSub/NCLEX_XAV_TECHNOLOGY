from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

def home(request):
    return render(request, 'pages/home.html')
      
# NEW: Your First API View
@api_view(['GET'])
def hello_api(request):
    data = {
        "message": "Welcome to DocPlus API!",
        "status": "Success",
        "developer": "Anish"
    }
    return Response(data)