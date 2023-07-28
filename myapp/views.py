from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm
from .ImageController import generate_AI_image
from django.http import JsonResponse
def my_view(request):
    print(f"Great! You're using Python 3.6+. If you fail here, use the right version.")
    message = 'Upload as many files as you want!'
    # Handle file upload
    if request.method == 'POST':
        newdoc = Document(docfile=request.FILES['docfile'])
        newdoc.save()
        filename = request.FILES['docfile']
        ai_img_url = generate_AI_image(filename.name)
        # Redirect to the document list after POST
        data = {
            'result' : ai_img_url
            }
        return JsonResponse(data)
 
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()
    # Render list page with the documents and the form
    context = {'documents': documents, 'form': form, 'message': message}
    return render(request, 'list.html', context)
