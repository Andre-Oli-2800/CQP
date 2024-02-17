import os
import stat
from django.db import IntegrityError
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from website.models import Usuario, Cliente,Produto,Fornecedor,comprarProd,loteProd
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.db.utils import OperationalError

def cadastro(request):
        if 'cadastrar' in request.POST:           
                cpf = request.POST.get("cpf")
                nome = request.POST.get("nome")
                sobrenome = request.POST.get("sobrenome")
                email = request.POST.get("email")
                telefone = request.POST.get('telefone')
                celular = request.POST.get('celular')
                sexo = request.POST.get("sexo")
                dataNascimento = request.POST.get("dtNascimento")
                senha = request.POST.get("senha")
                confSenha = request.POST.get("confSenha")
                if cpf == ' ' or nome == '' or sobrenome == '' or email == '' or telefone == '' or celular == '' or sexo == '' or dataNascimento == '' or senha == '' or confSenha == '':      
                    messages.error(request,'Preencha todos os campos')
                    return redirect('cadastro')
                else:
                    if senha == confSenha:
                        try:
                            senha = make_password(senha) 
                            usuarioCriado = Usuario.objects.create(cpf=cpf,nome=nome,sobrenome=sobrenome,email=email,telefone=telefone, celular=celular, sexo=sexo,dataNascimento=dataNascimento,senha=senha)                      
                            autenticarUsuario = User(username=email, password=senha)    
                            autenticarUsuario.save() 
                            messages.success(request,"Conta criada com sucesso")
                            return redirect('/login') 
                        except (IntegrityError):
                            messages.error(request, 'Já existe um usuário cadastrado com esse CPF')
                    else:
                        messages.error(request,"As senhas inseridas são diferentes")               
                        return redirect("/cadastro")                   
        if 'login' in request.POST:
            return redirect('/login')
        return render(request,'cadastro.html')

def login(request):
    if 'login' in request.POST:
        try:
            email = request.POST.get("email")
            senha = request.POST.get("senha")
            usuario = Usuario.objects.get(email=email)
            user = User.objects.get(username= usuario.email)           
            if email == '' or senha == '':
                messages.error(request, 'Preencha todos os campos')    
            else:
                if usuario:
                    checar_senha=check_password(senha, user.password)
                    if checar_senha:
                        cpf = usuario.cpf
                        return redirect('/paginaInicial/'+str(cpf))
                    else:
                        messages.error(request, "Email/senha inválido(s)") 
                        return redirect('login')                          
        except (Usuario.DoesNotExist):   
            messages.error(request, "Email/senha inválido(s)")
            return redirect('login')  
        except (OperationalError):
            messages.error(request, "Email/senha inválido(s)")
            return redirect('login')    
    elif 'cadastrar' in request.POST:
        return redirect('/cadastro')
    return render(request,"login.html")

def paginaInicial (request,cpf):
    try:
        if "sair" in request.POST:
            return redirect('sair')
        elif 'cadCliente' in request.POST:
            return redirect('cadastrarCliente')
        elif 'cadProduto' in request.POST:
            return redirect('cadastroProduto')
        elif 'CadFornecedor' in request.POST:
            return redirect('cadastrarFornecedor')
        elif 'cadLote' in request.POST:
            return redirect('cadastrarLote')
        elif 'comprarProduto' in request.POST:
            return redirect('comprarProduto')
        elif 'grafico' in request.POST:
            return redirect('graficos')
        elif 'editarConta' in request.POST:
            return redirect('../editarPerfil/'+str(cpf))
    except Usuario.DoesNotExist:
        messages.error(request,'Esse usuário não existe')
        return redirect('login')
    return render(request,'paginaInicial.html')

def cadastrarCliente(request):
    if 'Sair' in request.POST:
        return redirect('sair')
    elif 'salvar' in request.POST:
        nome = request.POST.get("nome")
        sobrenome = request.POST.get("sobrenome")
        email = request.POST.get("email")
        telefone = request.POST.get('telefone')
        celular = request.POST.get('celular')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        sexo = request.POST.get("sexo")
        dataNascimento = request.POST.get("dtNascimento")
        Cliente.objects.create(nome=nome,sobrenome=sobrenome,email=email,telefone=telefone,celular=celular,
                               endereco=endereco,cidade=cidade, sexo=sexo,dataNascimento=dataNascimento)
    return render(request,'cadastrarCliente.html')

def cadastroProduto(request):
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'salvar' in request.POST:
        nome = request.POST('nome')
        marca = request.POST('marca')
        peso = request.POST('peso')
        descricao = request.POST('descProduto')
        Produto.objects.create(nome=nome,marca=marca,peso=peso,descricao=descricao)
    return render(request,'cadastrarProduto.html')

def comprarProduro(request):
    if 'Sair' in request.POST:
        return redirect('sair')
    elif 'confirmar' in request.POST:
        cpfCliente = request.POST.get('cpfCli')
        idProduto = request.POST.get('idProduto')
        quantidade = request.POST.get('quant')
        fabricacao = request.POST.get('dataFab')
        validade = request.POST.get('daraVali')
        comprarProd.objects.create(cpfCliente=cpfCliente,idProduto=idProduto,quantidade=quantidade,fabricacao=fabricacao,validade=validade)
        messages.success(request,'Compra registrada com sucesso')
        return redirect('comprarProduto')
    return render(request,'comprarProduto.html')

def cadastrarFornecedor(request):
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'cadastrar' in request.POST:
        cnpj = request.POST.get('cnpj')
        nome = request.POST.get('nome')
        ramo = request.POST.get('ramo')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        Fornecedor.objects.create(cnpj=cnpj,nome=nome,ramo=ramo,email=email,telefone=telefone,endereco=endereco,cidade=cidade,estado=estado)
        return('cadastrarFornecedor')
    return render(request,'cadastrarFornecedor.html')

def cadastrarLote(request):
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'Cadastrar' in request.POST:
        idProduto = request.POST.fet('idProduto')
        quantidade = request.POST.get('quanti')
        fabricacao = request.POST.get('dataFabri')
        validade = request.POST.get('dataVali')
        loteProd.objects.create(idProduto=idProduto,quantidade=quantidade,fabricacao=fabricacao,validade=validade)
        return redirect('cadastrarLote')
    return render(request,'cadastrarLote.html')

def graficos(request):
    if 'Sair' in request.POST:
        return redirect('sair')     
    return render(request,'graficos.html')



def editarPerfil(request,cpf):
    user= Usuario.objects.get(cpf=cpf)
    dataUsuario = user.dataNascimento
    dataPanda = pd.to_datetime(dataUsuario)
    data = str(dataPanda.date())
    usuario= Usuario.objects.filter(cpf=cpf)
    if 'Sair' in request.POST:
        return redirect('sair')
    elif 'salvar' in request.POST:
        nome = request.POST.get("nome")
        sobrenome = request.POST.get("sobrenome")
        email = request.POST.get("email")
        sexo = request.POST.get("sexo")
        dataNascimento = request.POST.get("dtNascimento")
        senha = request.POST.get("senha")
        confSenha = request.POST.get("confSenha")
        if nome == '' or sobrenome == '' or email == '' or sexo == '' or dataNascimento == '' or senha == '' or confSenha == '':      
            messages.error(request,'Preencha todos os campos')
            return redirect('editarPerfil/'+str(cpf))
        else:
            if senha == confSenha:
                Usuario.objects.filter(cpf=cpf).update(nome=nome, sobrenome=sobrenome,
                                       email=email,sexo=sexo,dataNascimento=dataNascimento,senha=senha)
                messages.success(request,"Perfil editado com sucesso")
                return redirect('/editarPerfil/'+str(cpf)) 
    return render(request,'editarPerfil.html',{'usuario':usuario,'data':data,'cpf':cpf})

def excluir(request, id):
    excluirArq = Usuario.objects.get(id=id)
    arquivo = str(excluirArq.enderecoArquivo)
    cpf = excluirArq.cpf
    excluirArq.delete()
    messages.sucess(request,"Arquivo exluído com sucesso")
    return redirect('../arquivosEnviados/'+str(cpf)) 

def sair(request):
    logout(request)
    messages.success(request,"Você saiu do seu perfil")
    return HttpResponseRedirect("/")
