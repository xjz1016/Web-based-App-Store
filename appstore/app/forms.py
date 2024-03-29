from django import forms
from app.models import App, Review
from django.core.files.uploadedfile import InMemoryUploadedFile
from app.humanize import naturalsize

# https://docs.djangoproject.com/en/2.1/topics/http/file-uploads/
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
# https://stackoverflow.com/questions/32007311/how-to-change-data-in-django-modelform
# https://docs.djangoproject.com/en/2.1/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other

# Create the form class.
class CreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'

    class Meta:
        model = App
        fields = ['app_name', 'size', 'version', 'category', 'picture',
    'language', 'price']

    # Validate the size of the picture
    def clean(self) :
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None : return
        if len(pic) > self.max_upload_limit:
            self.add_error('picture', "File must be < "+self.max_upload_limit_text+" bytes")
            
    # Convert uploaded File object to a picture
    def save(self, commit=True) :
        instance = super(CreateForm, self).save(commit=False)

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.picture   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()

        return instance


class ReviewForm(forms.ModelForm):
    # review_text = forms.CharField(required=True, max_length=500, min_length=3, strip=True,
    #         widget=forms.TextInput(attrs={'style': 'height:100px'}), label='comments')
    # stars = forms.IntegerField(max_value=5, min_value=0)
    class Meta:
        model = Review
        fields = ['review_text', 'stars']
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        # self.fields['review_text'] = forms.CharField(required=True, max_length=500, min_length=3, strip=True,
        #     widget=forms.TextInput(attrs={'style': 'height:100px'}), label='comments')
        self.fields['review_text'] = forms.CharField(required=True, max_length=500, min_length=3, strip=True,
             label='comments', widget=forms.Textarea(attrs={'style': 'height:100px'}))
        # self.fields['stars'].widget = forms.IntegerField(max_value=5, min_value=0)
        self.fields['stars'] = forms.IntegerField(max_value=5, min_value=0, label='rating')
