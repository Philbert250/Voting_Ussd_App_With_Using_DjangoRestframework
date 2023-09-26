from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *

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
                    user,create = Student.objects.get_or_create(regNumber=reg_number)

                    # Create a new Vote object
                    vote = Vote(student=user, category=category, candidate=selected_candidate, vots="1")
                    vote.save()
                    response = "END Thank you for voting!"
                else:
                    response = "END Invalid candidate selection."
            else:
                response = "END Invalid category selection."
        else:
            response = "END Invalid input."

        return HttpResponse(response)
    return HttpResponse('Welcome')