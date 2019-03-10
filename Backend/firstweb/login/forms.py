from django import forms
from .models import User, UserProfile
class UserForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput())
    confirm_password=forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email','password')

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password= cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Both password fields should match")
class UserProfileForm(forms.ModelForm):
    YESNO_CHOICES = (('male', 'male'), ('female', 'female'))
    sex = forms.TypedChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect)
    FAVORITE_COLORS_CHOICES=(('red','red'),('blue','blue'))
    favorite_colors = forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple, choices=FAVORITE_COLORS_CHOICES)
    dob = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                 input_formats=('%d/%m/%Y',))

    class Meta:

        model=UserProfile
        fields=('phone','sex','favorite_colors','dob')
class Login(forms.Form):
    username = forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput())
