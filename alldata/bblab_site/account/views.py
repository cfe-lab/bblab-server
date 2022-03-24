from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.utils.http import is_safe_url

from .form import LoginForm

from django.contrib.auth.decorators import login_required

# go to next if it is provided
def redirect_path(request):
    if request.GET.get('next') != None and is_safe_url(request.GET.get('next'), None):
        return request.GET.get('next')
    else:
        return '/django/wiki/'

def v_login(request):
    if request.user.is_authenticated:
        return redirect('/django/wiki/')  # redirect user to wiki page only
    else:
	#TODO: implement brute force protection. --> done? --> yup, its implemented (2019-11-24)
        if request.method == 'POST':
            form_data = request.POST

            # This uses the salt hash method to autheticate & store passwords.
            user = authenticate(request=request, username=form_data['username'], password=form_data['password'])

            # Authenticate and log-in user.
            if user is not None:
                login(request, user)
                return redirect(redirect_path(request))
            else:
                context = { 'form': LoginForm(), 'login_failed': True, 'next': request.GET.get('next'), 
				'site_title': 'log in', 'content_title': 'Bblab Authentication' }
                return render(request, 'login.html', context)
        else:
            # the 'next' entry keeps the next going to the login attempt.
            context = { 'form': LoginForm(), 'login_failed': False, 'next': request.GET.get('next'), 
				'site_title': 'log in', 'content_title': 'Bblab Authentication' }
            return render(request, 'login.html', context)

def v_logout(request):
    if request.user.is_authenticated:
        if request.method == 'POST':  # Is this ok?  Can people just send post requests by accident?
            logout(request)  # logout user
            return redirect(redirect_path(request))
        else:
            context = { 'logout_state': 'verify', 'site_title': 'log out', 
			'content_title': 'Bblab Authentication', 'next': request.GET.get('next') }
            return render(request, 'logout.html', context)
    else:
        context = { 'logout_state': 'logged_out', 'site_title': 'log out', 'content_title': 'Bblab Authentication' }
        return render(request, 'logout.html', context)

@login_required
def v_account(request):
	context = { 'username': request.user.username } 
	return render(request, 'account.html', context)

def v_lockout(request):
	return HttpResponse( "You have failed to log in too many times, please contact an admin." )
