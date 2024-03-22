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
from django.core.exceptions import ValidationError


def cadastro(request):
        status = ''
        if 'cadastrar' in request.POST:           
            cpf = request.POST.get("cpf")
            nome = request.POST.get("nome")
            sobrenome = request.POST.get("sobrenome")
            email = request.POST.get("email")
            telefone = request.POST.get('tel')
            celular = request.POST.get('cel')
            sexo = request.POST.get("sexo")
            dataNascimento = request.POST.get("dtNascimento")
            senha = request.POST.get("senha")
            confSenha = request.POST.get("confSenha")
            if cpf == ' ' or nome == '' or sobrenome == '' or email == '' or telefone == '' or celular == '' or sexo == '' or dataNascimento == '' or senha == '' or confSenha == '':      
                messages.error(request,'Preencha todos os campos')
                status = 'erro'  
                print(f'STATUS: {status}')
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
                        status = 'erro'  
                else:
                    messages.error(request,"As senhas inseridas são diferentes")  
                    status = 'erro'             
                    return redirect("/cadastro")                   
        if 'login' in request.POST:
            return redirect('/login')
        return render(request,'cadastro.html',{'status':status})

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
            return redirect('../cadastrarCliente/'+str(cpf))
        elif 'cadProduto' in request.POST:
            return redirect('../cadastroProduto/'+str(cpf))
        elif 'CadFornecedor' in request.POST:
            return redirect('../cadastrarFornecedor/'+str(cpf))
        elif 'cadLote' in request.POST:
            return redirect('../cadastrarLote/'+str(cpf))
        elif 'comprarProduto' in request.POST:
            return redirect('../comprarProduto/'+str(cpf))
        elif 'grafico' in request.POST:
            return redirect('../graficos/'+str(cpf))
        elif 'editarConta' in request.POST:
            return redirect('../editarPerfil/'+str(cpf))
    except Usuario.DoesNotExist:
        messages.error(request,'Esse usuário não existe')
        return redirect('login')
    return render(request,'paginaInicial.html')

def cadastrarCliente(request,cpf):
    if 'Sair' in request.POST:
        return redirect('sair')
    elif 'cadastrar' in request.POST:
        try:
            cpfCliente = request.POST.get('cpf')
            nome = request.POST.get("nome")
            sobrenome = request.POST.get("sobrenome")
            email = request.POST.get("email")
            telefone = request.POST.get('telefone')
            celular = request.POST.get('celular')
            endereco = request.POST.get('endereco')
            cidade = request.POST.get('cidade')
            sexo = request.POST.get("sexo")
            dataNascimento = request.POST.get("dtNascimento")
            Cliente.objects.create(cpf=cpfCliente,nome=nome,sobrenome=sobrenome,email=email,telefone=telefone,celular=celular,
                                endereco=endereco,cidade=cidade, sexo=sexo,dataNascimento=dataNascimento)
            messages.success(request,'Cliente cadastrado com sucesso')
        except ValueError:
            messages.error(request,'Preencha todos os campos')
        except ValidationError:
            messages.error(request,'Insira a data de nascimento do cliente')
        except IntegrityError:
            messages.error(request,'Já existe um cliente cadastrado com esse CPF')
        return redirect('../cadastrarCliente/'+str(cpf))
    return render(request,'cadastrarCliente.html',{'cpf':cpf})

def cadastroProduto(request,cpf):
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'cadastrar' in request.POST:
        try:
            nome = request.POST.get('nome')
            marca = request.POST.get('marca')
            peso = request.POST.get('peso')
            medida = request.POST.get('medida')
            preco = request.POST.get('preco')
            descricao = request.POST.get('descProduto')
            Produto.objects.create(nome=nome,marca=marca,peso=peso,medida=medida,preco=preco,descricao=descricao)
            messages.success(request,'Produto cadastrado com sucesso')
        except ValueError:
            messages.error(request,'Preencha todos os campos')
            return redirect('../cadastroProduto/'+str(cpf))
    return render(request,'cadastrarProduto.html',{'cpf':cpf})

def comprarProduto(request,cpf):
    produtos = Produto.objects.all()
    clientes = Cliente.objects.all()
    fornecedores = Fornecedor.objects.all()
    if 'Sair' in request.POST:
        return redirect('sair')
    elif 'comprar' in request.POST:
        try:
            cpfCliente = request.POST.get('cpfCli')
            idProduto = request.POST.get('idProduto')
            quantProd = loteProd.objects.values_list('quanti').filter(idProduto=idProduto)
            quantidade = request.POST.get('quant')
            prod = Produto.objects.get(id=idProduto)
            cli = Cliente.objects.get(cpf=cpfCliente)
            somaLotes = 0
            totCompras = 0
            lotes = loteProd.objects.values_list('quanti',flat=True).filter(idProduto=idProduto)
            comprasAntes = comprarProd.objects.values_list('quantProd',flat=True).filter(idProduto=idProduto)
            for compraAnte in comprasAntes:
                totCompras += compraAnte
            for lote in lotes:
                somaLotes+=lote
            if (int(somaLotes) <= int(totCompras)+int(quantidade)):
                messages.error(request,'A quantidade disponível desse produto é menor que a solicitada')
            else:
                comprarProd.objects.create(cpfCliente=cli,idProduto=prod,quantProd=quantidade)
                messages.success(request,'Compra registrada com sucesso')
        except ValueError:
            messages.error(request,'Preencha todos os campos')
            return redirect('../comprarProduto/'+str(cpf))
        except Cliente.DoesNotExist:
            messages.error(request,'Selecione um cliente')
            return redirect('../comprarProduto/'+str(cpf))
    return render(request,'comprarProduto.html',{'produtos':produtos,'clientes':clientes,'fornecedores':fornecedores,'cpf':cpf})

def cadastrarFornecedor(request,cpf):
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'cadastrar' in request.POST:
        try:
            cnpj = request.POST.get('cnpj')
            nome = request.POST.get('nome')
            ramo = request.POST.get('ramo')
            email = request.POST.get('email')
            telefone = request.POST.get('telefone')
            endereco = request.POST.get('endereco')
            cidade = request.POST.get('cidade')
            estado = request.POST.get('estado')
            Fornecedor.objects.create(cnpj=cnpj,nome=nome,ramo=ramo,email=email,telefone=telefone,endereco=endereco,cidade=cidade,estado=estado)
        except ValueError:
            messages.error(request,'Preencha todos os campos')
        except IntegrityError:
            messages.error(request, "Já existe um fornecedor cadastrado com esse CNPJ")
        except AttributeError:
            messages.error(request,'Preencha todos os campos')
        return redirect('../cadastrarFornecedor/'+str(cpf))
    
    return render(request,'cadastrarFornecedor.html',{'cpf':cpf})

def cadastrarLote(request,cpf):
    produtos = Produto.objects.all()
    fornecedores = Fornecedor.objects.all()
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'cadastrar' in request.POST:
        try:
            idProduto = request.POST.get('idProduto')
            cnpj = request.POST.get('cnpj')
            quantidade = request.POST.get('quantidade')
            fabricacao = request.POST.get('dataFabri')
            validade = request.POST.get('dataVali')
            prod = Produto.objects.get(id=idProduto)
            fornec = Fornecedor.objects.get(cnpj=cnpj)
            print(f'cnpj: {cnpj} idProduto: {idProduto}')
            loteProd.objects.create(idProduto=prod,idFornecedor=fornec,quanti=quantidade,fabri=fabricacao,vali=validade)
            messages.success(request,'Lote cadastrado com sucesso')
        except ValueError:
            messages.error(request,'Preencha todos os campos')
        except ValidationError:
            messages.error(request,'Insira a data de fabricação e validade')
        except Fornecedor.DoesNotExist:
            messages.error(request,'Insira um fornecedor')
        return redirect('../cadastrarLote/'+str(cpf))
    return render(request,'cadastrarLote.html',{'produtos':produtos,'fornecedores':fornecedores,'cpf':cpf})

def graficos(request,cpf):
    dados = Produto.objects.raw('''select p.id,p.nome, 
                                sum(lp.quanti) as Quantidade_Vendida,
                                sum(cp.quantProd) as Quantidade_Comprada 
                                from loteprod lp 
                                left join produto p on (lp.idProduto_id = p.id) 
                                left join clienteprod cp on (lp.idProduto_id = cp.idProduto_id) 
                                group by p.nome''')
    if 'Sair' in request.POST:
        return redirect('sair')     
    return render(request,'graficos.html',{'cpf':cpf,'dados':dados})

def editarPerfil(request,cpf):
    try:
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
    except Usuario.DoesNotExist:
        messages.error(request,'Esse usuário não existe') 
        return redirect('../paginaInicial/'+str(cpf))   
    return render(request,'editarPerfil.html',{'usuario':usuario,'data':data,'cpf':cpf})

def sair(request):
    logout(request)
    messages.success(request,"Você saiu do seu perfil")
    return HttpResponseRedirect("/")
