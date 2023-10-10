from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import IntegrityError

def signingAdmin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('homeAdmin')
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('signingAdmin')
    else:
        return render(request, 'login.html')

def logoutAdmin(request):
    logout(request)
    return redirect('signingAdmin')

def homeAdmin(request):
    if request.user.is_authenticated:
        students_count = Student.objects.count()
        category_count = Category.objects.count()
        vote_count = Vote.objects.count()
        candidate_count = Candidate.objects.count()
        context={
            'students_count':students_count,
            'category_count':category_count,
            'vote_count':vote_count,
            'candidate_count':candidate_count
            }
        return render(request, "index.html", context)
    else:
        messages.info(request, 'You are not administrator')
        return redirect('signingAdmin')

def categoryVoting(request):
    vote_category = Category.objects.all()
    success_message = ""

    return render(request, "voting_category.html", {'vote_category': vote_category, 'success_message': success_message})

def viewVots(request, category_id):
    try:
        category = Category.objects.get(categoryId=category_id)
    except Category.DoesNotExist:
        category = None

    if category:
        candidates = Candidate.objects.filter(category=category)

        candidate_votes = {}

        for candidate in candidates:
            votes_count = Vote.objects.filter(category=category, candidate=candidate).count()
            candidate_votes[candidate] = votes_count
        sorted_candidates = sorted(candidate_votes.items(), key=lambda x: x[1], reverse=True)

        return render(request, "voting_result.html", {'category': category, 'sorted_candidates': sorted_candidates})
    else:
        return render(request, "category_not_found.html") 

@csrf_exempt
def ussdapp(request):
    if request.method == 'POST':
        session_id = request.POST.get("sessionId", None)
        service_code = request.POST.get("serviceCode", None)
        phone_number = request.POST.get("phoneNumber", None)
        text = request.POST.get("text")
        level = text.split('*')
        response = ""

        if text == '':
            # Initial menu
            response = "CON Welcome to UR voting\n"
            response += "1. Continue as student\n"
            response += "2. Exit"
        elif level[0] == '1' and len(level) == 1:
            # Student registration number input
            response = "CON Enter Registration Number:\n"
        elif level[0] == '1' and len(level) == 2:
            # Validate registration number
            reg_number = level[1]
            if Student.objects.filter(regNumber=reg_number).exists():
                # Valid student, proceed to category selection
                response = "CON Choose category to vote:\n"
                categories = Category.objects.all()
                for idx, category in enumerate(categories, start=1):
                    response += f"{idx}. {category.categoryName}\n"
                response += f"{len(categories) + 1}. Back"
            else:
                # Invalid student, prompt to enter registration number again
                response = "CON Invalid registration number. Enter Registration Number:\n"
        elif level[0] == '1' and len(level) == 3:
            # Category selection
            reg_number = level[1]
            category_idx = int(level[2]) - 1
            response = "CON Choose candidate to vote:\n"
            categories = Category.objects.all()
            if 0 <= category_idx < len(categories):
                category = categories[category_idx]
                candidates = Candidate.objects.filter(category=category)
                for idx, candidate in enumerate(candidates, start=1):
                    response += f"{idx}. {candidate.student.name}\n"
                response += f"{len(candidates) + 1}. Back"
            else:
                response = "END Invalid category selection."
        elif level[0] == '1' and len(level) == 4:
            # Voting
            reg_number = level[1]
            category_idx = int(level[2]) - 1
            candidate_idx = int(level[3]) - 1
            categories = Category.objects.all()

            if 0 <= category_idx < len(categories):
                category = categories[category_idx]
                candidates = Candidate.objects.filter(category=category)

                if 0 <= candidate_idx < len(candidates):
                    selected_candidate = candidates[candidate_idx]
                    reg_number = level[1]
                    user, created = Student.objects.get_or_create(regNumber=reg_number)

                    # Check if the student has already voted in this category
                    if not Vote.objects.filter(student=user, category=category).exists():
                        # Create a new Vote object
                        vote = Vote(student=user, category=category, candidate=selected_candidate, vots="1")
                        vote.save()
                        response = "END Thank you for voting!"
                    else:
                        response = "END You have already voted in this category."
                else:
                    response = "END Invalid candidate selection."
            else:
                response = "END Invalid category selection."
        else:
            response = "END Thank you for using our app."

        return HttpResponse(response)
    return HttpResponse('Welcome')
