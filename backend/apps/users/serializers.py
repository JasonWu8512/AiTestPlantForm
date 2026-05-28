from django.contrib.auth.models import Group, User
from rest_framework import serializers


ROLE_NAMES = ("admin", "tester", "viewer")


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "is_active", "is_staff", "is_superuser", "role", "date_joined")
        read_only_fields = ("id", "is_staff", "is_superuser", "date_joined")

    def get_role(self, obj):
        if obj.is_superuser:
            return "admin"
        group = obj.groups.filter(name__in=ROLE_NAMES).first()
        return group.name if group else "viewer"


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, min_length=6)
    role = serializers.ChoiceField(choices=ROLE_NAMES, required=False, default="viewer")

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "is_active", "role")
        read_only_fields = ("id",)

    def create(self, validated_data):
        role = validated_data.pop("role", "viewer")
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        user.set_password(password)
        user.is_staff = role == "admin"
        user.is_superuser = role == "admin"
        user.save()
        self._sync_role(user, role)
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop("role", None)
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        if role:
            instance.is_staff = role == "admin"
            instance.is_superuser = role == "admin"
            self._sync_role(instance, role)
        instance.save()
        return instance

    def _sync_role(self, user, role):
        for role_name in ROLE_NAMES:
            group, _ = Group.objects.get_or_create(name=role_name)
            user.groups.remove(group)
        group = Group.objects.get(name=role)
        user.groups.add(group)
