from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view #데코레이터
from rest_framework import viewsets, mixins
from rest_framework.decorators import action

from .models import Post, Comment, Tag
from .serializers import PostSerializer, CommentSerializer, TagSerializer, PostListSerializer

from django.shortcuts import get_object_or_404

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return [IsAdminUser()]
        return []
        

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        post = serializer.instance
        self.handle_tags(post)

        return Response(serializer.data)
    
    def perform_update(self, serializer):
        post = serializer.save()
        post.tags.clear()
        self.handle_tags(post)

    def handle_tags(self, post):
        tags = [words[1:] for words in post.content.split(' ') if words.startswith('#')]
        for t in tags:
            tag, created = Tag.objects.get_or_create(name=t)
            post.tags.add(tag)
        post.save()
    
    @action(methods=['GET'], detail=False)
    def recommend(self, request):
        ran_post = self.get_queryset().order_by("?").first()
        ran_post_serializer = PostListSerializer(ran_post)
        return Response(ran_post_serializer.data)
    
    @action(methods=['GET'], detail=True)
    def test(self, request, pk=None):
        test_post = self.get_object()
        test_post.click_num+=1
        test_post.save(update_fields=['click_num'])
        return Response()

#댓글 디테일 조회 수정 삭제   
class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return [IsOwnerOrReadOnly()]
        return []
#영화 게시물에 있는 댓글 목록 조회, 영화 게시물에 댓글 작성
class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset

    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)


class TagViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg="tag_name"

    def retrieve(self, request, *args, **kwargs):
        tag_name=kwargs.get("tag_name")
        tags=get_object_or_404(Tag, name=tag_name)
        posts=Post.objects.filter(tags=tags)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


