from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone

from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Institute
from academics.models import StudentProfile, Batch, AttendanceRecord
from finance.models import FeePayment, FeeInstallment
from .serializers import (
    CustomTokenObtainPairSerializer,
    InstituteSerializer,
    UserSerializer,
)


class DashboardStatsView(APIView):
    """
    The Brain of the ERP. 
    Returns specific data widgets based on the User Role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role
        data = {
            "role": role,
            "username": user.username,
            "widgets": []
        }

        # ------------------------------------------------
        # 1. SUPER ADMIN (Business Owner View)
        # ------------------------------------------------
        if role == User.Roles.SUPER_ADMIN:
            total_institutes = Institute.objects.count()
            total_users = User.objects.count()
            global_revenue = FeePayment.objects.aggregate(Sum('amount'))['amount__sum'] or 0

            data["widgets"] = [
                {"label": "Total Institutes", "value": total_institutes, "color": "blue"},
                {"label": "Total Users", "value": total_users, "color": "green"},
                {"label": "Total Revenue (Global)", "value": f"₹ {global_revenue}", "color": "purple"},
            ]
            data["table_title"] = "Recent Institutes"
            data["table_data"] = list(
                Institute.objects.order_by('-created_at')[:5]
                .values('id', 'name', 'code', 'created_at')
            )

        # ------------------------------------------------
        # 2. INSTITUTE ADMIN (Principal/Manager View)
        # ------------------------------------------------
        elif role == User.Roles.INSTITUTE_ADMIN:
            inst = user.institute
            student_count = StudentProfile.objects.filter(institute=inst).count()
            batch_count = Batch.objects.filter(institute=inst).count()

            today = timezone.now().date()
            today_collection = FeePayment.objects.filter(
                institute=inst, payment_date=today
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            pending_installments = FeeInstallment.objects.filter(
                institute=inst, status='PENDING'
            ).count()

            data["widgets"] = [
                {"label": "Active Students", "value": student_count, "color": "blue"},
                {"label": "Active Batches", "value": batch_count, "color": "orange"},
                {"label": "Today's Collection", "value": f"₹ {today_collection}", "color": "green"},
                {"label": "Fee Defaulters", "value": pending_installments, "color": "red"},
            ]

            data["table_title"] = "Recent Fee Payments"
            payments = FeePayment.objects.filter(institute=inst).select_related(
                'installment__allocation__student__user'
            ).order_by('-payment_date')[:5]
            data["table_data"] = [
                {
                    "Student": p.installment.allocation.student.user.get_full_name() or p.installment.allocation.student.user.username,
                    "Amount": f"₹ {p.amount}",
                    "Mode": p.mode,
                    "Date": p.payment_date
                }
                for p in payments
            ]

        # ------------------------------------------------
        # 3. TEACHER (Faculty View)
        # ------------------------------------------------
        elif role == User.Roles.TEACHER:
            my_batches = Batch.objects.filter(teachers=user)
            batch_count = my_batches.count()
            student_count = StudentProfile.objects.filter(batch__in=my_batches).distinct().count()

            data["widgets"] = [
                {"label": "My Batches", "value": batch_count, "color": "blue"},
                {"label": "Total Students", "value": student_count, "color": "teal"},
            ]

            data["table_title"] = "My Scheduled Batches"
            data["table_data"] = list(my_batches.values('name', 'year'))

        # ------------------------------------------------
        # 4. STUDENT
        # ------------------------------------------------
        elif role == User.Roles.STUDENT:
            try:
                profile = user.student_profile
                total_classes = AttendanceRecord.objects.filter(student=profile).count()
                present_classes = AttendanceRecord.objects.filter(student=profile, status='PRESENT').count()
                percentage = round((present_classes / total_classes * 100), 1) if total_classes > 0 else 0

                due_amount = FeeInstallment.objects.filter(
                    allocation__student=profile,
                    status__in=['PENDING', 'PARTIAL']
                ).aggregate(Sum('amount_due'))['amount_due__sum'] or 0

                data["widgets"] = [
                    {"label": "Attendance", "value": f"{percentage}%", "color": "red" if percentage < 75 else "green"},
                    {"label": "Fees Due", "value": f"₹ {due_amount}", "color": "red" if due_amount > 0 else "green"},
                    {"label": "My Batch", "value": profile.batch.name if profile.batch else "N/A", "color": "blue"},
                ]

                data["table_title"] = "My Recent Attendance"
                records = AttendanceRecord.objects.filter(student=profile).order_by('-date')[:5]
                data["table_data"] = [{"Date": r.date, "Status": r.status, "Subject/Batch": r.batch.name} for r in records]

            except StudentProfile.DoesNotExist:
                data["widgets"] = [{"label": "Error", "value": "No Profile Found", "color": "red"}]

        # ------------------------------------------------
        # 5. PARENT
        # ------------------------------------------------
        elif role == User.Roles.PARENT:
            children = request.user.children.all()  # reverse M2M relation from StudentProfile.parents

            total_due = 0
            for child in children:
                due = FeeInstallment.objects.filter(
                    allocation__student=child,
                    status__in=['PENDING', 'PARTIAL']
                ).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
                total_due += due

            data["widgets"] = [
                {"label": "My Children", "value": children.count(), "color": "blue"},
                {"label": "Total Fees Due", "value": f"₹ {total_due}", "color": "red" if total_due > 0 else "green"},
            ]

            data["table_title"] = "My Children's Status"
            data["table_data"] = [
                {
                    "Name": c.user.get_full_name(),
                    "Class": c.batch.name if c.batch else "No Batch",
                    "Roll No": c.enrollment_number
                } for c in children
            ]

        return Response(data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Login Endpoint.
    Returns: Access Token, Refresh Token, User Role, and Institute ID.
    """
    serializer_class = CustomTokenObtainPairSerializer


# --- New: InstituteViewSet and UserViewSet for API Routers ---


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class InstituteViewSet(viewsets.ModelViewSet):
    """
    API for Super Admins to manage Institutes.
    """
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """
    API to manage Users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Super Admin sees all users
        if self.request.user.role == User.Roles.SUPER_ADMIN:
            return User.objects.all()
        # Institute Admin sees only their institute users
        return User.objects.filter(institute=self.request.user.institute)
