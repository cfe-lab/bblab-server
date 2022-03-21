from django.urls import path
from . import views

urlpatterns = [
	path('', views.index),
	path('add_on_column/', views.index_column),
	path('generate_files/', views.generate_files, name="generate_files"),
	path('output/', views.output),
	path('output/<filename>', views.output),
	path('output/archived_layouts/', views.archive),
	path('output/archived_layouts/<filename>', views.archive),
	path('output/archived_layouts/old_archived_layouts/', views.old_archive),
	path('output/archived_layouts/old_archived_layouts/<filename>', views.old_archive),
]
