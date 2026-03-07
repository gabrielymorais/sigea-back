from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "email",
            "cpf",
            "telefone",
            "tipo_profissional",
            "escola_lotacao",
            "portaria",
            "is_archived",
            "archived_at",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "username",
            "full_name",
            "email",
            "cpf",
            "telefone",
            "tipo_profissional",
            "escola_lotacao",
            "portaria",
            "password",
        ]
        extra_kwargs = {
            "username": {"required": True, "allow_blank": False},
            "full_name": {"required": True, "allow_blank": False},
            "email": {"required": True, "allow_blank": False},
            "cpf": {"required": True, "allow_blank": False},
            "telefone": {"required": True, "allow_blank": False},
            "tipo_profissional": {"required": True, "allow_blank": False},
            "escola_lotacao": {"required": True, "allow_blank": False},
            "portaria": {"required": True, "allow_blank": False},
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Nome de usuário já está em uso.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email já está em uso.")
        return value

    def validate_cpf(self, value):
        if User.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("CPF já está em uso.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Atualização segura.
    - Para trocar senha: mandar current_password + new_password
    - Admin pode resetar senha de outro usuário mandando só new_password (opcional)
    """
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = [
            "username",
            "full_name",
            "email",
            "cpf",
            "telefone",
            "tipo_profissional",
            "escola_lotacao",
            "portaria",
            "current_password",
            "new_password",
        ]

    def validate_username(self, value):
        qs = User.objects.filter(username=value).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Nome de usuário já está em uso.")
        return value

    def validate_email(self, value):
        qs = User.objects.filter(email=value).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email já está em uso.")
        return value

    def validate_cpf(self, value):
        qs = User.objects.filter(cpf=value).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("CPF já está em uso.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")

        if not new_password:
            return attrs

        # Se admin está resetando senha de outro usuário, pode sem senha atual 
        if request and request.user and request.user.is_staff and self.instance.pk != request.user.pk:
            return attrs

        # Self: exige senha atual
        if not current_password:
            raise serializers.ValidationError(
                {"current_password": "Informe sua senha atual para alterar a senha."}
            )

        if not self.instance.check_password(current_password):
            raise serializers.ValidationError({"current_password": "Senha atual incorreta."})

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("current_password", None)
        new_password = validated_data.pop("new_password", None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance