"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import statistics
from django import views
from django.contrib import admin
from django.urls import path
from website import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name='login'),
    path('login', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('pagina_inicial/<int:cpf>',views.paginaInicial,name='pagina_inicial'),   
    path('enviarArquivo/<int:cpf>',views.enviarArquivo,name='enviarArquivo'),
    path('verBaixarArquivos/<int:cpf>',views.verBaixarArquivos,name='verBaixarArquivos'),
    path('baixarArquivo/<str:arquivo>',views.baixarArquivo, name='baixarArquivo'),
    path('visualizarArquivo/<str:arquivo>',views.visualizarArquivo, name='visualizarArquivo'),
    path('arquivosEnviados/<int:cpf>',views.arquivosEnviados,name='arquivosEnviados'),
    path('editarArquivo/<int:id>',views.editar,name='editar'),
    path('excluir/<int:id>',views.excluir,name='excluir'),
    path('editarPerfil/<int:cpf>',views.editarPerfil,name='editarPerfil'),
    path('sair',views.sair,name='sair'),
]
