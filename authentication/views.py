from base64 import urlsafe_b64decode
from email import message
from http.client import HTTPResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from project_1 import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, send_mail
from . token import generate_token


import authentication
from project_1.info import EMAIL_HOST_USER

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        # print(username)
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username) or User.objects.filter(email=email):
            messages.error(request, "User already in use please make another username")
            return redirect('signup')
        if len(username) > 15:
            messages.error(request, "Length of the username is too long")
            return redirect('signup')
        if not username.isalnum():
            messages.error(request, "Username can only contain alphanumeric values")
            return redirect('signup')
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('signup')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your Account has been successfully created. We have also sent you a conf email")
        # Welcome email
        subject = "Welcome to our Project website!!"
        message = "Hello" + myuser.first_name + "!! \n" + "Please confim your email address. \n Thank you for visiting our website."
        from_mail = EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_mail, to_list, fail_silently=True)


        # Email conf
        current_site = get_current_site(request)
        email_subject = "conf your emailt @gfg - Django login!!"
        message2 = render_to_string('email_confirmation.html', {

            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser)
        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('signin')
    return render(request, "authentication/signup.html")

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')




def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        # print(username)
        # print(pass1)

        user = authenticate(username=username, password=pass1)

        if user is not None:
            # print(username, pass1)
            # print("user is not none")
            login(request, user)
            fname = user.first_name
            messages.success(request, "Your have successfully logged In.")
            return render(request, "authentication/index.html", {'fname': fname})
        else:
            # print("user is none entered bad credentials")
            messages.error(request, "Bad Credentials")
            return redirect('home')
    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "You have successfully logged Out")
    return render(request, "authentication/signout.html")

