from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from .models import (
    Profile, Pet, PetType,
    PetMedicalHistory, PetReport, PetAdoption, Notification
)
from .serializers import (
    ProfileSerializer, PetTypeSerializer, PetSerializer,
    PetMedicalHistorySerializer, PetReportSerializer,
    PetAdoptionSerializer, NotificationSerializer, LoginSerializer, LostPetRequestSerializer, AdminNotificationSerializer,
      PetReportListSerializer, PetAdoptionListSerializer, AdminApprovalSerializer, UserPetReportSerializer,
        UserAdoptionRequestSerializer, AdminUserSerializer,AdminPetReportSerializer
)

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from django.conf import settings
import jwt
from django.db import transaction
from .models import Notification
# -------------------------
# PetType ViewSet
# -------------------------
class PetTypeViewSet(viewsets.ModelViewSet):
    queryset = PetType.objects.all().order_by("id")
    serializer_class = PetTypeSerializer


# -------------------------
# Profile ViewSet
# -------------------------
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(modified_by=user)

    # ✅ GET /api/profiles/profile_details/
    @action(detail=False, methods=['get'], url_path='profile_details')
    def profile_details(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(email=user.email)
        except Profile.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------
# Pet ViewSet
# -------------------------
# class PetViewSet(viewsets.ModelViewSet):
#     queryset = Pet.objects.all().order_by("id")
#     serializer_class = PetSerializer
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [IsAuthenticated]  # ✅ Requires auth

#     def perform_create(self, serializer):
#         user = self.request.user if self.request.user.is_authenticated else None
#         serializer.save(created_by=user, modified_by=user)

#     def perform_update(self, serializer):
#         user = self.request.user if self.request.user.is_authenticated else None
#         serializer.save(modified_by=user)

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all().order_by("id")
    serializer_class = PetSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]  # ✅ Requires auth

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # ✅ pass request to serializer
        return context

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(modified_by=user)



# -------------------------
# PetMedicalHistory ViewSet
# -------------------------
class PetMedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = PetMedicalHistory.objects.all().order_by("id")
    serializer_class = PetMedicalHistorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)


# -------------------------
# PetReport ViewSet
# -------------------------
class PetReportViewSet(viewsets.ModelViewSet):
    queryset = PetReport.objects.all().order_by("id")
    serializer_class = PetReportSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(modified_by=user)


# -------------------------
# PetAdoption ViewSet
# -------------------------
class PetAdoptionViewSet(viewsets.ModelViewSet):
    queryset = PetAdoption.objects.all().order_by("id")
    serializer_class = PetAdoptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(modified_by=user)


# -------------------------
# Notification ViewSet
# -------------------------
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("id")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user, modified_by=user)

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        try:
            notification = self.get_object()
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        
        notification.is_read = True
        notification.save()
        
        # Return the updated notification data
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------
# Register API
# -------------------------

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Profile registered successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# -------------------------
# Login API with JWT
# -------------------------
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        raw_password = serializer.validated_data["password"]

        try:
            user = Profile.objects.get(email=email)
        except Profile.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if check_password(raw_password, user.password):
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            access_token = str(refresh.access_token)

            return Response({
                "refresh_token": str(refresh),
                "access_token": access_token,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "detail": "Login successful"
            })

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# -------------------------
# LostPetRequestAPIView
# -------------------------
class LostPetRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user  # Profile object

        data = request.data
        
        # Parse JSON data from FormData
        import json
        try:
            pet_data = json.loads(data.get("pet", "{}"))
            report_data = json.loads(data.get("report", "{}"))
            medical_history_data = json.loads(data.get("medical_history", "{}")) if data.get("medical_history") else None
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON data"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not pet_data or not report_data:
            return Response(
                {"error": "Pet and Report data are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle pet image
        pet_image = request.FILES.get('pet_image')
        print(f"Pet image received: {pet_image}")  # Debug log
        if pet_image:
            pet_data['image'] = pet_image

        # 1️⃣ Create Pet
        pet_serializer = PetSerializer(data=pet_data, context={"request": request})
        if pet_serializer.is_valid():
            pet = pet_serializer.save(created_by=user, modified_by=user)
            print(f"Pet created with image: {pet.image}")  # Debug log
        else:
            print("Pet serializer errors:", pet_serializer.errors)  # Debug logging
            return Response({"pet": pet_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Handle report image (use same image as pet for now)
        if pet_image:
            report_data['image'] = pet_image

        # 2️⃣ Create PetReport
        report_serializer = PetReportSerializer(data=report_data, context={"request": request})
        if report_serializer.is_valid():
            report = report_serializer.save(user=user, pet=pet, created_by=user, modified_by=user)
            print(f"Report created with image: {report.image}")  # Debug log
        else:
            return Response({"report": report_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ Create PetMedicalHistory (if vaccinated or diseased)
        if pet.is_vaccinated or pet.is_diseased:
            medical_serializer = PetMedicalHistorySerializer(
                data=medical_history_data,
                context={"request": request, "pet": pet}  # pass pet in context
            )
            if medical_serializer.is_valid():
                medical_serializer.save()  # pet and user are already in create() via context
            else:
                return Response(
                    {"medical_history": medical_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 4️⃣ Create Notification for Admin
         # 4️⃣ Create Notification for Admin
        try:
            admin_user = Profile.objects.get(is_superuser=True)
        except Profile.DoesNotExist:
            admin_user = None

        # Create the notification and explicitly set the admin as the receiver
        notification = Notification.objects.create(
            sender=user,
            receiver=admin_user, # 👈 SET THE RECEIVER
            content=f"New lost pet reported: {pet.name}",
            pet=pet,
            report=report
        )

        return Response({
            "message": "Lost pet request submitted successfully",
            "pet_id": pet.id,
            "report_id": report.id,
            "notification_id": notification.id
        }, status=status.HTTP_201_CREATED)
    

    def get(self, request):
        user = request.user  

        # ✅ Step 2: filter Lost pets whose reports are Accepted
        reports = PetReport.objects.filter(
            pet_status="Lost",
            report_status="Accepted"
        )

        data = []
        for report in reports:
            data.append({
                "report_id": report.id,
                "report_status": report.report_status,
                "pet_status": report.pet_status,
                "image": report.image.url if report.image else None,
                "pet": {
                    "id": report.pet.id,
                    "name": report.pet.name,
                    "pet_type": str(report.pet.pet_type) if report.pet.pet_type else None,
                    "breed": report.pet.breed,
                    "age": report.pet.age,
                    "color": report.pet.color,
                }
            })

        return Response({"lost_pets": data}, status=status.HTTP_200_OK)


# -------------------------
# AdminNotificationsAPIView
# -------------------------
class AdminNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Only superusers can access
        if not user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Filter for notifications where the receiver is the current superuser
        notifications = Notification.objects.filter(receiver=user).order_by("-created_at")
        
        # Use the serializer to handle the data conversion automatically
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({"notifications": serializer.data}, status=status.HTTP_200_OK)
    


# -------------------------
# Pets List API
# -------------------------
class PetsListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        tab = request.query_params.get("tab")
        if not tab:
            return Response({"error": "Tab parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        data = []

        if tab.lower() == "lost":
            reports = PetReport.objects.filter(pet_status="Lost", report_status="Accepted")
            data = PetReportSerializer(reports, many=True, context={"request": request}).data

        elif tab.lower() == "found":
            reports = PetReport.objects.filter(pet_status="Found", report_status="Accepted")
            data = PetReportSerializer(reports, many=True, context={"request": request}).data

        elif tab.lower() == "adopt":
            adoptions = PetAdoption.objects.filter(status="Approved")
            data = PetAdoptionListSerializer(adoptions, many=True, context={"request": request}).data

        else:
            return Response({"error": "Invalid tab value"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"results": data}, status=status.HTTP_200_OK)


# -------------------------
# Admin Approval API
# -------------------------
class AdminApprovalAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users

    def post(self, request):
        # ✅ Superuser check
        if not request.user.is_superuser:
            return Response(
                {"error": "Only admin can approve or reject requests"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdminApprovalSerializer(data=request.data)
        if serializer.is_valid():
            request_type = serializer.validated_data["request_type"]
            pet_id = serializer.validated_data["pet_id"]
            action = serializer.validated_data["action"]

            # LOST or FOUND
            if request_type in ["lost", "found"]:
                pet_status = "Lost" if request_type == "lost" else "Found"
                try:
                    report = PetReport.objects.get(pet__id=pet_id, pet_status=pet_status)
                    report.report_status = "Accepted" if action == "approve" else "Rejected"
                    report.save()

                    # Notification with receiver
                    Notification.objects.create(
                        sender=request.user,                     # Admin
                        receiver=report.user,                    # ← NEW: user who created the report
                        content=f"Your {request_type} pet request is {report.report_status.lower()}",
                        pet=report.pet,
                        report=report
                    )
                    return Response(
                        {"message": f"{request_type.capitalize()} pet request {report.report_status.lower()} successfully"},
                        status=status.HTTP_200_OK
                    )
                except PetReport.DoesNotExist:
                    return Response({"error": "Pet report not found"}, status=status.HTTP_404_NOT_FOUND)

            # ADOPTION
            elif request_type == "adopt":
                try:
                    adoption = PetAdoption.objects.get(pet__id=pet_id)
                    adoption.status = "Approved" if action == "approve" else "Rejected"
                    adoption.save()

                    # Notification with receiver
                    Notification.objects.create(
                        sender=request.user,                      # Admin
                        receiver=adoption.requestor,             # ← NEW: user who requested adoption
                        content=f"Your adoption request is {adoption.status.lower()}",
                        pet=adoption.pet
                    )
                    return Response(
                        {"message": f"Adoption request {adoption.status.lower()} successfully"},
                        status=status.HTTP_200_OK
                    )
                except PetAdoption.DoesNotExist:
                    return Response({"error": "Adoption request not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------
# Show Notifications API
# -------------------------
class UserNotificationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get logged-in user

        # Get all notifications for this user, order by latest
        notifications = Notification.objects.filter(receiver=user).order_by('-created_at')

        serializer = NotificationSerializer(notifications, many=True, context={"request": request})
        return Response({"notifications": serializer.data}, status=status.HTTP_200_OK)



# -------------------------
# User Requests List API
# -------------------------
class UserRequestsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user  # Already Profile because Profile is your AUTH_USER_MODEL

        # fetch reports created by this profile
        reports = PetReport.objects.filter(user=profile)

        # fetch adoption requests made by this profile
        adoptions = PetAdoption.objects.filter(requestor=profile)

        report_data = UserPetReportSerializer(reports, many=True).data
        adoption_data = UserAdoptionRequestSerializer(adoptions, many=True).data

        return Response({
            "reports": report_data,
            "adoptions": adoption_data
        }, status=status.HTTP_200_OK)




class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated]  # must be logged in

    def get(self, request):
        user = request.user

        # ✅ Only superusers can access
        if not user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        users = Profile.objects.all()
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        user = request.user

        if not user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        try:
            target_user = Profile.objects.get(id=user_id)
        except Profile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserSerializer(target_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = request.user

        if not user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        try:
            target_user = Profile.objects.get(id=user_id)
        except Profile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        target_user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
    


class AdminPetReportsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        reports = PetReport.objects.all().order_by("-created_date")
        serializer = AdminPetReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPetReportDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, report_id):
        if not request.user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        try:
            report = PetReport.objects.get(id=report_id)
        except PetReport.DoesNotExist:
            return Response({"detail": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")  # "approve" or "reject"
        if action == "approve":
            report.report_status = "Accepted"
        elif action == "reject":
            report.report_status = "Rejected"
        else:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        report.save()
        return Response({"message": f"Report {action}d successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, report_id):
        if not request.user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        try:
            report = PetReport.objects.get(id=report_id)
        except PetReport.DoesNotExist:
            return Response({"detail": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

        report.delete()
        return Response({"message": "Report deleted successfully"}, status=status.HTTP_200_OK)
    

class AdminUnreadNotificationCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        # Filter for notifications where the receiver is the current superuser
        unread_count = Notification.objects.filter(is_read=False, receiver=request.user).count()
        
        return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
    
class AdminLostPetRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ Only allow admin
        if not request.user.is_superuser:
            return Response(
                {"error": "Only admin can view lost pet requests"},
                status=status.HTTP_403_FORBIDDEN
            )

        reports = PetReport.objects.filter(pet_status="Lost").select_related("pet")

        data = []
        for report in reports:
            data.append({
                "report_id": report.id,
                "report_status": report.report_status,
                "pet_status": report.pet_status,
                "image": report.image.url if report.image else None,
                "pet": {
                    "id": report.pet.id,
                    "name": report.pet.name,
                    "pet_type": str(report.pet.pet_type) if report.pet.pet_type else None,
                    "breed": report.pet.breed,
                    "age": report.pet.age,
                    "color": report.pet.color,
                }
            })

        return Response({"lost_pets": data}, status=status.HTTP_200_OK)


class AdminFoundPetRequestsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ Only allow admin
        if not request.user.is_superuser:
            return Response(
                {"error": "Only admin can view lost pet requests"},
                status=status.HTTP_403_FORBIDDEN
            )

        reports = PetReport.objects.filter(pet_status="Found").select_related("pet")

        data = []
        for report in reports:
            data.append({
                "report_id": report.id,
                "report_status": report.report_status,
                "pet_status": report.pet_status,
                "image": report.image.url if report.image else None,
                "pet": {
                    "id": report.pet.id,
                    "name": report.pet.name,
                    "pet_type": str(report.pet.pet_type) if report.pet.pet_type else None,
                    "breed": report.pet.breed,
                    "age": report.pet.age,
                    "color": report.pet.color,
                }
            })

        return Response({"found_pets": data}, status=status.HTTP_200_OK)


class AdminManageReportStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, report_id):
        if not request.user.is_superuser:
            return Response(
                {"error": "Only admin can update report status"},
                status=status.HTTP_403_FORBIDDEN
            )

        report_status = request.data.get("report_status")
        if report_status not in dict(REPORT_STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = PetReport.objects.get(id=report_id)
            report.report_status = report_status
            report.save()

            # Notify user
            Notification.objects.create(
                sender=request.user,
                receiver=report.user,
                content=f"Your pet report status changed to {report_status.lower()}",
                pet=report.pet,
                report=report
            )

            return Response(
                {"message": f"Report status updated to {report_status}"},
                status=status.HTTP_200_OK
            )
        except PetReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
