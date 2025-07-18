from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Job
from .serializer import JobSerializer, LoginSerializer
import threading
from .tasks import process_data_task
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, authenticate
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class RunJobAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        data = request.data
        
        if not data.get('job_id'):
            return Response({
                'status':False,
                'message': f"job_id is required.",
                'data' : {}
            },status=404)
        
        job_id =data.get('job_id')
        
        job = Job.objects.filter(job_id=job_id).exists()
        if job:
            return Response({
            'status':False,
            'message': f"Job {job_id} already exists.",
            'data' : {}
        },status=403)
        
        serializer = JobSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status':True,
                'message': f"Job {job_id} is running.",
                'data' : {}
            },status=200)
        else:
            return Response({
                'status':False,
                'message': f"Something went wrong.",
                'error' : serializer.errors
            },status=401)

    def put(self, request):
        data = request.data
        if not Job.objects.filter(job_id=data.get('job_id')):
            return Response({
                'status':False,
                'message': f"invalid Job.",
                'data' : {}
            }, status=404)
        serializer = JobSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response({
                'status':False,
                'message': f"Something went wrong.",
                'error' : serializer.errors
            }, status=403)
        
class JobStatusAPIView(APIView):
    def get(self,request):
        data = request.data
        
        if not data.get('job_id'):
            return Response({
                'status':False,
                'message': f"job_id is required.",
                'data' : {}
            },status=403)
        
        job_id = data.get('job_id')
        
        job = Job.objects.filter(job_id=job_id)
        if not job.exists():
            return Response({
            'status':False,
            'message': f"Job {job_id} does't exists.",
            'data' : {}
        },status=404)
        
        job_obj = job[0]
        return Response({
            'status':True,
            'message': f"Job {job_id} is {job_obj.status}.",
            'data' : {
                'status' : job_obj.status,
                'input' : str(job_obj.input_data),
                'output' : str(job_obj.output_data),
            }
        },status=200)


class JobStartAPIView(APIView):
    def post(self, request):
        job_id = request.data.get('job_id')

        try:
            job_instance = Job.objects.get(job_id=job_id)
        except Job.DoesNotExist:
            return Response({
                'status': False,
                'message': f"Job with ID {job_id} does not exist.",
            }, status=404)

        serializer = JobSerializer(instance=job_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save() 
            
            thread = threading.Thread(target=process_data_task, args=(job_instance.job_id,))
            thread.start()
            print("Thread started for job:", job_instance.job_id)
            
            response_data = {
                "job_id": str(job_instance.job_id),
                "status": "SUBMITTED" 
            }
            return Response(response_data, status=200)
        
        # If validation fails for other reasons, return the specific errors
        return Response({
            'status': False,
            'message': "Invalid data provided.",
            'errors': serializer.errors
        }, status=400)

class LoginAPI(APIView):
    def post(self, request):
        data = request.data
        if not data.get('username') or not data.get('password'):
            return Response({
            'status': False,
            'message': "username and password is required.",
            'data': {}
            }, status=400)
            
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.data['username'],
                password=serializer.data['password']
            )
            if user is None:
                return Response({
                    "status": False,
                    "message": "Invalid credentials!",
                    "data" : {}
                })     
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "status" : True,
                "message" : "Login credentials reveived!!!",
                "data" : {
                    "token" : token.key
                }
            })
        else:
            return Response({
                "status" : False,
                "message" : "something went wrong.",
                "errors" : serializer.errors
            })