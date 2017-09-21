from django import forms


class UserSignUpForm(forms.Form):
    """
    Basic sign up information of users
    """

    first_name = forms.CharField(label='firstname', max_length=30)
    last_name = forms.CharField(label='lastname', max_length=30)

    email = forms.EmailField(label='email')
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(label='password', max_length=128) 

    
class UserSignInForm(forms.Form):
    """
    Basic sign in information of users
    """

    email = forms.EmailField(label='email')
    password = forms.CharField(label='password', max_length=128)
