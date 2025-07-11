from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_content, name='generate_content'),
    path('generate-custom/', views.generate_custom_content, name='generate_custom_content'),
    path('custom-prompt/', views.custom_prompt, name='custom_prompt'),
    path('reference-image/', views.reference_image_generator, name='reference_image_generator'),
    path('generate-reference-image/', views.generate_reference_image, name='generate_reference_image'),
    path('video-generator/', views.video_generator, name='video_generator'),
    path('generate-video/', views.generate_video, name='generate_video'),
    path('meme-generator/', views.meme_generator, name='meme_generator'),
    path('generate-meme/', views.generate_meme, name='generate_meme'),
    path('healthcheck/', views.healthcheck, name='healthcheck'),
] 