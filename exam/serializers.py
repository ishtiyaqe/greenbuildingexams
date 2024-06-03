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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['answer'] = representation['answer'].replace("Options: [", "").strip()
        return representation

class QestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True, source='answer_set')

    class Meta:
        model = Qestion
        fields = ['id', 'question', 'answers']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['question'] = representation['question'].replace("Question: ", "").strip()
        
        # Include correct_answer if context flag is set
        if self.context.get('include_correct_answer'):
            representation['correct_answer'] = instance.correct_answer
        
        return representation

class ExamSerializer(serializers.ModelSerializer):
    questions = QestionSerializer(many=True, read_only=True, source='qestion_set')

    class Meta:
        model = Exam
        fields = ['id', 'title', 'result', 'start_time', 'end_time', 'questions']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Pass context to the nested QestionSerializer
        context = self.context.copy()
        context['include_correct_answer'] = bool(instance.result)
        
        # Re-serialize the questions with the updated context
        questions = QestionSerializer(instance.qestion_set.all(), many=True, context=context).data
        representation['questions'] = questions

        return representation

class ExamSerializerL(serializers.ModelSerializer):
    
    class Meta:
        model = Exam
        fields ='__all__'