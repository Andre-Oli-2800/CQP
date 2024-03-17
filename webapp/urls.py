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
    path('paginaInicial/<int:cpf>',views.paginaInicial,name='paginaInicial'),   
    path('cadastrarCliente/<int:cpf>',views.cadastrarCliente,name='cadastrarCliente'),
    path('cadastroProduto/<int:cpf>',views.cadastroProduto,name='cadastroProduto'),
    path('cadastrarFornecedor/<int:cpf>',views.cadastrarFornecedor,name='cadastrarFornecedor'),
    path('comprarProduto/<int:cpf>',views.comprarProduro,name='comprarProduto'),
    path('cadastrarLote/<int:cpf>',views.cadastrarLote,name='cadastrarLote'),
    path('graficos/<int:cpf>',views.graficos,name='graficos'),
    path('excluir/<int:id>',views.excluir,name='excluir'),
    path('editarPerfil/<int:cpf>',views.editarPerfil,name='editarPerfil'),
    path('sair',views.sair,name='sair'),
]

