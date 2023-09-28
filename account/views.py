from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


from .models import UserBase
from .forms import RegistrationForm
from .token import account_activation_token

# Create your views here.

@login_required
def dashboard(request):
    return render(request,'account/user/dashboard.html')

def account_register(request):

    # if request.user.is_authenticated:
    #     return redirect('account:dashboard')
    
    if request.method == "POST":
        # Collect the data from the form
        registrationForm = RegistrationForm(request.POST)
        if registrationForm.is_valid():
            user = registrationForm.save(commit=False)
            # cleaned_data to save from injecting some sql code
            user.email = registrationForm.cleaned_data['email']
            user.set_password = registrationForm.cleaned_data['password']
            user.is_active = False # we want to activate after he accepts the email
            user.save()

            # setup email
            current_site = get_current_site(request)
            subject = 'Activate your Account'
            # render html message in the email
            message = render_to_string('account/registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return HttpResponse('registered successfully and activation sent')
        else:
            return HttpResponse('wrong')
    else:
        registerForm = RegistrationForm()
    return render(request, 'account/registration/register.html', {'form': registerForm})



def account_activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserBase.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user,token):
        user.is_active = True  # activate the user
        user.save()
        login(request, user)   # login the user
        return redirect('account:dashboard')
    else:
        return render(request, 'account/registration/activation_invalid.html')

