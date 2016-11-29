from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^participant/$', views.participant, name='participant'),
	url(r'^instructor/$', views.instructor, name='instructor'),
	url(r'^instructor/new/$', views.newCourse, name='newCourse'),
	url(r'^instructor/deployCourse/$', views.deployCourse, name='deployCourse'),
	url(r'^instructor/edit/(?P<course_id>\d+)/$', views.editCourse, name='editCourse'),
	url(r'^participant/course/(?P<course_id>\d+)/$', views.view_course, name='view'),
	url(r'^participant/course/(?P<course_id>\d+)/(?P<participant_id>\d+)/complete/$', views.completeCourse, name='completeCourse'),
	url(r'^addDrop/$', views.addDrop, name='addDrop'),
	url(r'^instructor/new/loadComponents/$', views.loadComponents, name='loadComponents'),
	url(r'^instructor/new/addModule/$', views.addModule, name='addModules'),
	url(r'^instructor/new/renameModule/$', views.renameModule, name='renameModule'),
	url(r'^instructor/new/deleteModule/$', views.deleteModule, name='deleteModule'),
	url(r'^instructor/new/addComponent/$', views.addComponent, name='addComponent'),
	url(r'^instructor/new/deleteComponent/$', views.deleteComponent, name='deleteComponent'),
	url(r'^instructor/new/loadComponentBody/$', views.loadComponentBody, name='loadComponentBody'),
	url(r'^admin/$', views.admin, name='admin'),
	url(r'^admin/newCategory/$', views.newCategory, name='newCategory'),
	url(r'^admin/adminchange/$', views.adminchange, name='adminchange'),
	url(r'^admin/deleteCategory/$', views.deleteCategory, name='deleteCategory'),
	url(r'^register/$', views.register, name='register'),
	url(r'^regComplete/$', views.regComplete, name='regComplete'),
	url(r'^participant/course/(?P<course_id>\d+)/partiComponentBody/$', views.partiComponentBody, name='partiComponentBody'),
	url(r'^participant/course/(?P<course_id>\d+)/loadModules/$', views.loadModules, name='loadModules'),
	url(r'^hr/$', views.participantList, name='participantList'),
	url(r'^hr/(?P<participant_id>\d+)/$', views.courseHistory, name='courseHistory'),
    url(r'^login/$', auth_views.login, {'template_name': 'main/login.html'}, name='login'),
    url(r'^logout/$', views.logOut, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
