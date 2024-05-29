from django.urls import path
from . import views
from .views import delete_segment,update_segment_texts,upload_video,merge_edited_audio_video,resend_code

urlpatterns = [
	path('payment_successful', views.payment_successful, name='payment_successful'),
	path('payment_cancelled', views.payment_cancelled, name='payment_cancelled'),
	path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),
    path('', views.index, name='index'),
    path('pricing', views.pricing, name='pricing'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    path('onboard/<int:pk>',views.onboard,name='onboard'),
    path('work_space/<int:pk>', views.work_space, name='work_space'),
    path('user_history/<int:pk>', views.user_history, name='user_history'),
    path('delete-segment/<int:workspace_pk>/<int:segment_index>/', delete_segment, name='delete_segment'),
    path('update-segment-texts/<int:workspace_pk>/', update_segment_texts, name='update_segment_texts'),
    path('upload_video/<int:pk>/', upload_video, name='upload_video'),
    path('merge_edited_audio_video/<int:pk>/', merge_edited_audio_video, name='merge_edited_audio_video'),
    path('admin_login',views.admin_login,name="admin_login"),
    path('admin_side',views.admin_side,name="admin_side"),
    path('admin_logout',views.admin_logout,name="admin_logout"),
    path('delete_entry/<int:user_id>/', views.delete_entry, name='delete_entry'), 
    path('resend_code/', resend_code, name='resend_code'),
    path('save_feedback/', views.save_feedback, name='save_feedback'),
]
