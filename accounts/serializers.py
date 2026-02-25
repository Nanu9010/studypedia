# ===== accounts/serializers.py =====
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Follow

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        username_or_email = data.get('username_or_email').strip()
        password = data.get('password')

        user = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email.lower())
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                raise serializers.ValidationError({'error': 'No account found with this email.'})
        else:
            user = authenticate(username=username_or_email, password=password)
            if user is None:
                raise serializers.ValidationError({'error': 'Invalid username or password.'})

        if user is None:
            raise serializers.ValidationError({'error': 'Invalid credentials.'})

        if not user.is_active:
            raise serializers.ValidationError({'error': 'This account is inactive.'})

        data['user'] = user
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    password_confirm = serializers.CharField(max_length=128, write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'college', 'year_of_study', 'location', 'phone', 'profile_picture', 'bio'
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Passwords must match.'}
            )
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    # follower_count = serializers.IntegerField(source='follower_count', read_only=True)
    # following_count = serializers.IntegerField(source='following_count', read_only=True)
    is_admin_user = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 'college',
            'year_of_study', 'location', 'phone', 'profile_picture', 'bio', 'credits',
            'wallet_balance', 'follower_count', 'following_count', 'is_admin_user',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'role', 'credits', 'wallet_balance', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # Update only allowed fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'follower_username', 'following_username', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        follower = data['follower']
        following = data['following']
        if follower == following:
            raise serializers.ValidationError('Users cannot follow themselves.')
        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError('This follow relationship already exists.')
        return data