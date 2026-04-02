from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.paginators import CoursePagination
from lms.serializers import (CourseDetailSerializer, CourseSerializer,
                             LessonSerializer)
from users.models import Payments
from users.permissions import IsModerator, IsOwner

# Create your views here.

@extend_schema_view(
    list=extend_schema(
        summary="Список курсов",
        description="Возвращает список курсов пользователя. Модераторы видят все курсы.",
        responses={200: CourseSerializer(many=True)},
        tags=['courses'],
    ),
    retrieve=extend_schema(
        summary="Детальная информация о курсе",
        description="Возвращает информацию о курсе. Если есть доступ — включает уроки.",
        responses={200: CourseDetailSerializer},
        tags=['courses'],
    ),
    create=extend_schema(
        summary="Создание курса",
        description="Создаёт новый курс. Доступно только обычным пользователям.",
        request=CourseSerializer,
        responses={201: CourseSerializer},
        tags=['courses'],
    ),
    update=extend_schema(
        summary="Обновление курса",
        description="Обновляет курс. Доступно модераторам и владельцам.",
        request=CourseSerializer,
        responses={200: CourseSerializer},
        tags=['courses'],
    ),
    destroy=extend_schema(
        summary="Удаление курса",
        description="Удаляет курс. Доступно только владельцу.",
        responses={204: None},
        tags=['courses'],
    ),
)
class CourseViewSet(ModelViewSet):
    """ViewSet для управления курсами"""

    queryset = Course.objects.all()
    pagination_class = CoursePagination

    def get_serializer_class(self):
        """Динамический выбор сериализатора"""
        if self.action == "list":
            return CourseSerializer

        if self.action == "retrieve":
            if self._has_full_access(self.request.user, self.get_object()):
                return CourseDetailSerializer

        return CourseSerializer

    def _has_full_access(self, user, course):
        """
        Проверяет доступ к полной версии курса (урокам).
        Доступ имеют:
        - Модераторы
        - Владелец курса
        - Пользователь, купивший курс
        """
        if not user or not user.is_authenticated:
            return False

        if user.groups.filter(name="Moderators").exists():
            return True

        if course.owner == user:
            return True

        # Проверяем покупку курса
        if Payments.objects.filter(user=user, paid_course=course, is_paid=True).exists():
            return True
        return False

    def get_queryset(self):
        """Возвращает курсы для списка "Мои курсы":
        - Свои курсы (владелец)
        - Купленные курсы (есть платёж)
        """
        user = self.request.user

        if not user.is_authenticated:
            return Course.objects.none()

        if user.groups.filter(name="Moderators").exists():
            return Course.objects.all()

        owned = Course.objects.filter(owner=user)

        purchased_ids = Payments.objects.filter(
            user=user, paid_course__isnull=False, is_paid=True
        ).values_list("paid_course", flat=True)

        return owned | Course.objects.filter(id__in=purchased_ids)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), (~IsModerator)()]

        elif self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), (IsModerator | IsOwner)()]

        elif self.action == "destroy":
            return [IsAuthenticated(), IsOwner()]

        elif self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        return super().get_permissions()


@extend_schema_view(
    post=extend_schema(
        summary="Создание урока",
        description="Создаёт новый урок. Доступно только обычным пользователям",
        request=LessonSerializer,
        responses={201: LessonSerializer},
        tags=['lessons'],
    )
)
class LessonCreateAPIView(generics.CreateAPIView):
    """Создание нового урока."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModerator]  # Только обычные пользователи

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



@extend_schema_view(
    get=extend_schema(
        summary="Список уроков",
        description="Возвращает список уроков. Модераторы видят все уроки, обычные пользователи - свои",
        responses={200: LessonSerializer(many=True)},
        tags=['lessons'],
    )
)
class LessonListAPIView(generics.ListAPIView):
    """Получение списка всех уроков."""

    serializer_class = LessonSerializer
    pagination_class = CoursePagination

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name="Moderators").exists():
            return Lesson.objects.all()

        # 1. Свои уроки
        owned = Lesson.objects.filter(owner=user)

        # 2. Купленные уроки
        purchased_lesson_ids = Payments.objects.filter(
            user=user, paid_lesson__isnull=False, is_paid=True
        ).values_list("paid_lesson", flat=True)

        # 3. Уроки из купленных курсов
        purchased_course_ids = Payments.objects.filter(
            user=user, paid_course__isnull=False, is_paid=True
        ).values_list("paid_course", flat=True)

        return owned | Lesson.objects.filter(id__in=purchased_lesson_ids) | Lesson.objects.filter(
            course__id__in=purchased_course_ids)



@extend_schema_view(
    get=extend_schema(
        summary="Детальная информация об уроке",
        description="Возвращает детальную информацию о конкретном уроке.",
        responses={200: LessonSerializer},
        tags=['lessons'],
    )
)
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение детальной информации о конкретном уроке."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]



@extend_schema_view(
    put=extend_schema(
        summary="Обновление урока",
        description="Обновляет существующий урок. Доступно модераторам и владельцам.",
        request=LessonSerializer,
        responses={200: LessonSerializer},
        tags=['lessons'],
    ),
    patch=extend_schema(
        summary="Частичное обновление урока",
        description="Частично обновляет существующий урок. Доступно модераторам и владельцам.",
        request=LessonSerializer,
        responses={200: LessonSerializer},
        tags=['lessons'],
    ),
)
class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление существующего урока."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]

@extend_schema_view(
    delete=extend_schema(
        summary="Удаление урока",
        description="Удалять уроки могут только владельцы этого урока",
        responses={204: None},
        tags=['lessons'],
    )
)
class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner]
