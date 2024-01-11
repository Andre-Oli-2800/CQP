import os
import stat
from django.db import IntegrityError
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from website.models import Usuario, Arquivo
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
                                    usuarioCriado = Usuario.objects.create(cpf=cpf,nome=nome,sobrenome=sobrenome,email=email,sexo=sexo,dataNascimento=dataNascimento,senha=senha)                      
                                    autenticarUsuario = User(username=email, password=senha)    
                                    autenticarUsuario.save() 
                                    messages.success(request,"Conta criada com sucesso")
                                    return redirect('/login') 
                                except (IntegrityError):
                                    messages.error(request, 'Já existe um usuário cadastrado com esse CPF')
                    else:
                        messages.error(request,"As senhas estão diferentes")               
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
                        return redirect('/pagina_inicial/'+str(cpf))
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
        elif 'enviarArquivo' in request.POST:
            return redirect('../enviarArquivo/'+str(cpf))
        elif 'verbaiArquivo' in request.POST:
            return redirect('../verBaixarArquivos/'+str(cpf))
        elif 'arqEnviados' in request.POST:
            return redirect('../arquivosEnviados/'+str(cpf))
        elif 'editarConta' in request.POST:
            return redirect('../editarPerfil/'+str(cpf))
    except Usuario.DoesNotExist:
        messages.error(request,'Esse usuário não existe')
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
            arq.descricao = request.POST.get('descArquivo')
            arq.cpf = cpf
            arq.save()
            messages.success(request,'Arquivo enviado com sucesso')
        except MultiValueDictKeyError:
            messages.error(request,"Escolha um arquivo")
            return redirect('../enviarArquivo/'+str(cpf))
        except ValueError:
            messages.error(request, "Digite o ano do arquivo. Caso não saiba, coloque 'desconhecido' ")  
            return redirect('../enviarArquivo/'+str(cpf))
    return render(request,'enviarArquivo.html',{'cpf':cpf})

def verBaixarArquivos(request,cpf):  
    arquivos = Arquivo.objects.all()
    arqs = Arquivo.objects.values_list('anoArquivo', flat=True).distinct()
    pHistorico = Arquivo.objects.values_list('periodoHistorico', flat=True).distinct()
    anos = Arquivo.objects.raw("SELECT id,titulo,periodoHistorico,anoArquivo,descricao FROM site.website_arquivo GROUP BY anoArquivo") 
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'Pesquisar' in request.POST:
        periodoEscolhido = request.POST.get('periodoHistorico')
        anoSelecionado = request.POST.get('ano')
        formato = request.POST.get('formato')
        ordenar = request.POST.get('ordenar') 
        if periodoEscolhido == '' and anoSelecionado == '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.all()
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.filter(anoArquivo=anoSelecionado)
        elif periodoEscolhido == '' and anoSelecionado == '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.order_by('titulo') 
        elif periodoEscolhido == '' and anoSelecionado == '' and ordenar == '' and formato != '':   
            arquivos = []
            arquivosExibidos = Arquivo.objects.all()
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido != '' and anoSelecionado != '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido,anoArquivo=anoSelecionado)
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido) 
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar == '' and formato != '': #Testar  
            arquivos = []
            arquivosExibidos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.filter(anoArquivo=anoSelecionado).order_by('titulo')  
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar == '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.filter(anoArquivo=anoSelecionado)
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido == '' and anoSelecionado == '' and ordenar != '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.order_by('titulo')  
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar != '' and formato != '':#Testar
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s order by titulo',[anoSelecionado])              
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar != '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where periodoHistorico order by titulo',[periodoEscolhido])              
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)    
        elif periodoEscolhido != '' and anoSelecionado != '' and ordenar == '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico',[anoSelecionado,periodoEscolhido])              
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo) 
        elif periodoEscolhido != '' and anoSelecionado != '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[anoSelecionado,periodoEscolhido])          
        elif  periodoEscolhido != '' and anoSelecionado != '' and ordenar != '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[anoSelecionado,periodoEscolhido])          
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
    if 'sair' in request.POST:
         return redirect('sair')
    return render(request, 'verBaixarArquivos.html', {'arquivos' : arquivos,'pHistorico':pHistorico,'anos':anos,'cpf':cpf})

def arquivosEnviados(request,cpf):
    arquivos = Arquivo.objects.filter(cpf=cpf)
    if arquivos != ' ':
        nome = 'Título'
    pHistorico = Arquivo.objects.filter(cpf=cpf).values_list('periodoHistorico', flat=True).distinct()
    anos = Arquivo.objects.filter(cpf=cpf).values_list('anoArquivo', flat=True).distinct()
    if 'Sair' in request.POST:
        return redirect('sair') 
    elif 'Pesquisar' in request.POST:
        periodoEscolhido = request.POST.get('periodoHistorico')
        anoSelecionado = request.POST.get('ano')
        formato = request.POST.get('formato')
        ordenar = request.POST.get('ordenar')
        if periodoEscolhido == '' and anoSelecionado == '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.filter(cpf=cpf)
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.filter(anoArquivo=anoSelecionado)
        elif periodoEscolhido == '' and anoSelecionado == '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.order_by('titulo') 
        elif periodoEscolhido == '' and anoSelecionado == '' and ordenar == '' and formato != '':   
            arquivos = []
            arquivosExibidos = Arquivo.objects.filter(cpf=cpf)
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido != '' and anoSelecionado != '' and ordenar == '' and formato == '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido,anoArquivo=anoSelecionado)
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.order_by('titulo').filter(periodoHistorico=periodoEscolhido) 
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar == '' and formato != '': #Testar  
            arquivos = []
            arquivosExibidos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.filter(anoArquivo=anoSelecionado).order_by('titulo')  
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar == '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.filter(anoArquivo=anoSelecionado)
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido == '' and anoSelecionado == '' and ordenar != '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.order_by('titulo')  
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido == '' and anoSelecionado != '' and ordenar != '' and formato != '':#Testar
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s order by titulo',[anoSelecionado])              
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)
        elif periodoEscolhido != '' and anoSelecionado == '' and ordenar != '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where periodoHistorico order by titulo',[periodoEscolhido])              
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)    
        elif  periodoEscolhido != '' and anoSelecionado != '' and ordenar == '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico',[anoSelecionado,periodoEscolhido])              
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo) 
        elif  periodoEscolhido != '' and anoSelecionado != '' and ordenar != '' and formato == '':
            arquivos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[anoSelecionado,periodoEscolhido])          
        elif  periodoEscolhido != '' and anoSelecionado != '' and ordenar != '' and formato != '':
            arquivos = []
            arquivosExibidos = Arquivo.objects.raw('select * from website_arquivo where anoArquivo = %s and periodoHistorico = %s order by titulo',[anoSelecionado,periodoEscolhido])          
            for arquivo in arquivosExibidos:
                nomeArquivo, extensao = os.path.splitext(str(arquivo.enderecoArquivo))
                if extensao == formato:
                    arquivos.append(arquivo)  
    return render(request,'arquivosEnviados.html', {'arquivos':arquivos,'pHistorico':pHistorico,'anos':anos,'nome':nome,'cpf':cpf})

def visualizarArquivo(request,arquivo):
    try:
        extensoes = [".pdf", ".txt", ".png", ".jpg", ".gif", ".bmp",".mp3",".mp4",'.JPG',"webp",".jpeg"]
        if arquivo.endswith(tuple(extensoes)):
            diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
            arquivo = open(diretorio_arquivo, 'rb') 
            abrir_Arquivo = FileResponse(arquivo)
            return abrir_Arquivo
        else:
            diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
            os.system(diretorio_arquivo)    
            os.chmod(diretorio_arquivo,stat.S_IREAD)     
            return redirect(request.META.get('HTTP_REFERER'))
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")      
            return redirect(request.META.get('HTTP_REFERER'))

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
            return redirect(request.META.get('HTTP_REFERER'))
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")     
            return redirect(request.META.get('HTTP_REFERER'))

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
            arquivoVelho = str(arquivo.enderecoArquivo)
            diretorio_arquivoVelho = (os.path.join(settings.MEDIA_ROOT, arquivoVelho))
            os.remove(diretorio_arquivoVelho)
            arq = request.FILES['enderecoArquivo']
            fs = FileSystemStorage()
            nomeArquivo = fs.save(arq.titulo, arq)
            arquivoEnviado = fs.url(nomeArquivo)
            Arquivo.objects.filter(id=id).update(titulo=titulo,enderecoArquivo=enderecoArquivo,periodoHistorico=periodoHistorico,anoArquivo=anoArquivo,descricao=descArquivo)
            messages.success(request, "Alterações feitas com sucesso")
            return redirect('../arquivosEnviados/'+str(arquivo.cpf))
        except (MultiValueDictKeyError,UnboundLocalError):
            titulo = request.POST.get('titulo')
            periodoHistorico = request.POST.get('periodoHistorico')
            anoArquivo = request.POST.get('anoArquivo')
            descArquivo = request.POST.get('descArquivo')
            arquivo = Arquivo.objects.get(id=id)
            Arquivo.objects.filter(id=id).update(titulo=titulo,periodoHistorico=periodoHistorico,anoArquivo=anoArquivo,descricao=descArquivo)
            messages.success(request, "Alterações feitas com sucesso")
            return redirect('../arquivosEnviados/'+str(arquivo.cpf))
        except ValueError:
            messages.error(request, "Digite o ano do arquivo. Caso não saiba, coloque 'desconhecido' ")  
    elif 'voltar' in request.POST:
        arquivo = Arquivo.objects.get(id=id)
        return redirect('../arquivosEnviados/'+str(arquivo.cpf))
    return render(request,'editarArquivo.html',{'arquivo':arquivo})

def excluir(request, id):
    excluirArq = Arquivo.objects.get(id=id)
    arquivo = str(excluirArq.enderecoArquivo)
    cpf = excluirArq.cpf
    excluirArq.delete()
    diretorio_arquivo = (os.path.join(settings.MEDIA_ROOT, arquivo))
    os.remove(diretorio_arquivo)
    messages.error(request,"Arquivo exluído com sucesso")
    return redirect('../arquivosEnviados/'+str(cpf)) 

def sair(request):
    logout(request)
    messages.success(request,"Você saiu do seu perfil")
    return HttpResponseRedirect("/")
