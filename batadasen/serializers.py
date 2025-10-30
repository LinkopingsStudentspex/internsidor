from rest_framework import serializers
from batadasen.models import Person


class PersonSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ["username", "first_name", "last_name", "email", "member_number"]

    def get_username(self, obj):
        if obj.user is None:
            return None
        else:
            return obj.user.username
