from django.db import models

# Create your models here.
class Job(models.Model):
    STATUS_CHOICES = (
        ('RUNNING','RUNNING'),
        ('SUCCEEDED','SUCCEEDED'),
        ('FAILED','FAILED'),
        )
    job_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,default='RUNNING') 
    input_data = models.ImageField(upload_to='input_data/', null=True, blank=True)
    output_data = models.ImageField(upload_to='output_data/', null=True, blank=True)
    
    def __str__(self):
        return self.job_id