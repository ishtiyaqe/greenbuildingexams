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
        print('generate exam 5 times')
        print(package.id)
        thread = threading.Thread(target=create_exam_logic, args=(package.id,))
        thread.start()
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
    
@csrf_exempt
@csrf_exempt
def create_exam(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            print(data)
            package_id = data.get('package_id')
            print(package_id)
            order_package = OrderPakage.objects.get(pakage=package_id)
            
            # Check if the order package exists and has available exam count
            if order_package.Exam_count <= 0:
                return JsonResponse({'message': 'Maximum exam count reached for this package'}, status=400)
            obj = order_package.pakage.pdf.path
            # Construct the full path
            # full_path = "media/" + obj
            # Call the main function with the path
           
            
            current_time = datetime.now().strftime('%H:%M:%S')  # Format: Hours:Minutes:Seconds
            # Create the exam
            exam = Exam.objects.create(
                title = f"{order_package.order.order_number} {current_time}",
                order=order_package.order,
                pakage=order_package.pakage,
                start_time=order_package.order.created_at,  # Start time is the order creation time
            )
            
            # Decrement the exam count for the order package
            order_package.Exam_count -= 1
            order_package.save()
            
            # Update OrderPakageUseCount model
            OrderPakageUseCount.objects.create(
                order=order_package,
                total_exam_crated=1
            )
            
            # questions_text = main(obj)
            questions_text = main('doc.docx')
            print(questions_text)
            # Parse the generated questions and answers
            # Parse the generated questions and answers
            for question_data in questions_text.split("\n\n"):
                question_lines = question_data.split("\n")
                
                # Extract and clean the question text
                question_text = question_lines[0].split("Question: ")[-1].strip()
                
                # Extract the correct answer
                correct_answer_text = question_lines[1].split("Answer: ")[-1].strip()
                
                # Extract options
                options_line = [line for line in question_lines if line.startswith('Options:')][0]
                options = options_line.split("Options: ")[-1].strip("[]").replace("'", "").split(", ")
                
                # Create the question object
                question_obj = Qestion.objects.create(
                    exam=exam,
                    question=question_text,
                    correct_answer=correct_answer_text
                )
                
                # Create the answer objects
                for answer_text in options:
                    Answer.objects.create(
                        question=question_obj,
                        answer=answer_text.strip()
                    )

            return JsonResponse({'success': 'Exam created successfully'}, status=201)
        
        except OrderPakage.DoesNotExist:
            return JsonResponse({'error': 'Order package not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)




def create_exam_logic(package_id):
    print('generate exam 0 times')
    print(package_id)
    # try:
    order_package = OrderPakage.objects.get(pakage=package_id)
    
    # Check if the order package exists and has available exam count
    if order_package.Exam_count <= 0:
        return JsonResponse({'message': 'Maximum exam count reached for this package'}, status=400)
    
    obj = order_package.pakage.pdf.path

    # Generate 500 questions from the uploaded data
    # questions_text = main(obj)
    questions_text = main('doc.docx')
    print(questions_text)

    # Split the questions text into individual questions
    question_chunks = questions_text.split("\n\n")

    # Group questions into chunks of 100
    question_batches = [question_chunks[i:i + 100] for i in range(0, len(question_chunks), 100)]

    for batch_index, question_batch in enumerate(question_batches):
        current_time = datetime.now().strftime('%H:%M:%S')  # Format: Hours:Minutes:Seconds
        # Create the exam
        exam = Exam.objects.create(
            title=f"{order_package.order.order_number} {current_time} Batch {batch_index + 1}",
            order=order_package.order,
            pakage=order_package.pakage,
            start_time=order_package.order.created_at,  # Start time is the order creation time
        )
        order_package.Exam_count -= 1
        order_package.save()
        create_single_exam(order_package, question_batch, exam)
    

    print("Exams created successfully")
    return JsonResponse({'success': 'Exams created successfully'}, status=201)
    
    # except OrderPakage.DoesNotExist:
    #     print("Order package not found")
    #     return JsonResponse({'error': 'Order package not found'}, status=404)

def create_single_exam(order_package, questions_text, exam):
    current_time = datetime.now().strftime('%H:%M:%S')  # Format: Hours:Minutes:Seconds
    logging.info('Generating exam at %s', current_time)
    logging.info('Questions text: %s', questions_text)



    # Decrement the exam count for the order package
    order_package.Exam_count -= 1
    order_package.save()

    # Update OrderPakageUseCount model
    OrderPakageUseCount.objects.create(
        order=order_package,
        total_exam_crated=1
    )

    # Parse the generated questions and answers
    for question_data in questions_text.split("\n\n"):
        question_lines = question_data.split("\n")
        
        # Extract and clean the question text
        question_text = question_lines[0].split("Question: ")[-1].strip()
        
        # Extract the correct answer
        correct_answer_text = question_lines[1].split("Answer: ")[-1].strip()
        
        # Extract options
        options_line = [line for line in question_lines if line.startswith('Options:')][0]
        options = options_line.split("Options: ")[-1].strip("[]").replace("'", "").split(", ")
        
        # Create the question object
        question_obj = Qestion.objects.create(
            exam=exam,
            question=question_text,
            correct_answer=correct_answer_text
        )
        
        # Create the answer objects
        for answer_text in options:
            Answer.objects.create(
                question=question_obj,
                answer=answer_text.strip()
            )



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
        serializer = ExamSerializer(exam)
        return Response(serializer.data)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
    

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