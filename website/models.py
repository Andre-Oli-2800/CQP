from django.db import models
 
class Usuario(models.Model):
    cpf = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=30)
    sobrenome = models.CharField(max_length=30)
    email = models.EmailField()
    sexo = models.CharField(max_length=15)
    dataNascimento = models.DateField()
    senha = models.CharField(max_length=50)
    class Meta:
        db_table = 'cadastro'
        
class Arquivo(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    enderecoArquivo = models.FileField(upload_to="", null=True, blank=True)
    periodoHistorico = models.CharField(max_length=100)
    anoArquivo = models.IntegerField()
    descricao = models.TextField()
    cpf = models.CharField(max_length=11)
    #class Meta:
    #    db_table = 'arquivo'

