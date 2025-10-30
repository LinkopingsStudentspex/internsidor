from rest_framework import serializers
from . import models


class SubtitleTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubtitleTrack
        fields = ["name", "subtitle_file"]


class VideoSerializer(serializers.ModelSerializer):
    subtitles = SubtitleTrackSerializer(many=True)

    class Meta:
        model = models.Video
        fields = [
            "title",
            "video_file",
            "information",
            "video_type",
            "subtitles",
        ]


class ProductionSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True)

    class Meta:
        model = models.Production
        fields = [
            "id",
            "short_name",
            "year",
            "title",
            "subtitle",
            "poster_image",
            "information",
            "videos",
        ]
