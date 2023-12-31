
from django.db import models
from django.db.models import Count, Sum, Min, Max, Q, Subquery, OuterRef
from django.db.models.aggregates import Count, Sum 
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.views import View
from .models import *
from .forms import *
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
import os
from django.contrib.auth.models import Group
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import RedirectView, DetailView
from django.http import HttpResponse, JsonResponse



####################### LIST VIEWS ######################################################


class MatriculasListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/matriculas_list.html'
    login_url = 'login'
    paginate_by = 10
    model = Matriculas
    def get_queryset(self):
        
        name = self.request.GET.get("name")
        if name:
            object_list = self.model.objects.filter(nome_aluno__icontains=name).filter(usuario=self.request.user).order_by('-data_matricula') # Vizualiza somente os registros que o user criou
        else:
            object_list = self.model.objects.all().filter(usuario=self.request.user).order_by('-data_matricula') # Vizualiza somente os registros que o user criou
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtém o processo ativo
        processo_ativo = cad_processo.objects.filter(ativo=True).first()

        # Adiciona o objeto processo_ativo ao contexto
        context['cad_processo'] = processo_ativo

        return context

    
class MatriculaFileView(View):
    model = Matriculas

    def get(self, request, pk, *args, **kwargs):
        matricula = get_object_or_404(self.model, pk=pk)
        file_path = matricula.arquivos.path

        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/octet-stream")
                response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
                return response
        else:
            raise Http404
    

## Listar Users 

class UserListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/user_list.html'
    model = User
    queryset = User.objects.all()
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('name', None)

        if search_term:
            # Filtra por nome do usuário
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term) |
                Q(username__icontains=search_term) | Q(email__icontains=search_term)
            )

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona os polos associados a cada usuário ao contexto
        context['polos'] = cad_polos.objects.filter(users__in=context['user_list'])
        
        # Adiciona os cargos de cada usuário ao contexto
        user_profiles = UserProfile.objects.filter(user__in=context['user_list'])
        context['cargos'] = {profile.user_id: profile.cargo for profile in user_profiles}
        
        # Adiciona os rankings de cada usuário ao contexto
        context['rankings'] = {profile.user_id: profile.ranking for profile in user_profiles}

        return context
    
    
class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = 'matriculas/user_profile.html'
    queryset = User.objects.all()
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user  # Assume que o perfil do usuário está vinculado ao UserProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Informações específicas do usuário logado
        user = self.request.user
        context['nome'] = user.get_full_name()
        context['usuario'] = user.username
        context['email'] = user.email

        # Informações adicionais (polo, cargo, ranking)
        try:
            # Se UserProfile não estiver configurado para ser estendido
            # com um modelo OneToOneField para User, ajuste essa parte
            user_profile = UserProfile.objects.get(user=user)
            context['polo'] = user_profile.polo  # Ajuste conforme necessário
            context['cargo'] = user_profile.cargo
            context['ranking'] = user_profile.ranking
            
            # Gráfico de barras
            matriculas_por_mes = self.get_matriculas_por_mes(user)
            context['matriculas_por_mes'] = matriculas_por_mes
           
            
        except UserProfile.DoesNotExist:
            # Lidere com o caso em que UserProfile não existe para o usuário
            context['polo'] = None
            context['cargo'] = None
            context['ranking'] = None

        return context
    
    def get_matriculas_por_mes(self, user):
        # Obtenha as matrículas do usuário
        matriculas = Matriculas.objects.filter(usuario=user)

        # Conte as matrículas por mês
        matriculas_por_mes = {}
        for matricula in matriculas:
            mes_ano = matricula.data_matricula.strftime("%Y-%m")
            matriculas_por_mes[mes_ano] = matriculas_por_mes.get(mes_ano, 0) + 1

        return matriculas_por_mes



class CampanhaListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/campanha_list.html'
    model = cad_campanhas
    queryset = cad_campanhas.objects.all().order_by('-data_fim')
    paginate_by = 8
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')

        if search_query:
            # Filtra curso com base no nome
            queryset = queryset.filter(nome__icontains=search_query)

        return queryset

class CursoListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/curso_list.html'
    model = cad_cursos
    queryset = cad_cursos.objects.all()
    paginate_by = 50
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')

        if search_query:
            # Filtra curso com base no nome
            queryset = queryset.filter(nome__icontains=search_query)

        return queryset
    
class PoloListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/polo_list.html'
    model = cad_polos
    queryset = cad_polos.objects.all().order_by('nome')
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')

        if search_query:
            # Filtra polos com base no nome
            queryset = queryset.filter(nome__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona a query de busca ao contexto
        context['search_query'] = self.request.GET.get('name', '')

        return context
    
class TipoCursoListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/tipo_curso_list.html'
    model = tipo_curso
    queryset = tipo_curso.objects.all().order_by('nome')
    paginate_by = 8
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')

        if search_query:
            # Filtra curso com base no nome
            queryset = queryset.filter(nome__icontains=search_query)

        return queryset

#TODO: Criar view para ver as metas inativas
#TODO: Criar view para ver os checkpoints inativos   
class ProcessoListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/processo_list.html'
    model = cad_processo
    queryset = cad_processo.objects.all().order_by('-data_final_processo')
    paginate_by = 8
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')

        if search_query:
            # Filtra processo com base no número ou ano
            queryset = queryset.filter(numero_processo__icontains=search_query) | queryset.filter(ano_processo__icontains=search_query)

        return queryset
    
class SpacePointListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/spacepoint_list.html'
    model = cad_spacepoint
    queryset = cad_spacepoint.objects.all().order_by('-data_spacepoint')
    paginate_by = 8
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')
        queryset = queryset.filter(id_processos__ativo=True)

        if search_query:
            # Filtra space point com base no nome
            queryset = queryset.filter(nome__icontains=search_query)

        return queryset

class MetasListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/metas_list.html'
    model = Metas
    queryset = Metas.objects.all()
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')
        queryset = queryset.filter(processo__ativo=True)
        if search_query:
            # Filtra metas com base no nome
            queryset = queryset.filter(processo__numero_processo__icontains=search_query)

        return queryset


################  NEW VIEWS ######################################################

class MatriculasNewView(LoginRequiredMixin,CreateView):  # Criar novo registro
    template_name = 'matriculas/matriculas_new.html'
    form_class = MatriculasForm
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()  
        return render(request, self.template_name, {'form': form})
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        
        # Obtém o objeto tipo_curso a partir do ID
        tipo_curso_id = form.cleaned_data['tipo_curso'].id

        tipo_curso_obj = get_object_or_404(tipo_curso, id=tipo_curso_id)
        
        # Atribui o objeto tipo_curso ao campo no modelo
        form.instance.tipo_curso = tipo_curso_obj

        # Atribui o objeto curso ao campo no modelo
        form.instance.curso = form.cleaned_data['curso']

        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('matriculas:matriculas_list')
    

    
def get_cursos(request):
    tipo_curso_id = request.GET.get('tipo_curso')
    cursos = cad_cursos.objects.filter(tipo_curso_id=tipo_curso_id).values('id', 'nome')
    cursos_list = list(cursos)
    return JsonResponse(cursos_list, safe=False)

   

class UserNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/user_new.html'
    form_class = UserForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user_instance = form.instance
        selected_polo = form.cleaned_data['polo']
        selected_cargo = form.cleaned_data['cargo'] 
        
        # Se o cargo for 'USUARIO', adicione as permissões necessárias
        if selected_cargo == 'U':
            # Associe o usuário ao grupo 'UsuarioGroup' (crie o grupo se necessário)
            usuario_group, created = Group.objects.get_or_create(name='UsuarioGroup')
            user_instance.groups.add(usuario_group)

        if selected_polo:
            user_profile = UserProfile.objects.create(user=user_instance, polo=selected_polo, cargo=selected_cargo)
            user_profile.save()

        return response

    def get_success_url(self) -> str:
        return reverse('matriculas:user_list')

class UserActivateView(View):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        user.is_active = True
        user.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:user_rank'))(request)

class UserDeactivateView(View):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        user.is_active = False
        user.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:user_list'))(request)

class UserActivateRanking(View):
    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        user.userprofile.ranking = True
        user.userprofile.save()
        return redirect('matriculas:user_list')

class UserDeactivateRanking(View):
    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        user.userprofile.ranking = False
        user.userprofile.save()
        return redirect('matriculas:user_list')



class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'matriculas/alterar_senha.html'

    def form_valid(self, form):
        messages.success(self.request, 'Sua senha foi alterada com sucesso.')
        return redirect('matriculas:user_profile')  # Atualize para o nome da URL correta

    def form_invalid(self, form):
        messages.error(self.request, 'Houve um erro ao alterar sua senha. Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)

def senha_alterada(request):
    messages_to_render = messages.get_messages(request)
    return render(request, 'matriculas/senha_alterada.html', {'messages': messages_to_render})


class PoloNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/polo_new.html'
    form_class = PoloForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('matriculas:polo_list')

class PoloActivateView(View):
    def get(self, request, id):
        polo = get_object_or_404(cad_polos, id=id)
        polo.active = True
        polo.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:polo_list'))(request)
class PoloDeactivateView(View):
    def get(self, request, id):
        polo = get_object_or_404(cad_polos, id=id)
        polo.active = False
        polo.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:polo_list'))(request)






class CursosNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/cursos_new.html'
    form_class = CursosForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('matriculas:curso_list')
    
class TipoCursoNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/tipo_curso_new.html'
    form_class = TipoCursoForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('matriculas:tipo_curso_list')
    
class CampanhaNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/campanha_new.html'
    form_class = CampanhaForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:campanha_list')   


class CampanhaActivateView(View):
    def get(self, request, id):
        campanha = get_object_or_404(cad_campanhas, id=id)
        campanha.active = True
        campanha.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:campanha_list'))(request)
class CampanhaDeactivateView(View):
    def get(self, request, id):
        campanha = get_object_or_404(cad_campanhas, id=id)
        campanha.active = False
        campanha.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:campanha_list'))(request)



    
class ProcessoNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/processo_new.html'
    form_class = ProcessoForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('matriculas:processo_list')
    
class ProcessoActivateView(View):
    def get(self, request, id):
        processo = get_object_or_404(cad_processo, id=id)
        processo.ativo = True
        processo.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:processo_list'))(request)
class ProcessoDeactivateView(View):
    def get(self, request, id):
        processo = get_object_or_404(cad_processo, id=id)
        processo.ativo = False
        processo.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:processo_list'))(request)
    

def lista_processos(request):
    # Filtra os processos ativos
    processos_ativos = cad_processo.objects.filter(ativo=True)
    # Passa a lista filtrada para o template
    return render (request, 'matriculas/processo_ativo.html', {'processos': processos_ativos})     



class SpacepointNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/spacepoint_new.html'
    form_class = SpacePointForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('matriculas:spacepoint_list')
    def get_initial(self):
        # Obtém o processo ativo (assumindo que você tem um campo 'ativo' em cad_processo)
        processo_ativo = cad_processo.objects.filter(ativo=True).first()

        # Inicializa o dicionário com os valores iniciais
        initial = {
            'id_processos': processo_ativo,
            'ativo': True,
        }

        return initial
    
    
class SpacepointActivateView(View):
    def get(self, request, id):
        processo = get_object_or_404(cad_processo, id=id)
        processo.ativo = True
        processo.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:spacepoint_list'))(request)
class SpacePointDeactivateView(View):
    def get(self, request, id):
        processo = get_object_or_404(cad_processo, id=id)
        processo.ativo = False
        processo.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:spacepoint_list'))(request)



class MetasNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/metas_new.html'
    form_class = MetasForm
    
    
    def get_success_url(self) -> str:
        return reverse('matriculas:metas_table')
    def get_initial(self):
        # Obtém o processo ativo (assumindo que você tem um campo 'ativo' em cad_processo)
        processo_ativo = cad_processo.objects.filter(ativo=True).first()

        # Inicializa o dicionário com os valores iniciais
        initial = {
            'processo': processo_ativo,
        }

        return initial

####################### UPDATE VIEWS ######################################################
    
class MatriculasUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/matriculas_update.html'
    form_class = MatriculasForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(Matriculas, id=id)

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        # Preenche os campos 'tipo_curso' e 'curso' com os valores atuais
        matricula = self.get_object()
        form.fields['tipo_curso'].initial = matricula.tipo_curso.id if matricula.tipo_curso else None
        form.fields['curso'].initial = matricula.curso.id if matricula.curso else None

        return form
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:matriculas_list')


class UserUpdateView(LoginRequiredMixin, UpdateView): #TODO: Ajustar para funcionar corretamente
    template_name = 'matriculas/user_update.html'
    form_class = UserForm
    model = UserProfile

    def get_object(self, queryset=None):
        return get_object_or_404(UserProfile, user__id=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = UserForm(instance=self.object.user)
        return self.render_to_response(self.get_context_data(user_form=user_form))

    def form_valid(self, form):
        user_profile = self.get_object()
        user_profile.polo = form.cleaned_data['polo']
        user_profile.cargo = form.cleaned_data['cargo']
        user_profile.ranking = form.cleaned_data['ranking']
        user_profile.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('matriculas:user_list')

    def get_success_url(self):
        return reverse_lazy('matriculas:user_list')
    
    
class CampanhaUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/campanha_new.html'
    form_class = CampanhaForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_campanhas, id=id)  # Retorna o objeto consultor a partir do id
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:campanha_list')

class CursoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/cursos_new.html'
    form_class = CursosForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_cursos, id=id)  # Retorna o objeto consultor a partir do id
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:curso_list')
    
class TipoCursoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/tipo_curso_new.html'
    form_class = TipoCursoForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(tipo_curso, id=id)  # Retorna o objeto consultor a partir do id
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:tipo_curso_list')
    
class PoloUpdateView(UpdateView):
    template_name = 'matriculas/polo_new.html'
    form_class = PoloForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_polos, id=id)  # Retorna o objeto consultor a partir do id
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:polo_list')
    
    
class ProcessoUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/processo_new.html'
    form_class = ProcessoForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_processo, id=id)  # Retorna o objeto consultor a partir do id
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:processo_list')
    
    
class SpacepointUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/spacepoint_new.html'
    form_class = SpacePointForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_spacepoint, id=id)  # Retorna o objeto consultor a partir do id
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:spacepoint_list')
    

class MetasUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/metas_new.html'
    form_class = MetasForm
    
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(Metas, id=id)  # Retorna o objeto consultor a partir do id
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('matriculas:metas_list')  
    
    

#TODO: CADASTRO DE PROCESSOS -  melhorar o layout
#TODO: PROCESSOS: Criar maneira de consultar / Editar o Processo de acordo com Numero e Ano
#TODO: PROCESSOS - na tela de cadastro de checkpoint mostrar os checkpoints cadastrados
# DELETE VIEWS ######################################################

class MatriculasDeleteView(LoginRequiredMixin, DeleteView): 
    model = Matriculas
    template_name = 'matriculas/matriculas_delete.html'

    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(Matriculas, id=id)

    def get_success_url(self):
        success_url = reverse('matriculas:matriculas_list')
        return success_url

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Verifica se o arquivo deve ser excluído
        excluir_arquivo = request.POST.get('excluir_arquivo')
        print(f"Excluir arquivo: {excluir_arquivo}")

        # Verifica se o valor de excluir_arquivo é 'True' (uma string)
        if excluir_arquivo == 'True' and self.object.comprovante:
            print("Excluindo arquivo...")
            print(f"Caminho do arquivo: {self.object.comprovante.path}")
            self.object.comprovante.delete()

        # Chama o método delete da superclasse
        response = super().delete(request, *args, **kwargs)

        # Retorna a URL de sucesso
        return response

class UserDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(UserProfile, id=id)
    
    def get_success_url(self):
        return reverse('matriculas:user_list')
   
class CampanhaDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_campanhas, id=id)
    
    def get_success_url(self):
        return reverse('matriculas:campanha_list')
    
class CursoDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_cursos, id=id)
    
    def get_success_url(self):
        return reverse('matriculas:curso_list')
    
    
class TipoCursoDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(tipo_curso, id=id)
    
    def get_success_url(self):
        return reverse('matriculas:tipo_curso_list')
    
class PoloDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_polos, id=id)
    
    def get_success_url(self):
        return reverse('matriculas:polo_list')
    
class ProcessoDeleteView(LoginRequiredMixin, DeleteView):
    def get_object(self):
        id = self.kwargs.get('id')
        return get_object_or_404(cad_processo, id=id)
    
    def get_success_url(self):
        return reverse('matriculas:processo_list')


## Consultas ######################################################################################


def RankView(request):
    context = {}
    
    #context['usuarios'] = User.objects.all()
    context['usuarios'] = User.objects.exclude(is_superuser=True)  # Exclui superusuários

    # Obtém a campanha ativa
    processo_ativo = cad_processo.objects.filter(ativo=True).first()

    if processo_ativo:
        data_inicio = processo_ativo.data_inicial_processo
        data_fim = processo_ativo.data_final_processo

        context['contagem_matriculas'] = []



        for usuario in context['usuarios']:
            user_profile = UserProfile.objects.filter(user=usuario, ranking=True).first()
            
            if user_profile:
                first_name = usuario.first_name
                last_name = usuario.last_name
                contagem = Matriculas.objects.filter(usuario=usuario, data_matricula__range=[data_inicio, data_fim]).count()
                soma_pontos = tipo_curso.objects.filter(matriculas__usuario=usuario).aggregate(soma_pontos=models.Sum('pontos'))['soma_pontos']
                ultima_matricula = Matriculas.objects.filter(usuario=usuario).order_by('-create_date').first()

                if ultima_matricula:
                    agora = datetime.now(ultima_matricula.create_date.tzinfo)
                    dias_sem_matricula = (agora - ultima_matricula.create_date).days
                else:
                    dias_sem_matricula = None

                if dias_sem_matricula is not None:
                    if dias_sem_matricula <= 1:
                        cor = 'verde'
                    elif dias_sem_matricula <= 3:
                        cor = 'amarela'
                    else:
                        cor = 'vermelha'
                else:
                    cor = 'nunca'

                context['contagem_matriculas'].append({
                    'usuario': usuario.username,
                    'first_name': first_name,  # Adicionado campo 'first_name'
                    'last_name': last_name, 
                    'contagem': contagem,
                    'soma_pontos': soma_pontos if soma_pontos is not None else 0,
                    'dias_sem_matricula': dias_sem_matricula,
                    'cor': cor
                })

        context['contagem_matriculas'].sort(key=lambda x: x['contagem'], reverse=True)
        context['num_linhas'] = range(1, len(context['contagem_matriculas']) + 1)

    return render(request, 'matriculas/consulta.html', context)

#TODO: Ajustar para quando exlcuir um registro voltar para a mesma página
class MatriculasFullListView(ListView):
    template_name = 'matriculas/matriculas_full_list.html'
    model = Matriculas
    queryset = Matriculas.objects.all()

    def get_queryset(self):
        queryset = Matriculas.objects.all()

        # Filtrar por data inicial
        data_inicial = self.request.GET.get('data_inicial')
        if not data_inicial:
            data_inicial = datetime.now().date()
        else:
            data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d').date()
        queryset = queryset.filter(data_matricula__gte=data_inicial)

        # Filtrar por data final (usando a data atual se não fornecida)
        data_final = self.request.GET.get('data_final')
        if not data_final:
            data_final = datetime.now().date()
        else:
            data_final = datetime.strptime(data_final, '%Y-%m-%d').date()
        queryset = queryset.filter(data_matricula__lte=data_final)

        # Filtrar por usuário (todos se não fornecido)
        usuario_id = self.request.GET.get('usuario')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)

        # Salvar os valores para uso no template
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.usuario_id = usuario_id

        queryset = queryset.order_by('-data_matricula')

        return queryset 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona usuários ao contexto para o campo de seleção
        context['usuarios'] = User.objects.all()
        
        # Adiciona os valores ao contexto
        context['data_inicial'] = self.data_inicial
        context['data_final'] = self.data_final
        context['usuario_id'] = self.usuario_id
        
        # Adiciona o first_name e last_name do usuário ao contexto
        if self.usuario_id:
            user_obj = User.objects.get(pk=self.usuario_id)
            context['usuario_first_name'] = user_obj.first_name
            context['usuario_last_name'] = user_obj.last_name
        else:
            context['usuario_first_name'] = "Todos"
            context['usuario_last_name'] = ""

        return context
    
    
    
    
class RelatorioDia(LoginRequiredMixin, ListView):
    template_name = 'matriculas/relatorio_dia.html'
    model = Matriculas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

         # Processar os dados do formulário
        form = DateSelectForm(self.request.GET)
        
        if form.is_valid():
            selected_date = form.cleaned_data['selected_date']
        else:
            selected_date = timezone.now().date()
            
         # Total de Matrículas do Dia
        total_matriculas_dia = Matriculas.objects.filter(
            data_matricula__date=selected_date
        ).count()
        context['total_matriculas_dia'] = total_matriculas_dia

        # Lista de Polos Cadastrados
        context['polos'] = cad_polos.objects.all()
        
        # Quantidade total de matrículas por polo
        matriculas_por_polo = {}
        for polo in context['polos']:
            matriculas_por_polo[polo.id] = Matriculas.objects.filter(
                usuario__userprofile__polo=polo,
                data_matricula__date=selected_date
            ).aggregate(total=Count('id'))['total']

        context['matriculas_por_polo'] = matriculas_por_polo

        # Total de Matrículas por Usuário 
        matriculas_por_usuario = (
            Matriculas.objects
            .filter(data_matricula__date=selected_date)
            .values('usuario__username', 'usuario__first_name', 'usuario__last_name')  
            .annotate(total=Count('id'))
        )
        context['matriculas_por_usuario'] = matriculas_por_usuario
        
        
        # Total de Matrículas por Usuário com informação do Polo
        matriculas_por_usuario_com_polo = (
            Matriculas.objects
            .filter(data_matricula__date=selected_date)
            .values('usuario__userprofile__polo__nome')  
            # Substitua 'usuario__username' e 'usuario__userprofile__polo__nome' pelos nomes reais dos campos
            .annotate(total=Count('id'))
        )
        context['matriculas_por_usuario_com_polo'] = matriculas_por_usuario_com_polo
        context['date_select_form'] = form     
        
        return context 

class RelatorioFinanceiro(LoginRequiredMixin,FormView, ListView): 
    template_name = 'matriculas/relatorio_financeiro.html'
    model = Matriculas
    form_class = DateRangeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_data = []
        user_with_highest_avg_1mens = None
        user_with_highest_avg_2mens = None
        user_with_highest_avg_desc = None

        # Se o formulário for válido, processa as datas
        if self.request.method == 'GET' and 'data_inicial' in self.request.GET and 'data_final' in self.request.GET:
            data_inicial = self.request.GET['data_inicial']
            data_final = self.request.GET['data_final']

            # Converte as datas para o formato desejado (DD/MM/AA)
            data_inicial_formatted = datetime.strptime(data_inicial, '%Y-%m-%d').strftime('%d/%m/%y')
            data_final_formatted = datetime.strptime(data_final, '%Y-%m-%d').strftime('%d/%m/%y')

            # Adiciona as datas ao contexto formatadas
            context['data_inicial'] = data_inicial_formatted
            context['data_final'] = data_final_formatted
            
            # Obtém todos os usuários
            users = User.objects.filter(is_superuser=False)
            
            # Itera sobre cada usuário para calcular os totais
            for user in users:
                try:
                    # Tenta obter o perfil de usuário
                    user_profile = UserProfile.objects.get(user=user)

                    # Filtra as matrículas associadas a esse usuário
                    user_matriculas = Matriculas.objects.filter(usuario=user, data_matricula__range=[data_inicial, data_final])

                    # Calcula os totais para cada campo
                    total_valor_mensalidade = user_matriculas.aggregate(Sum('valor_mensalidade'))['valor_mensalidade__sum']
                    total_desconto_polo = user_matriculas.aggregate(Sum('desconto_polo'))['desconto_polo__sum']
                    total_desconto_total = user_matriculas.aggregate(Sum('desconto_total'))['desconto_total__sum']

                    # Calcula valores divididos pelo número de matrículas
                    total_matriculas = user_matriculas.count()
                    avg_valor_mensalidade = total_valor_mensalidade / total_matriculas if total_matriculas else 0
                    avg_desconto_polo = total_desconto_polo / total_matriculas if total_matriculas else 0
                    avg_desconto_total = total_desconto_total / total_matriculas if total_matriculas else 0

                    # Adiciona os dados do usuário e totais ao contexto
                    user_data.append({
                        'user': user,
                        'total_valor_mensalidade': total_valor_mensalidade or 0,
                        'total_desconto_polo': total_desconto_polo or 0,
                        'total_desconto_total': total_desconto_total or 0,
                        'avg_valor_mensalidade': avg_valor_mensalidade,
                        'avg_desconto_polo': avg_desconto_polo,
                        'avg_desconto_total': avg_desconto_total,
                        'total_matriculas': total_matriculas,
                    })
                except UserProfile.DoesNotExist:
                    # Se o perfil de usuário não existir, adiciona dados padrão ao contexto
                    user_data.append({
                        'user': user,
                        'total_valor_mensalidade': 0,
                        'total_desconto_polo': 0,
                        'total_desconto_total': 0,
                        'avg_valor_mensalidade': 0,
                        'avg_desconto_polo': 0,
                        'avg_desconto_total': 0,
                        'total_matriculas': 0,
                    })
        
                # Verifica se há pelo menos um usuário antes de calcular o máximo
        if user_data:
            # Filtra os usuários que têm total_matriculas diferente de zero
            user_data_with_matriculas = [user for user in user_data if user['total_matriculas'] != 0]

            if user_data_with_matriculas:
                # Encontrar o usuário com a média mais alta
                user_with_highest_avg_1mens = max(user_data_with_matriculas, key=lambda user: user['avg_valor_mensalidade'])
                user_with_highest_avg_2mens = max(user_data_with_matriculas, key=lambda user: user['avg_desconto_polo'])
                user_with_highest_avg_desc = min(user_data_with_matriculas, key=lambda user: user['avg_desconto_total'])
            else:
                # Se nenhum usuário tiver total_matriculas diferente de zero, define os valores como None
                user_with_highest_avg_1mens = None
                user_with_highest_avg_2mens = None
                user_with_highest_avg_desc = None

        # Adiciona os dados ao contexto da view
        context['user_data'] = user_data
        context['user_with_highest_avg_1mens'] = user_with_highest_avg_1mens
        context['user_with_highest_avg_2mens'] = user_with_highest_avg_2mens
        context['user_with_highest_avg_desc'] = user_with_highest_avg_desc


        return context
 

#TODO: RELATORIO SPACEPOINT : INCLUIR SPACEPOINT NO RESUMO MENSAL 
#TODO: Criar um darkmode para o site
#TODO: Criar metodo para retirar os pontos

class RelatorioSpace(LoginRequiredMixin, ListView):
    template_name = 'matriculas/relatorio_spacepoint.html'
    model = Matriculas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Alteração: Obtém todas as opções de processo disponíveis
        context['processos_disponiveis'] = cad_processo.objects.all()

        # Obtém o número do processo e ano selecionado a partir dos parâmetros GET
        filtro_processo_ano = self.request.GET.get('filtro_processo_ano', None)

        # Inicializa as datas de início e fim do processo
        data_inicial_processo = datetime.now().date()
        data_final_processo = datetime.now().date()

        # Alteração: Obtém as datas do último processo cadastrado
        ultimo_processo = cad_processo.objects.order_by('-data_final_processo').first()
        if ultimo_processo:
            data_inicial_processo = ultimo_processo.data_inicial_processo
            data_final_processo = ultimo_processo.data_final_processo

        # Se filtro_processo_ano não estiver definido, incluir tanto processos ativos quanto inativos
        if not filtro_processo_ano:
            processos = cad_processo.objects.all()
            data_inicial_processo = processos.aggregate(Min('data_inicial_processo'))['data_inicial_processo__min']
            data_final_processo = processos.aggregate(Max('data_final_processo'))['data_final_processo__max']
        else:
            numero_processo, ano_processo = filtro_processo_ano.split('/')
            processo = cad_processo.objects.get(numero_processo=numero_processo, ano_processo=ano_processo)

            # Obtém as datas de início e fim do processo
            data_inicial_processo = processo.data_inicial_processo
            data_final_processo = processo.data_final_processo

        context['processos'] = cad_processo.objects.all()

        context['data_inicial_processo'] = data_inicial_processo
        context['data_final_processo'] = data_final_processo
        context['filtro_processo_ano'] = filtro_processo_ano

        context['exibir_resultados'] = 'filtro_processo_ano' in self.request.GET

        # Obtém a lista de usuários e as matrículas para cada usuário no período selecionado
        usuarios = User.objects.filter(
            matriculas__processo_sel__in=context['processos'],
            matriculas__data_matricula__range=[data_inicial_processo, data_final_processo]
        ).distinct()

        total_matriculas_por_usuario = []
        for usuario in usuarios:
            matriculas_usuario = Matriculas.objects.filter(
                usuario=usuario,
                processo_sel__in=context['processos'],
                data_matricula__range=[data_inicial_processo, data_final_processo]
            )

            # Obtém a lista de todos os meses entre as datas de início e fim
            meses_entre_datas = list(self.get_month_range(data_inicial_processo, data_final_processo))

            # Inicializa o dicionário total_matriculas_por_mes com zeros para todos os meses
            total_matriculas_por_mes = {mes.strftime('%Y-%m'): 0 for mes in meses_entre_datas}

            # Iterar sobre todas as matrículas do usuário no período
            for matricula in matriculas_usuario:
                chave_mes_ano = matricula.data_matricula.strftime('%Y-%m')

                # Atualize o valor para o mês com matrículas
                total_matriculas_por_mes[chave_mes_ano] += 1

            # Adiciona o total geral de matrículas para o usuário
            total_geral_usuario = matriculas_usuario.count()

            total_matriculas_por_usuario.append({
                'usuario': usuario,
                'total_matriculas_por_mes': total_matriculas_por_mes,
                'total_geral_usuario': total_geral_usuario,
            })

        context['total_matriculas_por_usuario'] = total_matriculas_por_usuario
        context['meses_entre_datas'] = self.get_month_range(data_inicial_processo, data_final_processo)

        return context

    def get_month_range(self, start_date, end_date):
        current_date = start_date.date()  # Convertendo para date
        end_date = end_date.date()  # Convertendo para date
        while current_date <= end_date:
            yield current_date
            # Adiciona um mês
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)

    def get_queryset(self):
        # Obtém o objeto cad_processo selecionado no formulário
        filtro_processo_ano = self.request.GET.get('filtro_processo_ano')

        # Filtra as matrículas com base nas informações selecionadas
        queryset = Matriculas.objects.all()
        if filtro_processo_ano:
            numero_processo, ano_processo = filtro_processo_ano.split('/')
            processo = cad_processo.objects.get(numero_processo=numero_processo, ano_processo=ano_processo)
            data_inicial = processo.data_inicial_processo
            data_final = processo.data_final_processo
            queryset = queryset.filter(processo_sel__id=processo.id, data_matricula__range=(data_inicial, data_final))

        return queryset


    
class RelatorioCampanha(LoginRequiredMixin, ListView):
    template_name = 'matriculas/relatorio_campanha.html'
    paginate_by = 8
    model = Matriculas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Alteração: Obtém todas as campanhas disponíveis
        context['campanhas_disponiveis'] = cad_campanhas.objects.all()

        # Obtém a campanha selecionada a partir dos parâmetros GET
        filtro_campanha = self.request.GET.get('filtro_campanha', None)
        

        # Inicializa as datas de início e fim da campanha
        data_inicio_campanha = datetime.now().date()
        data_fim_campanha = datetime.now().date()

        # Alteração: Obtém as datas da última campanha cadastrada
        ultima_campanha = cad_campanhas.objects.order_by('-data_fim').first()
        if ultima_campanha:
            data_inicio_campanha = ultima_campanha.data_inicio
            data_fim_campanha = ultima_campanha.data_fim

        # Se filtro_campanha não estiver definido, incluir tanto campanhas ativas quanto inativas
        if not filtro_campanha:
            campanhas = cad_campanhas.objects.all()
            data_inicio_campanha = campanhas.aggregate(Min('data_inicio'))['data_inicio__min']
            data_fim_campanha = campanhas.aggregate(Max('data_fim'))['data_fim__max']
        else:
            campanha = cad_campanhas.objects.get(id=filtro_campanha)
            

            # Obtém as datas de início e fim da campanha
            data_inicio_campanha = campanha.data_inicio
            data_fim_campanha = campanha.data_fim

        context['campanhas'] = cad_campanhas.objects.all()

        context['data_inicio_campanha'] = data_inicio_campanha
        context['data_fim_campanha'] = data_fim_campanha
        context['filtro_campanha'] = filtro_campanha

        context['exibir_resultados'] = 'filtro_campanha' in self.request.GET
        
        # Obtém a lista de usuários e as matrículas para cada usuário no período selecionado
        usuarios = User.objects.filter(
            id__in=Subquery(
                Matriculas.objects.filter(
                    campanha__in=context['campanhas_disponiveis'],
                    data_matricula__range=[data_inicio_campanha, data_fim_campanha],
                    usuario=OuterRef('id')
                ).values('usuario')
            )
        )

        total_matriculas_por_usuario = []
        for usuario in usuarios:
            matriculas_usuario = Matriculas.objects.filter(
                usuario=usuario,
                campanha__id=filtro_campanha,
                data_matricula__range=[data_inicio_campanha, data_fim_campanha]
            )

            # Dicionário para armazenar o total de matrículas por mês
            total_matriculas_por_mes = {}

            # Iterar sobre todas as matrículas do usuário no período
            for matricula in matriculas_usuario:
                chave_mes_ano = matricula.data_matricula.strftime('%Y-%m')
                total_matriculas_por_mes[chave_mes_ano] = total_matriculas_por_mes.get(chave_mes_ano, 0) + 1

            # Preencher com 0 nos meses sem matrículas
            for mes in self.get_month_range(data_inicio_campanha, data_fim_campanha):
                chave_mes_ano = mes.strftime('%Y-%m')
                if chave_mes_ano not in total_matriculas_por_mes:
                    total_matriculas_por_mes[chave_mes_ano] = 0

            # Adiciona o total geral de matrículas para o usuário
            total_geral_usuario = matriculas_usuario.count()

            total_matriculas_por_usuario.append({
                'usuario': usuario,
                'total_matriculas_por_mes': total_matriculas_por_mes,
                'total_geral_usuario': total_geral_usuario,
            })

        context['total_matriculas_por_usuario'] = total_matriculas_por_usuario
        context['meses_entre_datas'] = self.get_month_range(data_inicio_campanha, data_fim_campanha)

        return context

    def get_month_range(self, start_date, end_date):
        current_date = start_date.date()  # Convertendo para date
        end_date = end_date.date()  # Convertendo para date
        while current_date <= end_date:
            yield current_date
            # Adiciona um mês
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)

    def get_queryset(self):
        # Obtém o ID da campanha selecionada no formulário
        filtro_campanha = self.request.GET.get('filtro_campanha')

        # Filtra as matrículas com base nas informações selecionadas
        queryset = Matriculas.objects.all()
        if filtro_campanha:
            campanha = cad_campanhas.objects.get(id=filtro_campanha)
            data_inicio = campanha.data_inicio
            data_fim = campanha.data_fim
            queryset = queryset.filter(campanha__id=campanha.id, data_matricula__range=(data_inicio, data_fim))

        return queryset
    
class MetasTableView(LoginRequiredMixin, View):
    template_name = 'matriculas/metas_table.html'

    def get(self, request, *args, **kwargs):
        # Recupera os dados necessários do banco de dados
        metas_data, tipos_curso = self.get_metas_data()

        # Passa os dados para o contexto do template
        context = {'metas_data': metas_data, 'tipos_curso': tipos_curso}
       
        return render(request, self.template_name, context)

    def get_metas_data(self):
        metas_data = []
        polos = cad_polos.objects.filter(active=True).order_by('nome')
        tipos_curso = tipo_curso.objects.filter(active=True).order_by('nome')

        for polo in polos:
            # Filtra os processos ativos relacionados ao polo
            processos_ativos = cad_processo.objects.filter(ativo=True)

            # Inicializa o dicionário para armazenar os valores das metas para cada tipo_curso
            meta_por_tipo_curso = {tipo.nome: 0 for tipo in tipos_curso}

            for processo in processos_ativos:
                # Filtra as metas relacionadas ao processo
                metas_polo = Metas.objects.filter(polo=polo, processo=processo)

                # Preenche o dicionário com os valores das metas reais
                for meta in metas_polo:
                    meta_por_tipo_curso[meta.tipo_curso.nome] += meta.meta

            # Calcula o total de todas as metas
            total_metas = sum(meta_por_tipo_curso.values())

            # Adiciona os dados à lista
            metas_data.append({
                'polo': polo.nome,
                'meta_por_tipo_curso': meta_por_tipo_curso,
                'total_metas': total_metas,
            })

        return metas_data, tipos_curso
    

# class RelatorioMetasTableView(LoginRequiredMixin, ListView):
#     template_name = 'matriculas/relatorio_metas_table.html'
#     model = Matriculas

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Filtre os processos seletivos ativos
#         processos_seletivos_ativos = cad_processo.objects.filter(ativo=True)

#         # Adiciona o campo meta_por_tipo_curso da primeira view
#         metas_data, tipos_curso = MetasTableView().get_metas_data()
#         context['meta_por_tipo_curso'] = {tipo.nome: 0 for tipo in tipos_curso}
#         for meta_data in metas_data:
#             for tipo, valor in meta_data['meta_por_tipo_curso'].items():
#                 context['meta_por_tipo_curso'][tipo] += valor
        
#         # Total de Matrículas do Dia para processos seletivos ativos
#         total_matriculas_dia = Matriculas.objects.filter(processo_sel__in=processos_seletivos_ativos).count()
#         context['total_matriculas_dia'] = total_matriculas_dia

#         # Lista de Polos Cadastrados
#         context['polos'] = cad_polos.objects.all().order_by('nome')
#         context['tipo_curso'] = tipo_curso.objects.all()
#         # Quantidade total de matrículas por polo para processos seletivos ativos
#         matriculas_por_polo = {}
#         for polo in context['polos']:
#             matriculas_por_polo[polo.id] = {
#                 'polo': polo,
#                 'total': Matriculas.objects.filter(
#                     usuario__userprofile__polo=polo,
#                     processo_sel__in=processos_seletivos_ativos,
#                 ).aggregate(total=Count('id'))['total'],
#                 'somatorio_tipo_curso': {}
#             }

#             # Somatório de matrículas por tipo de curso para cada polo para processos seletivos ativos
#             tipos_de_curso = tipo_curso.objects.all()
#             for tipo in tipos_de_curso:
#                 matriculas_por_polo[polo.id]['somatorio_tipo_curso'][tipo.id] = Matriculas.objects.filter(
#                     usuario__userprofile__polo=polo,
#                     tipo_curso=tipo,
#                     processo_sel__in=processos_seletivos_ativos,
#                 ).aggregate(total=Count('id'))['total']

#         context['matriculas_por_polo'] = matriculas_por_polo

#         # Total de Matrículas por Usuário com informação do Polo
#         matriculas_por_usuario_com_polo = (
#             Matriculas.objects
#             .values('usuario__userprofile__polo__nome')
#             .annotate(total=Count('id'))
#         )
#         context['matriculas_por_usuario_com_polo'] = matriculas_por_usuario_com_polo
#         context['tipos_de_curso'] = tipo_curso.objects.all().order_by('nome')
#         return context

class RelatorioMetasTableView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/relatorio_metas_table.html'
    model = Matriculas

    def get(self, request, *args, **kwargs):
        # Dados da primeira view  - total_matriculas_dia RETORNA SOMA TOTAL DE MATRICULAS REALIZADAS
        metas_data, tipos_curso = self.get_metas_data()
        total_matriculas_dia = Matriculas.objects.filter(
            processo_sel__in=self.get_processos_ativos()).count()
       
        # Dados da segunda view
        matriculas_por_polo = self.get_matriculas_por_polo()
        matriculas_por_usuario_com_polo = self.get_matriculas_por_usuario_com_polo()

        context = {
            'metas_data': metas_data,
            'tipos_curso': tipos_curso,
            'total_matriculas_dia': total_matriculas_dia,
            'matriculas_por_polo': matriculas_por_polo,
            'matriculas_por_usuario_com_polo': matriculas_por_usuario_com_polo,
        }

        return render(request, self.template_name, context)

    def get_metas_data(self):
        metas_data = []
        polos = cad_polos.objects.filter(active=True).order_by('nome')
        tipos_curso = tipo_curso.objects.filter(active=True).order_by('nome')

        for polo in polos:
            processos_ativos = cad_processo.objects.filter(ativo=True)
            meta_por_tipo_curso = {tipo.nome: 0 for tipo in tipos_curso}

            for processo in processos_ativos:
                metas_polo = Metas.objects.filter(polo=polo, processo=processo)

                for meta in metas_polo:
                    meta_por_tipo_curso[meta.tipo_curso.nome] += meta.meta

            total_metas = sum(meta_por_tipo_curso.values())

            metas_data.append({
                'polo': polo.nome,
                'meta_por_tipo_curso': meta_por_tipo_curso,
                'total_metas': total_metas, # Fazer o somatório das metas
            })
            
        return metas_data, tipos_curso

    def get_processos_ativos(self):
        return cad_processo.objects.filter(ativo=True)

    def get_matriculas_por_polo(self):
        processos_seletivos_ativos = cad_processo.objects.filter(ativo=True)
        matriculas_por_polo = {}

        for polo in cad_polos.objects.all().order_by('nome'):
            matriculas_por_polo[polo.id] = {
                'polo': polo,
                'total': Matriculas.objects.filter(
                    usuario__userprofile__polo=polo,
                    processo_sel__in=processos_seletivos_ativos,
                ).aggregate(total=Count('id'))['total'],
                'somatorio_tipo_curso': {}
            }

            tipos_de_curso = tipo_curso.objects.all().order_by('nome')

            for tipo in tipos_de_curso:
                matriculas_por_polo[polo.id]['somatorio_tipo_curso'][tipo.id] = Matriculas.objects.filter(
                    usuario__userprofile__polo=polo,
                    tipo_curso=tipo,
                    processo_sel__in=processos_seletivos_ativos,
                ).aggregate(total=Count('id'))['total']
                
        return matriculas_por_polo

    def get_matriculas_por_usuario_com_polo(self):
        matriculas_por_usuario_com_polo = (
            Matriculas.objects
            .values('usuario__userprofile__polo__nome')
            .annotate(total=Count('id'))
        )
        return matriculas_por_usuario_com_polo
    
    
class RelatorioCheckpointView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/relatorio_checkpoint.html'
    model = Matriculas

    def get(self, request, *args, **kwargs):
        # Dados da primeira view
        metas_data, tipos_curso, total_geral_metas = self.get_metas_data()
        total_matriculas_dia = Matriculas.objects.filter(
            processo_sel__in=self.get_processos_ativos()).count()
        
        matriculas_por_total = (total_matriculas_dia / total_geral_metas) * 100
        # Dados da segunda view
        matriculas_por_polo = self.get_matriculas_por_polo()
        matriculas_por_usuario_com_polo = self.get_matriculas_por_usuario_com_polo()

        spacepoint_data = self.get_spacepoint_data()
         # Cálculo do ritmo
        ritmo = self.calcular_ritmo(total_matriculas_dia)
        ritmo_polo = self.calcular_ritmo_polo(matriculas_por_polo)
        # Cálculo do ritmo_meta
        ritmo_meta = self.calcular_ritmo_meta(total_geral_metas)
        
        
        
        context = {
            'metas_data': metas_data,
            'tipos_curso': tipos_curso,
            'total_geral_metas': total_geral_metas,
            'total_matriculas_dia': total_matriculas_dia,
            'matriculas_por_polo': matriculas_por_polo,
            'matriculas_por_usuario_com_polo': matriculas_por_usuario_com_polo,
            'matriculas_por_total': matriculas_por_total,
            'spacepoint_data': spacepoint_data,
            'ritmo': ritmo,
            'ritmo_meta': ritmo_meta,
            'ritmo_polo': ritmo_polo,
            
        }
        
        return render(request, self.template_name, context)

    def get_metas_data(self):
        metas_data = []
        polos = cad_polos.objects.filter(active=True).order_by('nome')
        tipos_curso = tipo_curso.objects.filter(active=True).order_by('nome')

        for polo in polos:
            processos_ativos = cad_processo.objects.filter(ativo=True)
            meta_por_tipo_curso = {tipo.nome: 0 for tipo in tipos_curso}

            for processo in processos_ativos:
                metas_polo = Metas.objects.filter(polo=polo, processo=processo)

                for meta in metas_polo:
                    meta_por_tipo_curso[meta.tipo_curso.nome] += meta.meta

            total_metas = sum(meta_por_tipo_curso.values())

            metas_data.append({
                'polo': polo.nome,
                'meta_por_tipo_curso': meta_por_tipo_curso,
                'total_metas': total_metas,
            })
            
            total_geral_metas = sum(entry['total_metas'] for entry in metas_data)
            for entry in metas_data:
                entry['total_geral_metas'] = total_geral_metas
                
            print(total_metas)
              
        return metas_data, tipos_curso, total_geral_metas

    def get_processos_ativos(self):
        return cad_processo.objects.filter(ativo=True)

    def get_matriculas_por_polo(self):
        processos_seletivos_ativos = cad_processo.objects.filter(ativo=True)
        matriculas_por_polo = {}

        for polo in cad_polos.objects.all().order_by('nome'):
            total_metas_polo = sum(entry['total_metas'] for entry in self.get_metas_data()[0] if entry['polo'] == polo.nome)

            # Adicione a variável ritmo_polo_meta
            ritmo_polo_meta = 0

            if total_metas_polo > 0:
                # Calcular o número de dias entre a data final e inicial do processo_sel
                processo_ativo = self.get_processos_ativos().first()
                dias_entre_datas = (processo_ativo.data_final_processo - processo_ativo.data_inicial_processo).days

                # Evitar a divisão por zero
                if dias_entre_datas > 0:
                    ritmo_polo_meta = total_metas_polo / dias_entre_datas

            matriculas_por_polo[polo.id] = {
                'polo': polo,
                'total': Matriculas.objects.filter(
                    usuario__userprofile__polo=polo,
                    processo_sel__in=processos_seletivos_ativos,
                ).aggregate(total=Count('id'))['total'],
                'somatorio_tipo_curso': {},
                'percentual_metas': 0,
                'ritmo_polo_meta': ritmo_polo_meta,  # Adicione esta variável
            }

            tipos_de_curso = tipo_curso.objects.all().order_by('nome')

            for tipo in tipos_de_curso:
                matriculas_por_polo[polo.id]['somatorio_tipo_curso'][tipo.id] = Matriculas.objects.filter(
                    usuario__userprofile__polo=polo,
                    tipo_curso=tipo,
                    processo_sel__in=processos_seletivos_ativos,
                ).aggregate(total=Count('id'))['total']

            if total_metas_polo > 0:
                matriculas_por_polo[polo.id]['percentual_metas'] = (
                    matriculas_por_polo[polo.id]['total'] / total_metas_polo
                ) * 100

        return matriculas_por_polo

    def get_matriculas_por_usuario_com_polo(self):
        matriculas_por_usuario_com_polo = (
            Matriculas.objects
            .values('usuario__userprofile__polo__nome')
            .annotate(total=Count('id'))
        )
        return matriculas_por_usuario_com_polo
    
    def get_spacepoint_data(self):
        processos_ativos = self.get_processos_ativos()
        
        spacepoint_data = cad_spacepoint.objects.filter(
            id_processos__in=processos_ativos,
            ativo=True
        ).values(
            'id_processos__numero_processo',
            'id_processos__ano_processo',
            'data_spacepoint',
            'meta_pc',
            'id_processos__data_inicial_processo',
            'id_processos__data_final_processo',
        ).order_by('data_spacepoint')[:10]  # Ajuste o número conforme necessário
        
        return spacepoint_data

    def calcular_ritmo(self, total_matriculas_dia):
        # Obtendo a data inicial do processo ativo
        processo_ativo = self.get_processos_ativos().first()
        data_inicial_processo = processo_ativo.data_inicial_processo

        # Calculando o número de dias entre a data inicial e o dia atual
        dias_entre_datas = (timezone.now() - data_inicial_processo).days

        # Evitando a divisão por zero
        if dias_entre_datas > 0:
            ritmo = total_matriculas_dia / dias_entre_datas
        else:
            ritmo = 0

        return ritmo
    
    def calcular_ritmo_meta(self, total_geral_metas):
        # Obtendo a data inicial e final do processo ativo
        processo_ativo = self.get_processos_ativos().first()
        data_inicial_processo = processo_ativo.data_inicial_processo
        data_final_processo = processo_ativo.data_final_processo

        # Calculando o número de dias entre a data inicial e final
        dias_entre_datas = (data_final_processo - data_inicial_processo).days

        # Evitando a divisão por zero
        if dias_entre_datas > 0:
            ritmo_meta = total_geral_metas / dias_entre_datas
        else:
            ritmo_meta = 0

        return ritmo_meta
    
    def calcular_ritmo_polo(self, matriculas_por_polo):
        # Obtendo a data inicial do processo ativo
        processo_ativo = self.get_processos_ativos().first()
        data_inicial_processo = processo_ativo.data_inicial_processo

        # Calculando o número de dias entre a data inicial e o dia atual
        dias_entre_datas = (timezone.now() - data_inicial_processo).days

        ritmo_polo = []

        for polo_id, matriculas in matriculas_por_polo.items():
            # Evitando a divisão por zero
            if dias_entre_datas > 0:
                # Calculando o ritmo por polo
                ritmo_polo.append({
                    'polo_nome': matriculas['polo'].nome,
                    'ritmo': matriculas['total'] / dias_entre_datas,
                })
            else:
                ritmo_polo.append({
                    'polo_nome': matriculas['polo'].nome,
                    'ritmo': 0,
                })

        return ritmo_polo
    
  