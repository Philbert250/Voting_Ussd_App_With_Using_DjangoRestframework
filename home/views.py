from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import logging
from django.core.mail import send_mail

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import uuid
import json
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from django.db import IntegrityError
import random
from django.core.exceptions import ObjectDoesNotExist


def voterRegister(request):
    students = Student.objects.all()
    success_message = ""
    error_message = ""
    
    if request.method == 'POST':
        regnumber = request.POST['regnumber']
        email = request.POST['email']
        plain_pin = request.POST['pin']
        
        try:
            student = Student.objects.get(regNumber=regnumber)
            
            # Check if the student is already registered as a voter
            if not Voters.objects.filter(student=student).exists():
                hashed_pin = make_password(plain_pin)
                
                new_voter = Voters(
                    student=student,
                    email=email,
                    pin=hashed_pin 
                )
                new_voter.save()
                success_message = "You have registered as a voter successfully."
            else:
                error_message = "You have already registered as a voter."
        except Student.DoesNotExist:
            error_message = "Invalid registration number. Please make sure you are a registered student."
    
    return render(request, "register.html", {'students': students, 'success_message': success_message, 'error_message': error_message})


def forgotPin(request):
    success_message = ""
    error_message = ""
    
    if request.method == 'POST':
        regnumber = request.POST['regnumber']
        email = request.POST['email']
        
        try:
            voter = Voters.objects.get(student__regNumber=regnumber, email=email)
            new_pin = str(random.randint(1000, 9999))
            voter.pin = make_password(new_pin)
            voter.save()

            subject = "UR Voting management system"
            message = f"Your PIN has been reset to {new_pin}. Please remember it."
            from_email = "muhireyves81@gmail.com"  
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)
            success_message = f"Your PIN has been reset. Check your email."
        except ObjectDoesNotExist:
            error_message = "Invalid registration number or email. Please make sure you are a registered voter."
    
    return render(request, "forgot_pin.html", {'success_message': success_message, 'error_message': error_message})

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


def voterRegistered(request):
    voters = Voters.objects.all()
    success_message = ""

    return render(request, "voters.html", {'voters': voters, 'success_message': success_message})

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

        # Retrieve voters who haven't voted in the selected category
        all_voters = Voters.objects.all()
        voters_who_did_not_vote = []

        for voter in all_voters:
            if not Vote.objects.filter(voter=voter, category=category).exists():
                voters_who_did_not_vote.append(voter)

        # Retrieve voters who have voted in the selected category
        voters_who_voted = []

        for vote in Vote.objects.filter(category=category):
            voter = vote.voter
            if voter not in voters_who_voted:
                voters_who_voted.append(voter)

        return render(request, "voting_result.html", {
            'category': category,
            'sorted_candidates': sorted_candidates,
            'voters_who_did_not_vote': voters_who_did_not_vote,
            'voters_who_voted': voters_who_voted
        })
    else:
        return render(request, "category_not_found.html")

import logging

logging.basicConfig(filename='ussdapp.log', level=logging.DEBUG)
logger = logging.getLogger("ussdapp")

@csrf_exempt
def ussdapp(request):
    if request.method == 'POST':
        text = request.POST.get("text")
        level = text.split('*')
        response = ""

        if text == '':
            # Initial menu
            response = "CON Welcome to UR voting\n"
            response += "1. Continue as student\n"
            response += "2. Exit"
        elif level[0] == '1' and len(level) == 1:
            # Voter login: Enter Registration Number
            response = "CON Enter Registration Number:\n"
        elif level[0] == '1' and len(level) == 2:
            try:
                registration_number = level[1]
                student = Student.objects.get(regNumber=registration_number)
                response = "CON Enter your PIN:\n"
            except Student.DoesNotExist:
                response = "END Invalid registration number."
        elif level[0] == '1' and len(level) == 3:
            # Verify PIN and proceed to voting menu
            registration_number = level[1]
            entered_pin = level[2]

            try:
                student = Student.objects.get(regNumber=registration_number)
                voter = Voters.objects.get(student=student)
                if check_password(entered_pin, voter.pin):
                    response = "CON Voting Menu:\n"
                    response += "1. Vote\n"
                    response += "2. Exit\n"
                else:
                    response = "END Invalid PIN."
            except (Student.DoesNotExist, Voters.DoesNotExist):
                response = "END Invalid registration number or PIN."
        elif level[0] == '1' and len(level) == 4:
            # Voting process
            if level[3] == '1':
                # Start the voting process
                response = "CON Choose a category to vote:\n"
                categories = Category.objects.all()
                for idx, category in enumerate(categories, start=1):
                    response += f"{idx}. {category.categoryName}\n"
        elif level[0] == '1' and len(level) == 5:
            # Vote selection
            category_idx = int(level[4]) - 1  # Note the change in index here
            categories = Category.objects.all()
            if 0 <= category_idx < len(categories):
                category = categories[category_idx]
                candidates = Candidate.objects.filter(category=category)
                response = "CON Choose a candidate to vote for:\n"
                for idx, candidate in enumerate(candidates, start=1):
                    response += f"{idx}. {candidate.student.name}\n"
            else:
                response = "END Invalid category selection."
        elif level[0] == '1' and len(level) == 6:
            # Finalize vote
            try:
                category_idx = int(level[4]) - 1  # Note the change in index here
                category = Category.objects.all()[category_idx]
                candidate_idx = int(level[5]) - 1
                candidates = Candidate.objects.filter(category=category)
                selected_candidate = candidates[candidate_idx]

                student = Student.objects.get(regNumber=level[1])
                voter = Voters.objects.get(student=student)
                # Check if the voter has already voted in this category
                if not Vote.objects.filter(voter=voter, category=category).exists():
                    vote = Vote(voter=voter, category=category, candidate=selected_candidate, vots="1")
                    vote.save()
                    response = "END Thank you for voting!"
                else:
                    response = "END You have already voted in this category."
            except (Student.DoesNotExist, Voters.DoesNotExist, Category.DoesNotExist, IndexError):
                response = "END Invalid input."
        else:
            response = "END Thank you for using our app."

        return HttpResponse(response)
    return HttpResponse('Welcome')