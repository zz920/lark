from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from users.forms import UserSignUpForm, UserSignInForm
from users.models import LarkUser as User


def user_signup(request):

    if request.method == "POST": 
        userform = UserSignUpForm(request.POST)
        if userform.is_valid():
            user = User.objects.create_user(**userform.cleaned_data)            
            user.save()
            return redirect('/user/signin') 
        else:
            raise Exception(userform._errors)

    return render_to_response("user_signup.html")


def user_signin(request):

    if request.method == "POST":
        userform = UserSignInForm(request.POST)
        if userform.is_valid():
            user = authenticate(request, **userform.cleaned_data) 
            if user is not None:
                login(request, user)
                # need redirect to user desktop
                # return redirect('/filedesk/home')
                return redirect('/user/signup')

    return render_to_response("user_signin.html")


def user_signout(request): 
    logout(request)
    return redirect('/user/signin')
