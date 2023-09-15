from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm
from .ImageController import OCR_TEST_IMG
from django.http import JsonResponse
from django.http import FileResponse
from django.conf import settings
def my_view(request):
    print(f"Great! You're using Python 3.6+. If you fail here, use the right version.")
    message = 'Upload as many files as you want!'
    # Handle file upload
    if request.method == 'POST':
        newdoc = Document(docfile=request.FILES['teach_file'])
        newdoc.save()
        newdoc2 = Document(docfile=request.FILES['student_file'])
        newdoc2.save()
        
        filename1 = request.FILES['teach_file']
        result1 = OCR_TEST_IMG(filename1.name)
        filename2 = request.FILES['student_file']
        result2 = OCR_TEST_IMG(filename2.name)
        
        # Redirect to the document list after POST
        data = {
            'result1' : result1,
            'result2' : result2,
            'url1' : filename1.name,
            'url2' : filename2.name
            }
        return JsonResponse(data)
 
    else:
        filename = request.GET.get('filename')
        img_path = settings.MEDIA_ROOT + '\\download\\' + filename
        response = FileResponse(open(img_path, 'rb'), content_type='image/png')  # Adjust content_type as needed
        return response 
