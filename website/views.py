import os
import stat
import subprocess as sp
from django.db import IntegrityError
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from website.models import Usuario, Arquivo
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.utils.datastructures import MultiValueDictKeyError
import pandas as pd

def cadastro(request):
        if 'cadastrar' in request.POST:           
                cpf = request.POST.get("cpf")
                nome = request.POST.get("nome")
                sobrenome = request.POST.get("sobrenome")
                email = request.POST.get("email")
                sexo = request.POST.get("sexo")
                dataNascimento = request.POST.get("dtNascimento")
                senha = request.POST.get("senha")
                confSenha = request.POST.get("confSenha")
                if cpf == ' ' or nome == '' or sobrenome == '' or email == '' or sexo == '' or dataNascimento == '' or senha == '' or confSenha == '':      
                    messages.error(request,'Preencha todos os campos')
                    return redirect('cadastro')
                else:
                    if senha == confSenha:
                        try:
                            senha = make_password(senha)
                            autenticarUsuario = User(username=email, password=senha)                          
                            #autenticarUsuario.save()
                            Usuario.objects.create(cpf=cpf,nome=nome, sobrenome=sobrenome,
                                                email=email,sexo=sexo,dataNascimento=dataNascimento,senha=senha)
                            messages.success(request,"Conta criada com sucesso")
                            return redirect('/login') 
                        except (IntegrityError):
                            messages.error(request, 'Já existe um usuário cadastrado com esse CPF')
                    else:
                        messages.error(request,"As senhas estão diferentes")               
                        return redirect("/cadastro")                   
            
                return redirect("/cadastro")
        if 'login' in request.POST:
            return redirect('/login')
        return render(request,'cadastro.html')

def login(request):
    if 'login' in request.POST:
        try:
            email = request.POST.get("email")
            senha = request.POST.get("senha")
            usuarioExistente = Usuario.objects.filter(email=email,senha=senha).exists()
            dadosUsuario = Usuario.objects.get(email=email)
            cpf = dadosUsuario.cpf
            if email == '' or senha == '':
                messages.error(request, 'Preencha todos os campos')    
            else:
                if usuarioExistente != False:
                    return redirect('/pagina_inicial/'+str(cpf))
                else:
                    messages.error(request, "Email/senha inválido(s)")                           
        except (Usuario.DoesNotExist):   
            messages.error(request, "Email/senha inválido(s)")
    elif 'cadastrar' in request.POST:
        return redirect('/cadastro')
    return render(request,"login.html")

#@login_required(login_url='login')
def paginaInicial (request,cpf):
    if 'enviarArquivo' in request.POST:
        return redirect('../enviarArquivo/'+str(cpf))
    elif 'verbaiArquivo' in request.POST:
        return redirect('../verBaixarArquivos/'+str(cpf))
    elif 'arqEnviados' in request.POST:
        return redirect('../arquivosEnviados/'+str(cpf))
    elif 'editarConta' in request.POST:
        return redirect('../editarPerfil/'+str(cpf))
    return render(request,'pagina_inicial.html')

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

def enviarArquivo(request,cpf):
    if 'Sair' in request.POST:
        return redirect('sair')  
    elif 'Enviar' in request.POST:  
        try:
            arq = Arquivo()
            arq.titulo = request.POST.get('titulo')
            arq.enderecoArquivo = request.FILES['enderecoArquivo']
            arq.periodoHistorico = request.POST.get('periodoHistorico')
            arq.anoArquivo = request.POST.get('anoArquivo')
            arq.descArquivo = request.POST.get('descArquivo')
            arq.cpf = cpf
            arq.save()
            messages.success(request,'Arquivo enviado com sucesso')
        except MultiValueDictKeyError:
            messages.error(request,"Escolha um arquivo")
        except ValueError:
            messages.error(request, "Digite o ano do arquivo. Caso não saiba, coloque 'desconhecido' ")  
        
    return render(request,'enviarArquivo.html',{'cpf':cpf})

def verBaixarArquivos(request,cpf):
    arquivos = Arquivo.objects.all()
    pHistorico = Arquivo.objects.values_list('periodoHistorico', flat=True).distinct()
    anos = Arquivo.objects.values_list('anoArquivo', flat=True).distinct()
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'Pesquisar' in request.POST:
        periodoEscolhido = request.POST.get('periodoHistorico')
        ano = request.POST.get('ano')
        formato = request.POST.get('formato')
        ordenar = request.POST.get('ordenar')

        if periodoEscolhido == '' and ano == '' and ordenar == '':
            print("TESTEZINHO")
            arquivos = ''
        elif periodoEscolhido != '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)       
        elif ordenar != '' and periodoEscolhido != '' and ano != '':
            #arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)
            arquivos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[ano,periodoEscolhido])          
        elif periodoEscolhido == '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano)
        elif periodoEscolhido != '' and ano == '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
        elif ordenar != '' and ano == '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.order_by('titulo') 
        elif ordenar != '' and ano == '' and periodoEscolhido != '':
            arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido)   
        elif ordenar != '' and ano != '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano).order_by('titulo')   
        elif formato != '':
            arquivos = Arquivo.objects.filter(formato=formato) 
    if 'visualizar' in request.POST:
        periodoEscolhido = request.POST.get('periodoHistorico')
        ano = request.POST.get('ano')
        formato = request.POST.get('formato')
        ordenar = request.POST.get('ordenar')
        if periodoEscolhido == '' and ano == '' and ordenar == '':
            arquivos = ''
        elif periodoEscolhido != '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)       
        elif ordenar != '' and periodoEscolhido != '' and ano != '':
            #arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)
            arquivos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[ano,periodoEscolhido])          
        elif periodoEscolhido == '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano)
        elif periodoEscolhido != '' and ano == '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
        elif ordenar != '' and ano == '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.order_by('titulo') 
        elif ordenar != '' and ano == '' and periodoEscolhido != '':
            arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido)   
        elif ordenar != '' and ano != '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano).order_by('titulo')   
        elif formato != '':
            arquivos = Arquivo.objects.filter(formato=formato) 
    elif 'baixar' in request.POST:
        periodoEscolhido = request.POST.get('periodoHistorico')
        ano = request.POST.get('ano')
        formato = request.POST.get('formato')
        ordenar = request.POST.get('ordenar')
        if periodoEscolhido == '' and ano == '' and ordenar == '':
            arquivos = ''
        elif periodoEscolhido != '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)       
        elif ordenar != '' and periodoEscolhido != '' and ano != '':
            #arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)
            arquivos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[ano,periodoEscolhido])          
        elif periodoEscolhido == '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano)
        elif periodoEscolhido != '' and ano == '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
        elif ordenar != '' and ano == '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.order_by('titulo') 
        elif ordenar != '' and ano == '' and periodoEscolhido != '':
            arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido)   
        elif ordenar != '' and ano != '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano).order_by('titulo')   
        elif formato != '':
            arquivos = Arquivo.objects.filter(formato=formato) 
    elif 'sair' in request.POST:
         return redirect('sair')
    elif 'editar' in request.POST:
         return redirect('../editarPerfil/'+(arquivos.cpf))
    return render(request, 'verBaixarArquivos.html', {'arquivos' : arquivos,'pHistorico':pHistorico,'anos':anos,'cpf':cpf})

def arquivosEnviados(request,cpf):
    arquivos = Arquivo.objects.filter(cpf=cpf)
    pHistorico = Arquivo.objects.filter(cpf=cpf).values_list('periodoHistorico', flat=True).distinct()
    anos = Arquivo.objects.filter(cpf=cpf).values_list('anoArquivo', flat=True).distinct()
    nome = Arquivo.objects.filter(cpf=cpf).values_list('titulo', flat=True).distinct()
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'Pesquisar' in request.POST:
        periodoEscolhido = request.POST.get('periodoHistorico')
        ano = request.POST.get('ano')
        formato = request.POST.get('formato')
        ordenar = request.POST.get('ordenar')

        if periodoEscolhido != '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)
        
        elif periodoEscolhido == '' and ano == '' and ordenar == '':
            arquivos = ''
        elif ordenar != '' and periodoEscolhido != '' and ano != '':
            #arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido,anoArquivo=ano)
            arquivos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[ano,periodoEscolhido])          
        elif periodoEscolhido == '' and ano != '' and ordenar == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano)
        elif periodoEscolhido != '' and ano == '' and ordenar == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
        elif ordenar != '' and ano == '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.order_by('titulo') 
        elif ordenar != '' and ano == '' and periodoEscolhido != '':
            arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido)   
        elif ordenar != '' and ano != '' and periodoEscolhido == '':
            arquivos = Arquivo.objects.filter(anoArquivo=ano).order_by('titulo')   
        elif formato != '':
            arquivos = Arquivo.objects.filter(formato=formato) 
    return render(request,'arquivosEnviados.html', {'arquivos':arquivos,'pHistorico':pHistorico,'anos':anos,'nome':nome,'cpf':cpf})

def visualizarArquivo(request,arquivo):
    try:
        extensoes = [".pdf", ".txt", ".png", ".jpg", ".gif", ".bmp",".mp3",".mp4",'.JPG']
        if arquivo.endswith(tuple(extensoes)):
            diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
            arquivo = open(diretorio_arquivo, 'rb') 
            abrir_Arquivo = FileResponse(arquivo)
            return abrir_Arquivo
        else:
            diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
            os.system(diretorio_arquivo)    
            os.chmod(diretorio_arquivo,stat.S_IREAD)     
            return redirect('../verBaixarArquivo')
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")      
            return redirect('../verBaixarArquivos')

def baixarArquivo(request, arquivo):
    try:
        if arquivo != '':
            diretorio_arquivo = (os.path.join(settings.MEDIA_ROOT, arquivo))
            diretorio = open(diretorio_arquivo,'rb')
            download_arquivo = HttpResponse(diretorio ,content_type="aplicacao/arquivo")
            download_arquivo ['Content-Disposition'] = "attachment; nome_arquivo=" + arquivo
            return download_arquivo
        else:
            messages.error(request,"Arquivo não encontrado")
            return redirect('verBaixarArquivos')
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")     
            return redirect('verBaixarArquivos')

def editar(request, id):
    arquivo = Arquivo.objects.filter(id=id)
    
    if 'salvar' in request.POST:
        try:
            titulo = request.POST.get('titulo')
            enderecoArquivo = request.FILES['enderecoArquivo']
            periodoHistorico = request.POST.get('periodoHistorico')
            anoArquivo = request.POST.get('anoArquivo')
            descArquivo = request.POST.get('descArquivo')
            arquivo = Arquivo.objects.get(id=id)
            Arquivo.objects.filter(id=id).update(titulo=titulo,enderecoArquivo=enderecoArquivo,periodoHistorico=periodoHistorico,anoArquivo=anoArquivo,descricao=descArquivo)
            messages.success(request, "Alterações feitas com sucesso")
            return redirect('../arquivosEnviados/'+str(arquivo.cpf))
        except MultiValueDictKeyError:
            messages.error(request,"Escolha um arquivo")
        except ValueError:
            messages.error(request, "Digite o ano do arquivo. Caso não saiba, coloque 'desconhecido' ")  
    elif 'voltar' in request.POST:
        arquivo = Arquivo.objects.get(id=id)
        return redirect('../arquivosEnviados/'+str(arquivo.cpf))
    return render(request,'editarArquivo.html',{'arquivo':arquivo})

def excluir(id):
    excluirArq = Arquivo.objects.get(id=id)
    cpf = excluirArq.cpf
    excluirArq.delete()
    return redirect('../arquivosEnviados/'+str(cpf)) 

def sair(request):
        logout(request)
        messages.success(request,"Você saiu do seu perfil")
        return HttpResponseRedirect("/")
