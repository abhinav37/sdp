from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^participant/$', views.participant, name='participant'),
	url(r'^instructor/$', views.instructor, name='instructor'),
	url(r'^instructor/new/$', views.newCourse, name='newCourse'),
	url(r'^participant/course/(?P<course_id>\d+)/$', views.view_course, name='view'),
	url(r'^finish/$', views.enrolling, name='enrolling'),
]