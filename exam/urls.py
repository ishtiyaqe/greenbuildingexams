from django.urls import path
from .views import *

urlpatterns = [
    path('pakages/', PakageListView.as_view(), name='pakage-list'),
    path('pakage/<int:id>/', ExamDetailPageView.as_view(), name='exam_detail_page'),
    path('create-order/', create_order, name='create_order'),
    path('create-exam/<int:package_id>/', create_exam_logic, name='create_exam'),
    path('myaccount/', my_account, name='my-account'),
    path('order-package/<int:pk>/', order_package_detail, name='order_package_detail'),
    path('check-coupon-code/<str:id>/', check_coupon_code, name='check_coupon_code'),
    path('exams/<int:exam_id>/', get_exam, name='get_exams'),
    path('create_affiliate/<str:email>', create_affiliate, name='create_affiliate'),
    path('user_exams/<int:exam_id>/', submit_user_answers, name='submit_user_answers'),
]
