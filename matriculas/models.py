from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count
from smart_selects.db_fields import ChainedForeignKey
from django.db.models.functions import ExtractMonth
from datetime import timedelta, date



# Create your models here.
def get_month_range(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        # Adiciona um mês
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)


class cad_polos(models.Model):
    ESTADOS_UF = [
        ('AC', 'ACRE'),
        ('AL', 'ALAGOAS'),
        ('AP', 'AMAPÁ'),
        ('AM', 'AMAZONAS'),
        ('BA', 'BAHIA'),
        ('CE', 'CEARÁ'),
        ('DF', 'DISTRITO FEDERAL'),
        ('ES', 'ESPÍRITO SANTO'),
        ('GO', 'GOIÁS'),
        ('MA', 'MARANHÃO'),
        ('MT', 'MATO GROSSO'),
        ('MS', 'MATO GROSSO DO SUL'),
        ('MG', 'MINAS GERAIS'),
        ('PA', 'PARÁ'),
        ('PB', 'PARAÍBA'),
        ('PR', 'PARANÁ'),
        ('PE', 'PERNAMBUCO'),
        ('PI', 'PIAUÍ'),
        ('RJ', 'RIO DE JANEIRO'),
        ('RN', 'RIO GRANDE DO NORTE'),
        ('RS', 'RIO GRANDE DO SUL'),
        ('RO', 'RONDÔNIA'),
        ('RR', 'RORAIMA'),
        ('SC', 'SANTA CATARINA'),
        ('SP', 'SÃO PAULO'),
        ('SE', 'SERGIPE'),
        ('TO', 'TOCANTINS')
    ]
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=ESTADOS_UF)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='polos')
    
    class Meta:
        db_table = 'polos'
        
    def __str__(self):
        return self.nome
    
    def get_nome_polo(self):
        return self.nome
    
    def get_absolute_url(self):
        return reverse("matriculas:polo_update", kwargs={'id': self.id}) #Direciona para a url de edição
    
    def get_delete_url(self):
        return reverse("matriculas:polo_delete", kwargs={'id': self.id})# Exclui o resgistro

class tipo_curso(models.Model):
    nome = models.CharField(max_length=100)
    pontos = models.IntegerField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipo_curso'
        
    def __str__(self):
        return self.nome
    
    def get_data_create_tp(self):
        return self.create_date.strftime('%d/%m/%Y')
    
    def get_data_update_tp(self):
        return self.update_date.strftime('%d/%m/%Y')
    
    def get_absolute_url(self):
        return reverse("matriculas:tipo_curso_update", kwargs={'id': self.id}) #Direciona para a url de edição
    
    def get_delete_url(self):
        return reverse("matriculas:tipo_curso_delete", kwargs={'id': self.id})# Exclui o resgistro


class cad_cursos(models.Model):
    nome = models.CharField(max_length=100)
    tipo_curso = models.ForeignKey(tipo_curso, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'cursos'
        
    def __str__(self):
        return self.nome
    
    def get_data_create_curso(self):
        return self.create_date.strftime('%d/%m/%Y')
    
    def get_data_update_curso(self):
        return self.update_date.strftime('%d/%m/%Y')
    
    def get_absolute_url(self):
        return reverse("matriculas:curso_update", kwargs={'id': self.id}) #Direciona para a url de edição
    
    def get_delete_url(self):
        return reverse("matriculas:curso_delete", kwargs={'id': self.id})# Exclui o resgistro

class cad_campanhas(models.Model):
    nome = models.CharField(max_length=100)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'campanhas'
        
    def __str__(self):
        return self.nome
    
    def get_data_inicio_camp(self):
        return self.data_inicio.strftime('%d/%m/%Y')
    
    def get_data_fim_camp(self):
        return self.data_fim.strftime('%d/%m/%Y')
    
    def get_absolute_url(self):
        return reverse("matriculas:campanha_update", kwargs={'id': self.id}) #Direciona para a url de edição
    
    def get_delete_url(self):
        return reverse("matriculas:campanha_delete", kwargs={'id': self.id})# Exclui o resgistro
    




    


#Adicionar o campo polo no cadastro do usuario    
#
class UserProfile(models.Model):
    choices_cargo = (('U', 'USUARIO'), ('A', 'ADMINISTRADOR'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    polo = models.ForeignKey(cad_polos, on_delete=models.SET_NULL, null=True, blank=True)
    cargo = models.CharField(max_length=1, choices=choices_cargo)
    
    def __str__(self):
        return self.user.username
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
   

class cad_processo(models.Model):
    
    NUMERO_PROCESSO_CHOICES = (
    ('51', '51'),
    ('52', '52'),
    ('53', '53'),
    ('54', '54'),
    )   
    
    numero_processo =  models.CharField(max_length=2, choices=NUMERO_PROCESSO_CHOICES)
    ano_processo = models.CharField(max_length=4)
    data_inicial_processo = models.DateTimeField()
    data_final_processo = models.DateTimeField()
    ativo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'processo'
        
    def __str__(self):
        return self.numero_processo 
    def get_data_inicial(self):
        return self.data_inicial_processo.strftime('%d/%m/%Y')
    def get_data_final(self):
        return self.data_final_processo.strftime('%d/%m/%Y')
    def get_absolute_url(self):
        return reverse("matriculas:processo_update", kwargs={'id': self.id}) #Direciona para a url de edição
    def get_delete_url(self):
        return reverse("matriculas:processo_delete", kwargs={'id': self.id})# Exclui o resgistro
    def get_month_range(self):
        return get_month_range(self.data_inicial_processo, self.data_final_processo)
    
    
class Matriculas(models.Model):
    id = models.AutoField(primary_key=True)
    data_matricula = models.DateTimeField()
    nome_aluno = models.CharField(max_length=200)
    numero_ra = models.CharField(max_length=12)
    tipo_curso = models.ForeignKey(tipo_curso, on_delete=models.CASCADE, null=True)
    curso = models.ForeignKey(cad_cursos, on_delete=models.CASCADE)
    campanha = models.ForeignKey(cad_campanhas, on_delete=models.CASCADE) 
    valor_mensalidade = models.DecimalField(max_digits=6, decimal_places=2)
    desconto_polo = models.DecimalField(max_digits=6, decimal_places=2)
    desconto_total = models.IntegerField(blank=False)
    pontos_trocados = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    comprovante = models.ImageField(upload_to='comprovantes/', blank=True, null=True)
    active = models.BooleanField(default=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT,related_name='matriculas')
    processo_sel = models.ForeignKey(cad_processo, on_delete=models.CASCADE)
    arquivos = models.FileField(upload_to='arquivos_matricula/', blank=True, null=True)
   
            
    class Meta:
        db_table = 'matricula'
        
    def __str__(self):
        #return self.nome_aluno
        return f"{self.processo_sel.numero_processo} - {self.processo_sel.ano_processo} - {self.nome_aluno}"
    
    def get_data_matricula(self):
        return self.data_matricula.strftime('%d/%m/%Y')
    
    def get_absolute_url(self):
        return reverse("matriculas:matriculas_update", kwargs={'id': self.id}) #Direciona para a url de edição
    
    def get_delete_url(self):
        return reverse("matriculas:matriculas_delete", kwargs={'id': self.id})# Exclui o resgistro
    
    def delete(self, *args, **kwargs):
        # Excluir arquivos associados antes de chamar o método delete da superclasse
        if self.comprovante:
            self.comprovante.delete()
        if self.arquivos:
            self.arquivos.delete()

        super().delete(*args, **kwargs)
