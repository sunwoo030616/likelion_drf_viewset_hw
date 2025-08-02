from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    tags = serializers.SerializerMethodField()

    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)

    comments = serializers.SerializerMethodField(read_only=True)
    like_num = serializers.IntegerField()  # 좋아요 수 추가

    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many=True)
        return serializer.data 
    

    def get_tags(self, instance):
        tag = instance.tags.all()
        return [t.name for t in tag]

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'comments',
            'click_num',
            'like_num',
        ]
    image = serializers.ImageField(use_url=True, required=False)

class PostListSerializer(serializers.ModelSerializer):
    comments_cnt = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    like_num = serializers.IntegerField()

    def get_comments_cnt(self, instance):
        return instance.comments.count()
    
    def get_tags(self, instance):
        tags = instance.tags.all()
        return [tag.name for tag in tags]
    class Meta:
        model = Post
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
            'image',
            'comments_cnt',
            'tags',
            'like_num',
        ]
        read_only_fields = ['id','created_at','updated_at','comments_cnt']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
