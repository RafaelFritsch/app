from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone


class DateInput(forms.DateInput):
    input_type = 'date'
    

class CursosForm(forms.ModelForm):
    nome = forms.CharField()
    tipo_curso = forms.ModelChoiceField(queryset=tipo_curso.objects.all())
    active = forms.BooleanField()
    
    class Meta:
        model = cad_cursos
        fields = (
            'nome',
            'tipo_curso',
            'active',
        )


class TipoCursoForm(forms.ModelForm):
    nome = forms.CharField()
    pontos = forms.IntegerField()
 
    
    class Meta:
        model = tipo_curso
        fields = (
            'nome',
            'pontos',
        )    





class MatriculasForm(forms.ModelForm):
    data_matricula = forms.DateTimeField(widget=DateInput())
    nome_aluno = forms.CharField()
    numero_ra = forms.CharField(label='RA', required=False)
    tipo_curso = forms.ModelChoiceField(queryset=tipo_curso.objects.all())
    curso = forms.ModelChoiceField(queryset=cad_cursos.objects.all())
    campanha = forms.ModelChoiceField(queryset=cad_campanhas.objects.all()) 
    valor_mensalidade = forms.DecimalField(label='R$ 1º Mens.')
    desconto_polo = forms.DecimalField(label='R$ 2º Mens.')
    desconto_total = forms.DecimalField(label='% Bolsa')
    processo_sel = forms.ModelChoiceField(queryset=cad_processo.objects.filter(ativo=True), widget=forms.Select(attrs={'class': 'selectpicker'}), label='Processo Seletivo')
    arquivos = forms.FileField(label='Enviar Comprovante', required=False, widget=forms.ClearableFileInput())
    
    def label_from_instance(self, obj):
        return f"{obj.numero_processo} / {obj.ano_processo}"

    class Meta:
        model = Matriculas
        fields = (
            'processo_sel',
            'data_matricula',
            'nome_aluno',
            'numero_ra',
            'tipo_curso',
            'curso',
            'campanha',
            'valor_mensalidade',
            'desconto_polo',
            'desconto_total',
            'arquivos',
        )
        
    def __init__(self, *args, **kwargs):
        super(MatriculasForm, self).__init__(*args, **kwargs)
        self.fields['processo_sel'].label_from_instance = self.label_from_instance
        self.fields['curso'].queryset = cad_cursos.objects.none()  
        self.fields['processo_sel'].widget.attrs['class'] = 'selectpicker'
        self.fields['curso'].widget.attrs['data-live-search'] = True # Adicionar atributo data-live-search para habilitar a pesquisa em campos de seleção
        
        if 'tipo_curso' in self.data: # Filtrar opções do campo curso dinamicamente com base no tipo de curso
            try:
                tipo_curso_id = int(self.data.get('tipo_curso'))
                self.fields['curso'].queryset = cad_cursos.objects.filter(tipo_curso_id=tipo_curso_id)
            except (ValueError, TypeError):
                pass      
        
        if 'instance' in kwargs:  ## carrega corretamentE os campos no update
            instance = kwargs['instance']
            if instance:
                self.fields['tipo_curso'].queryset = tipo_curso.objects.filter(id=instance.tipo_curso.id)
                self.fields['curso'].queryset = cad_cursos.objects.filter(tipo_curso_id=instance.tipo_curso.id)


ESTADOS_UF = (
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
)


class PoloForm(forms.ModelForm):
    nome = forms.CharField()
    estado = forms.CharField(widget=forms.Select(choices=ESTADOS_UF))
    active = forms.BooleanField()
    
    
    class Meta:
        model = cad_polos
        fields = (
            'nome',
            'estado',
            'active',
        )
        labels = {
            'active': 'Ativo',
        }

        

class CampanhaForm(forms.ModelForm):
    nome = forms.CharField()
    data_inicio = forms.DateField(widget=DateInput())
    data_fim = forms.DateField(widget=DateInput())
    active = forms.BooleanField()
    
    class Meta:
        model = cad_campanhas
        fields = (
            'nome',
            'data_inicio',
            'data_fim',
            'active',
        )
       
        
class UserForm(UserCreationForm):
    choices_cargo = (('U', 'USUARIO'), ('A', 'ADMINISTRADOR'))
    polo = forms.ModelChoiceField(queryset=cad_polos.objects.all())
    cargo = forms.ChoiceField(choices=choices_cargo, widget=forms.Select(attrs={'class': 'form-control'}))  # Adicionei o widget e a classe 'form-control'
    class Meta:
         model = User
         fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'polo', 'cargo')  # Adicionei 'polo' e 'cargo'
         labels = {
             'first_name': 'Nome',
             'last_name': 'Sobrenome',
             'username': 'Nome de Usuário',
             'email': 'Email',
             'password1': 'Senha',
             'password2': 'Confirme a Senha',
             'polo': 'Polo',
             'cargo': 'Cargo',
         }

    
    def get_absolute_url(self):
        return reverse("matriculas:user_update", kwargs={'id': self.id}) #Direciona para a url de edição
 
class UsuarioForm(forms.Form):
    usuarios = forms.ModelChoiceField(queryset=UserProfile.objects.all(),required=False, label='Escolha o usuário')   


class CustomUserCreationForm(UserCreationForm):
   
    polo = forms.ModelChoiceField(queryset=cad_polos.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email','username', 'password1', 'password2', 'polo')
        
    
NUMERO_PROC_CHOICES = (
    ('51', '51'),
    ('52', '52'),
    ('53', '53'),
    ('54', '54'),

    )   
    
              
class ProcessoForm(forms.ModelForm):
    numero_processo = forms.CharField(widget=forms.Select(choices=NUMERO_PROC_CHOICES))
    ano_processo = forms.IntegerField()
    data_inicial_processo = forms.DateTimeField(widget=DateInput())
    data_final_processo = forms.DateTimeField(widget=DateInput())
    ativo = forms.BooleanField(required=False)
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['ano_processo'].initial = datetime.now().year
        self.fields['ativo'].initial = True
    
    def clean(self):
        cleaned_data = super().clean()
        numero_processo = cleaned_data.get('numero_processo')
        ano_processo = cleaned_data.get('ano_processo')

        # Verifica se o processo existe
        if not cad_processo.objects.filter(numero_processo=numero_processo, ano_processo=ano_processo).exists():
            raise forms.ValidationError("O processo selecionado não é válido.")
    
    class Meta:
        model = cad_processo
        fields = (
            'numero_processo',
            'ano_processo',
            'data_inicial_processo',
            'data_final_processo',
            'ativo',
        )
 
class RelatorioSpaceForm(forms.Form):
    processo = forms.ModelChoiceField(
        queryset=cad_processo.objects.all(),
        label='Selecione o Processo',
        to_field_name='id',  # Necessário para garantir que o valor do campo seja o ID do processo
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personaliza a representação do objeto no campo de seleção
        self.fields['processo'].label_from_instance = lambda obj: f"{obj.numero_processo} / {obj.ano_processo}"
    
class DateRangeForm(forms.Form): #usado no relatorio financeiro
    data_inicial = forms.DateField(label='Data Inicial', widget=forms.DateInput(attrs={'type': 'date'}))
    data_final = forms.DateField(label='Data Final', widget=forms.DateInput(attrs={'type': 'date'}))
    
    
class DateSelectForm(forms.Form): #Usado no movimento diario
    selected_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}), initial=timezone.now().date(), required=False, label="")
