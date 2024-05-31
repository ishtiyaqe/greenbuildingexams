from unittest import result
from django.db import models
from ckeditor.fields import RichTextField 
from embed_video.fields import EmbedVideoField
# Create your models here.
from PIL import Image
import io
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import pre_save
import uuid



def convert_image_to_webp(image):
    if image:
        img = Image.open(image)
        webp_output = io.BytesIO()

        # Convert image to WebP format
        img.save(webp_output, format='WebP')
        webp_output.seek(0)

        # Set the filename extension to .webp
        filename, extension = os.path.splitext(image.name)
        webp_filename = filename + '.webp'

        # Create a new InMemoryUploadedFile object with the WebP data
        webp_file = InMemoryUploadedFile(
            webp_output,
            None,
            webp_filename,
            'image/webp',
            webp_output.tell(),
            None
        )

        return webp_file

    return image


class Pakage(models.Model):
    name = models.CharField(max_length=225, null=True)
    Tags = models.CharField(max_length=225, null=True)
    remove_pakage = models.BooleanField(default=False,null=True)
    old_price = models.IntegerField( null=True,blank=True)
    price = models.IntegerField( null=True)
    sku = models.CharField(unique=True, max_length=225, null=True, blank=True)
    main_image = models.ImageField(upload_to="static/images/pakage/", null=True,blank=True)
    on_homePage = models.BooleanField(default=False)
    shor_des = RichTextField()
    des = RichTextField()
    best_selling = models.BooleanField(blank=True,null=True)
    video = EmbedVideoField(blank=True,null=True)
    pdf = models.FileField(upload_to='static/pdfs/pakage/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return self.name
    # Rest of your fields and methods

    def save(self, *args, **kwargs):
        self.main_image = convert_image_to_webp(self.main_image)
        super().save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            url = self.main_image.url
        except:
            url = ''
        return 

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Pakage, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=255, null=True)
    order_number = models.CharField(max_length=20, unique=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('id').last()
            if last_order:
                last_order_number = int(last_order.order_number.split('-')[1])
                self.order_number = f'ORD-{last_order_number + 1}'
            else:
                self.order_number = 'ORD-1000'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)


class OrderPakage(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    pakage = models.ForeignKey('Pakage', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    Exam_count = models.IntegerField(default=5)

    def __str__(self):
        return f"Order: {self.order.id}, Pakage: {self.pakage.name}"

class OrderPakageUseCount(models.Model):
    order = models.ForeignKey('OrderPakage', on_delete=models.CASCADE)
    total_exam_crated = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Order: {self.order.id}"
    
    
    
class Exam(models.Model):
    title = models.CharField(max_length=80)
    order = models.ForeignKey('Order', on_delete=models.CASCADE,null=True)
    pakage = models.ForeignKey('Pakage', on_delete=models.CASCADE,null=True)
    result = models.IntegerField(null=True,blank=True)
    start_time = models.DateTimeField(null=True,blank=True)
    end_time = models.DateTimeField(null=True,blank=True)

    def save(self, *args, **kwargs):
        # Calculate the end time by adding 2 hours to the start time
        self.end_time = self.start_time + timedelta(hours=2)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Qestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True)
    question = models.CharField(max_length=800,null=True)
    correct_answer = models.CharField(max_length=800)
    def __str__(self):
        return self.question
    
class Answer(models.Model):
    question = models.ForeignKey(Qestion, on_delete=models.CASCADE, null=True)
    answer = models.CharField(max_length=800)


    def __str__(self):
        return f"Answer: {self.answer}"
    
    
class affiliate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    affiliate_code = models.CharField(max_length=255, unique=True, blank=True)  # Ensure unique and allow blank
    total_amunt = models.CharField(max_length=20, default=0)  # Use DecimalField for monetary values
    total_order = models.IntegerField(default=0)  # Use DecimalField for monetary values
    paypal_address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username}"

@receiver(pre_save, sender=affiliate)
def generate_unique_affiliate_code(sender, instance, **kwargs):
    if not instance.affiliate_code:  # Only generate if the field is blank
        instance.affiliate_code = str(uuid.uuid4())[:8]  # Generate a unique code
        while affiliate.objects.filter(affiliate_code=instance.affiliate_code).exists():
            instance.affiliate_code = str(uuid.uuid4())[:8]  # Ensure uniquenes\
                
class affiliate_earning(models.Model):
    PAID = 'paid'
    UNPAID = 'unpaid'
    STATUS_CHOICES = [
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
    ]

    affiliate_account = models.ForeignKey(affiliate, to_field="id", on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True)
    order_amunt = models.CharField(max_length=255)
    comision_amunt = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=UNPAID,
    )

    def __str__(self):
        return f"{self.affiliate_account} - {self.order} - {self.status}"
