from django.http import HttpResponse

def index(request):
	return HttpResponse("from views in main.index")

# Create your views here.
