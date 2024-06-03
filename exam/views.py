from httpx import request
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
import json
import time
from exam.openai_py import *
import threading
import logging

class PakageListView(generics.ListAPIView):
    queryset = Pakage.objects.all()
    serializer_class = PakageSerializer
    
    
    
class ExamDetailPageView(APIView):
    serializer_class = PakageSerializer

    def get(self, request, id):
        try:
            pakage = Pakage.objects.get(id=id)
            serializer = self.serializer_class(pakage)
            return Response(serializer.data)
        except Pakage.DoesNotExist:
            return Response({"detail": "Pakage not found."}, status=status.HTTP_404_NOT_FOUND)
        
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    if request.method == 'POST':
        user = request.user  # get the logged-in user
        exam_id = request.data.get('exam_id')
        order_amounts = request.data.get('order_amounts')
        coupon = request.data.get('coupon')
        paypal_payment_id = request.data.get('paypal_payment_id')
        
        try:
            package = Pakage.objects.get(id=exam_id)
            
        except Pakage.DoesNotExist:
            return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Initialize discount variables
        discount_amount = 0
        affiliate_instance = None

        # Check if coupon code is provided and valid
        if coupon:
            affiliate_instance = affiliate.objects.get(affiliate_code=coupon)
            discount_amount = package.price * 0.10  # Assume 10% discount for valid affiliate code
            order_amounts = package.price - discount_amount  # Apply discount
        
        # Create the order
        order = Order.objects.create(
            user=user,
            package=package,
            total_amount=order_amounts,
            payment_id=paypal_payment_id  # Store the PayPal payment ID in the order
        )
        
        # Create the payment
        payment = Payment.objects.create(
            order=order,
            payment_method='paypal',
            payment_id=paypal_payment_id,
            amount=order_amounts
        )
        
        # Create the OrderPackage (assuming you want to associate the package with the order)
        OrderPakage.objects.create(
            order=order,
            pakage=package,
            quantity=1,
            price=package.price
        )
        if affiliate_instance:
                # Calculate commission (40% of the discount amount)
                commission_amount = order_amounts  * 0.40

                # Create affiliate earning record
                affiliate_earning.objects.create(
                    affiliate_account_id=affiliate_instance.id,
                    order=order,
                    order_amunt=order_amounts,
                    comision_amunt=commission_amount
                )
                affiliate_instance.total_order += 1
                affiliate_instance.save()
        
        # Serialize the order
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_account(request):
    user = request.user

    # Fetch orders for the logged-in user
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # Serialize the data
    order_serializer = OrderSerializer(orders, many=True)

    # Return the serialized data
    return Response({
        'orders': order_serializer.data,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    user = request.user
    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    payments = Payment.objects.filter(order=order)
    active_packages = Pakage.objects.filter(orderpakage__order=order)

    order_serializer = OrderSerializer(order)
    payment_serializer = PaymentSerializer(payments, many=True)
    package_serializer = PakageSerializer(active_packages, many=True)

    return Response({
        'order': order_serializer.data,
        'payments': payment_serializer.data,
        'active_packages': package_serializer.data,
    })
    
    
    
def order_package_detail(request, pk):
    try:
        order_package = OrderPakage.objects.get(order=pk)
        # Check if the order belongs to the current user
        if order_package.order.user != request.user:
            return JsonResponse({'error': 'Unauthorized access to OrderPakage'}, status=403)
        
        active_packages = Pakage.objects.filter(orderpakage__order=pk)
        order = Order.objects.get(id=pk)
        e = Exam.objects.filter(order=order)
        exam_seralize = ExamSerializerL(e, many=True)
        order_serializer = OrderSerializer(order)
        serializer = OrderPakageSerializer(order_package)
        package_serializer = PakageSerializer(active_packages, many=True)

        return JsonResponse({
            'order_pakage':serializer.data,
            'packages':package_serializer.data,
            'order_serializer':order_serializer.data,
            'exam_seralize':exam_seralize.data,
        })
    except OrderPakage.DoesNotExist:
        return JsonResponse({'error': 'OrderPakage not found'}, status=404)

from at import *
import random

def create_exam_logic(request, package_id):
    try:
        print("start work")
        order_package = OrderPakage.objects.get(order=package_id)
        
        # Check if the order package exists and has available exam count
        if order_package.Exam_count <= 0:
            return JsonResponse({'message': 'Maximum exam count reached for this package'}, status=400)
        
        questions = Package_Qestion.objects.filter(package=order_package.pakage)
        
        print(questions)
        if not questions:
            print("No questions available for the exam")
            return JsonResponse({'message': 'No questions available for the exam'}, status=400)
        
        if len(questions) < 3:
            print("Not enough questions available for the exam")
            return JsonResponse({'message': 'Not enough questions available for the exam'}, status=400)
        
        # Randomly select 10 questions
        selected_questions = random.sample(list(questions), 3)
        print(selected_questions)
        current_time = timezone.now()  # Current time
        
        # Create the exam
        exam = Exam.objects.create(
            title=f"{order_package.order.order_number} {current_time} Batch 1",
            order=order_package.order,
            pakage=order_package.pakage,
        )
        
        order_package.Exam_count -= 1
        order_package.save()

        # Update OrderPakageUseCount model
        OrderPakageUseCount.objects.create(
            order=order_package,
            total_exam_crated=1
        )

        # Create question and answer objects for the selected questions
        for question in selected_questions:
            question_obj = Qestion.objects.create(
                exam=exam,
                question=question.question,
                correct_answer=question.correct_answer
            )
            
            # Get answers for the question
            answers = Package_Answer.objects.filter(question=question)
            
            # Create the answer objects
            for answer in answers:
                Answer.objects.create(
                    question=question_obj,
                    answer=answer.answer
                )

        return JsonResponse({'success': 'Exams created successfully'}, status=201)
    except OrderPakage.DoesNotExist:
        return JsonResponse({'message': 'Order package not found'}, status=404)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'An error occurred while creating the exam'}, status=500)

def parse_docx(file_path):
    questions = []
    current_question = {}

    # Open the .docx file
    doc = docx.Document(file_path)

    for paragraph in doc.paragraphs:
        line = paragraph.text.strip()

        # Check if the line starts with "question:"
        if line.startswith("question:"):
            # If a question is already being processed, add it to the list
            if current_question:
                questions.append(current_question)
                current_question = {}

            # Extract the question text and remove the "question:" prefix
            current_question["question"] = line.replace("question:", "").strip()
        # Check if the line starts with "options:"
        elif line.startswith("options:"):
            # Extract the options list and remove the "options:" prefix
            options = line.replace("options:", "").strip()
            # Remove the leading and trailing brackets, and split the options into a list
            current_question["options"] = [option.strip().strip("[]'") for option in options.split(",")]
        # Check if the line starts with "answer:"
        elif line.startswith("answer:"):
            # Extract the answer and remove the "answer:" prefix
            current_question["answer"] = line.replace("answer:", "").strip()

    # Add the last question to the list
    if current_question:
        questions.append(current_question)

    return questions


def package_create_exam_logicss(package_id):
    print("page all")
    print("page all")
    print("page all")
    try:
        order_package = Pakage.objects.get(id=package_id)
        
        obj = order_package.docx.path
        question_chunks = parse_docx(obj)

        # Group questions into chunks of 100 (not needed for this demonstration)
        question_batches = [question_chunks[i:i + 100] for i in range(0, len(question_chunks), 100)]

        for batch_index, question_batch in enumerate(question_batches):
            current_time = datetime.now().strftime('%H:%M:%S')  # Format: Hours:Minutes:Seconds
            # Create the exam
           

            package_create_single_examsss(question_batch, order_package)
        
        return JsonResponse({'success': 'Exams created successfully'}, status=201)
    
    except OrderPakage.DoesNotExist:
        return JsonResponse({'error': 'Order package not found'}, status=404)


def package_create_exam_logic(package_id):
    print("page all")
    print("page all")
    print("page all")
    try:
        order_package = Pakage.objects.get(id=package_id)
        
        obj = order_package.pdf.path

 
        # Split the questions text into individual questions
        # question_chunks = main(obj)
        question_chunks = questions_texts

        # Group questions into chunks of 100 (not needed for this demonstration)
        question_batches = [question_chunks[i:i + 100] for i in range(0, len(question_chunks), 100)]

        for batch_index, question_batch in enumerate(question_batches):
            current_time = datetime.now().strftime('%H:%M:%S')  # Format: Hours:Minutes:Seconds
            # Create the exam
           

            package_create_single_exam(question_batch, order_package)
        
        return JsonResponse({'success': 'Exams created successfully'}, status=201)
    
    except OrderPakage.DoesNotExist:
        return JsonResponse({'error': 'Order package not found'}, status=404)
    
def package_create_single_examsss(question_list, order_package):
    current_time = datetime.now().strftime('%H:%M:%S')  # Format: Hours:Minutes:Seconds
    logging.info('Generating exam at %s', current_time)
    logging.info('Questions list: %s', question_list)

    for question_data in question_list:
        try:
            # Extract and clean the question text
            question_text = question_data.get("question")
            
            # Extract the correct answer
            correct_answer_text = question_data.get("answer")
            
            # Extract options
            options = question_data.get("options", [])
            
            if question_text and correct_answer_text and options:
                # Create the question object
                question_obj = Package_Qestion.objects.create(
                    package=order_package,
                    question=question_text,
                    correct_answer=correct_answer_text
                )
                
                # Create the answer objects
                for answer_text in options:
                    Package_Answer.objects.create(
                        question=question_obj,
                        answer=answer_text.strip()
                    )
            else:
                logging.warning(f"Incomplete question data: {question_data}")
        
        except Exception as e:
            logging.error(f"Error processing question: {question_data}, Error: {e}")

def package_create_single_exam(question_list, order_package):
    current_time = datetime.now().strftime('%H:%M:%S')  # Format: Hours:Minutes:Seconds
    logging.info('Generating exam at %s', current_time)
    logging.info('Questions list: %s', question_list)

    for question_data in question_list:
        try:
            question_lines = question_data.split("\n")
            
            # Extract and clean the question text
            question_text = None
            for line in question_lines:
                if line.lower().startswith("question: "):
                    question_text = line.split("question: ")[-1].strip()
                    break
            
            # Extract the correct answer
            correct_answer_text = None
            for line in question_lines:
                if line.lower().startswith("answer: "):
                    correct_answer_text = line.split("answer: ")[-1].strip()
                    break
            
            # Extract options
            options_line = None
            for line in question_lines:
                if line.lower().startswith("options:"):
                    options_line = line
                    break
            
            if options_line:
                options = options_line.split("options: ")[-1].strip("[]").replace("'", "").split(", ")
            else:
                options = []
            
            if question_text and correct_answer_text and options:
                # Create the question object
                question_obj = Package_Qestion.objects.create(
                    package=order_package,
                    question=question_text,
                    correct_answer=correct_answer_text
                )
                
                # Create the answer objects
                for answer_text in options:
                    Package_Answer.objects.create(
                        question=question_obj,
                        answer=answer_text.strip()
                    )
            else:
                logging.warning(f"Incomplete question data: {question_data}")
        
        except Exception as e:
            logging.error(f"Error processing question: {question_data}, Error: {e}")




def check_coupon_code(request,id):
    if request.method == "GET":
        if affiliate.objects.filter(affiliate_code=id).exists():
            return JsonResponse({"valid": True, "discount": 0.1})  # Assuming a 10% discount
        else:
            return JsonResponse({"valid": False, "error": "Invalid coupon code"})
        
@api_view(['GET'])
@login_required
def get_exam(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
        
        # Check if start_time and end_time are empty, generate them if empty
        if not exam.start_time or not exam.end_time:
            exam.start_time = timezone.now()
            exam.end_time = exam.start_time + timedelta(hours=2)
            exam.save()  # Save the changes to the database
        
        serializer = ExamSerializer(exam, context={'request': request})
        return Response(serializer.data)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
    
    
@login_required
@api_view(['POST'])
def submit_user_answers(request, exam_id):
    if request.method == 'POST':
        answers = request.data.get('answers')

        if not answers:
            return Response({'error': 'No answers provided'}, status=400)

        total_questions = len(answers)
        total_correct = 0

        for answer in answers:
            question_id = answer.get('question_id')
            answer_text = answer.get('answer')

            if not question_id or not answer_text:
                return Response({'error': 'Invalid answer format'}, status=400)

            # Get the exam question or handle if it doesn't exist
            try:
                question = Qestion.objects.get(id=question_id)
            except Qestion.DoesNotExist:
                return Response({'error': f'Question with ID {question_id} not found'}, status=404)

            # Create User_exam object for each answer
            is_correct = answer_text == question.correct_answer
            User_exam.objects.create(
                exam_id=exam_id,
                question=question.question,
                answer=answer_text,
                correct_answer=question.correct_answer,
                is_correct=is_correct
            )

            if is_correct:
                total_correct += 1

        total_incorrect = total_questions - total_correct
        score = (total_correct / total_questions) * 100
        is_pass = score >= 33  # Assuming pass mark is 33 out of 100
        pl = Exam.objects.get(id = exam_id)
        print(pl)
        pl.result = score
        pl.save()
        return Response({
            'message': 'Answers submitted successfully',
            'total_correct': total_correct,
            'total_incorrect': total_incorrect,
            'score': score,
            'is_pass': is_pass
        }, status=200)
    else:
        return Response({'error': 'Invalid request method'}, status=405)

@login_required
def create_affiliate(request,email):
    if request.method == "POST":
        user = request.user
        paypal_address = email
        
        if not paypal_address:
            return JsonResponse({'error': 'PayPal address is required'}, status=400)

        # Create the affiliate instance
        affiliate_instance = affiliate(user=user, paypal_address=paypal_address)
        affiliate_instance.affiliate_code = str(uuid.uuid4())[:8]  # Generate a unique code
        while affiliate.objects.filter(affiliate_code=affiliate_instance.affiliate_code).exists():
            affiliate_instance.affiliate_code = str(uuid.uuid4())[:8]  # Ensure uniqueness
        affiliate_instance.save()

        return JsonResponse({'affiliate_code': affiliate_instance.affiliate_code})

    return JsonResponse({'error': 'Invalid request method'}, status=405)