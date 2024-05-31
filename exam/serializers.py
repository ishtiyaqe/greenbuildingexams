from rest_framework import serializers
from .models import *



class PakageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pakage
        fields = '__all__'
        



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class OrderPakageSerializer(serializers.ModelSerializer):
    pakage = PakageSerializer()

    class Meta:
        model = OrderPakage
        fields = ['pakage', 'quantity', 'price']




class OrderSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()
    active_packages = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'created_at', 'payment_id', 'order_number', 'user', 'package', 'payments', 'active_packages']

    def get_payments(self, obj):
        payments = Payment.objects.filter(order=obj)
        return PaymentSerializer(payments, many=True).data

    def get_active_packages(self, obj):
        active_packages = Pakage.objects.filter(orderpakage__order=obj)
        return PakageSerializer(active_packages, many=True).data
    
    

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer']

class QestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True, source='answer_set')
    
    class Meta:
        model = Qestion
        fields = ['id', 'question', 'correct_answer', 'answers']

class ExamSerializer(serializers.ModelSerializer):
    questions = QestionSerializer(many=True, read_only=True, source='qestion_set')
    
    class Meta:
        model = Exam
        fields = ['id', 'title', 'start_time', 'end_time', 'questions']

class ExamSerializerL(serializers.ModelSerializer):
    
    class Meta:
        model = Exam
        fields ='__all__'