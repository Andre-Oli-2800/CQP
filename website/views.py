import os
import stat
import subprocess as sp
from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from website.models import Usuario, Arquivo
from django.contrib import messages

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
                Usuario.objects.create(cpf=cpf,nome=nome, sobrenome=sobrenome,
                                       email=email,sexo=sexo,dataNascimento=dataNascimento,senha=senha)
                messages.success(request,"Conta criada com sucesso")
                return redirect('/login') 
            else:
                messages.error(request,"As senhas estão diferentes")               
        return redirect("/cadastro")
    elif 'login' in request.POST:
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
        return redirect('verBaixarArquivos')
    elif 'arqEnviados' in request.POST:
        return redirect('../arquivosEnviados/'+str(cpf))
    return render(request,'pagina_inicial.html')

def editarPerfil(request,cpf):
    if 'salvar' in request.POST:
        nome = request.POST.get("nome")
        sobrenome = request.POST.get("sobrenome")
        email = request.POST.get("email")
        sexo = request.POST.get("sexo")
        dataNascimento = request.POST.get("dtNascimento")
        senha = request.POST.get("senha")
        confSenha = request.POST.get("confSenha")
        if nome == '' or sobrenome == '' or email == '' or sexo == '' or dataNascimento == '' or senha == '' or confSenha == '':      
            messages.error(request,'Preencha todos os campos')
            return redirect('cadastro')
        else:
            if senha == confSenha:
                Usuario.objects.filter(cpf=cpf).update(nome=nome, sobrenome=sobrenome,
                                       email=email,sexo=sexo,dataNascimento=dataNascimento,senha=senha)
                messages.success(request,"Perfil editado com sucesso sucesso")
                return redirect('/pagina_inicial') 

def enviarArquivo(request,cpf):
    if request.method == 'POST':
        arq = Arquivo()
        arq.titulo = request.POST.get('titulo')
        arq.enderecoArquivo = request.FILES['enderecoArquivo']
        arq.periodoHistorico = request.POST.get('periodoHistorico')
        arq.anoArquivo = request.POST.get('anoArquivo')
        arq.descArquivo = request.POST.get('descArquivo')
        arq.cpf = cpf
        arq.save()
        messages.success(request,'Arquivo enviado com sucesso')
    return render(request,'enviarArquivo.html')

def verBaixarArquivos(request):
    arquivos = Arquivo.objects.all()
    pHistorico = Arquivo.objects.values_list('periodoHistorico', flat=True).distinct()
    if 'Pesquisar' in request.POST:
        periodoEscolhido = request.POST.get('periodoHistorico')
        formato = request.POST.get('formato')
        ordenar = request.POST.get('ordenar')

        if periodoEscolhido != '':

            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido)
        elif ordenar != '':
            arquivos = Arquivo.objects.order_by('titulo') 
        elif ordenar != '' and periodoEscolhido != '':
            arquivos = Arquivo.objects.filter(periodoHistorico=periodoEscolhido).order_by('titulo')     
        if formato != '':
                    arquivos = Arquivo.objects.filter(formato=formato) 
    if 'visualizar' in request.POST:
        return redirect('visualizarArquivos')
    elif 'baixar' in request.POST:
        return redirect('baixarArquivos')
    return render(request, 'verBaixarArquivos.html', {'arquivos' : arquivos,'pHistorico':pHistorico})
    
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


def arquivosEnviados(request,cpf):
    arquivos = Arquivo.objects.filter(cpf=cpf)
    if 'Teste' in request.POST:       
        arquivos = Arquivo.objects.filter()          
    if 'salvar' in request.POST:
        return redirect('editarArquivo')
    return render(request,'arquivosEnviados.html', {'arquivos':arquivos})

def editar(request, id):
    arquivo = Arquivo.objects.filter(id=id)
    
    if 'salvar' in request.POST:
        titulo = request.POST.get('titulo')
        enderecoArquivo = request.FILES['enderecoArquivo']
        periodoHistorico = request.POST.get('periodoHistorico')
        anoArquivo = request.POST.get('anoArquivo')
        descArquivo = request.POST.get('descArquivo')
        arquivo = Arquivo.objects.get(id=id)
        Arquivo.objects.filter(id=id).update(titulo=titulo,enderecoArquivo=enderecoArquivo,periodoHistorico=periodoHistorico,anoArquivo=anoArquivo,descricao=descArquivo)
        messages.success(request, "Alterações feitas com sucesso")
        return redirect('../arquivosEnviados/'+str(arquivo.cpf))
    return render(request,'editarArquivo.html',{'arquivo':arquivo})

def excluir(id):
    excluirArq = Arquivo.objects.get(id=id)
    cpf = excluirArq.cpf
    excluirArq.delete()
    return redirect('../arquivosEnviados/'+str(cpf)) 

def sair(request):
        #logout(request)
        messages.success(request,"Você saiu do seu perfil")
        return HttpResponseRedirect("/")
