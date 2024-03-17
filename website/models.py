from django.db import models
 
class Usuario(models.Model):
    cpf = models.BigIntegerField(primary_key=True)
    nome = models.CharField(max_length=30)
    sobrenome = models.CharField(max_length=30)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    celular = models.CharField(max_length=15)
    sexo = models.CharField(max_length=15)
    dataNascimento = models.DateField()
    senha = models.CharField(max_length=50)
    class Meta:
        db_table = 'usuario'

class Cliente(models.Model):
    cpf = models.BigIntegerField(primary_key=True)
    nome = models.CharField(max_length=30)
    sobrenome = models.CharField(max_length=30)
    email = models.EmailField()
    telefone = models.CharField(max_length=30)
    celular = models.CharField(max_length=30)
    endereco = models.CharField(max_length=200)
    cidade = models.CharField(max_length=20)
    sexo = models.CharField(max_length=15)
    dataNascimento = models.DateField()
    class Meta:
        db_table = 'cliente'
        
class Fornecedor(models.Model):
    cnpj = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=100)
    ramo = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=50)
    estado = models.CharField(max_length=30)
    class Meta:
        db_table='fornecedor'

class Produto(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    marca = models.CharField(max_length=50)
    peso = models.IntegerField()
    medida = models.CharField(max_length=5)
    preco = models.FloatField()
    descricao = models.TextField()
    class Meta:
        db_table = 'produto'

class comprarProd(models.Model):
    id = models.AutoField(primary_key=True)
    cpfCliente = models.ForeignKey(Cliente,on_delete=models.CASCADE)
    idProduto = models.ForeignKey(Produto,on_delete=models.CASCADE)
    quantProd = models.IntegerField()
    class Meta:
        db_table = 'clienteProd'

class loteProd(models.Model):
    id = models.AutoField(primary_key=True)
    idProduto = models.ForeignKey(Produto,on_delete=models.CASCADE)
    idFornecedor = models.ForeignKey(Fornecedor,on_delete=models.CASCADE)
    quanti = models.IntegerField()
    fabri = models.DateField()
    vali = models.DateField()
    class Meta:
        db_table = 'loteProd'


