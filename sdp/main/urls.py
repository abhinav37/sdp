from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^participant/$', views.participant, name='participant'),
	url(r'^instructor/$', views.instructor, name='instructor'),
	url(r'^instructor/new/$', views.newCourse, name='newCourse'),
	url(r'^instructor/edit/(?P<course_id>\d+)/$', views.editCourse, name='editCourse'),
	url(r'^participant/course/(?P<course_id>\d+)/$', views.view_course, name='view'),
	url(r'^addDrop/$', views.addDrop, name='addDrop'),
	url(r'^instructor/new/loadComponents/$', views.loadComponents, name='loadComponents'),
	url(r'^instructor/new/add_module/$', views.add_module, name='add_modules'),
	url(r'^instructor/new/add_component/$', views.add_component, name='add_component'),

]