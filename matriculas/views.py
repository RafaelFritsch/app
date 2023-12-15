
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
import os
from django.contrib.auth.models import Group
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.http import HttpResponse, JsonResponse



####################### LIST VIEWS ######################################################
def lista_processos(request):
    # Filtra os processos ativos
    processos_ativos = cad_processo.objects.filter(ativo=True)
    # Passa a lista filtrada para o template
    return render (request, 'matriculas/processo_ativo.html', {'processos': processos_ativos})  

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
    paginate_by = 15

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

        return context

class CampanhaListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/campanha_list.html'
    model = cad_campanhas
    queryset = cad_campanhas.objects.all()
    paginate_by = 10
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
    paginate_by = 10
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
    queryset = cad_polos.objects.all()
    paginate_by = 10
    
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
    queryset = tipo_curso.objects.all()
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')

        if search_query:
            # Filtra curso com base no nome
            queryset = queryset.filter(nome__icontains=search_query)

        return queryset
    
class ProcessoListView(LoginRequiredMixin, ListView):
    template_name = 'matriculas/processo_list.html'
    model = cad_processo
    queryset = cad_processo.objects.all()
    paginate_by = 20
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('name', '')

        if search_query:
            # Filtra processo com base no número ou ano
            queryset = queryset.filter(numero_processo__icontains=search_query) | queryset.filter(ano_processo__icontains=search_query)

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
    print(cursos_list)
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
        return RedirectView.as_view(url=reverse_lazy('matriculas:user_list'))(request)

class UserDeactivateView(View):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        user.is_active = False
        user.save()
        return RedirectView.as_view(url=reverse_lazy('matriculas:user_list'))(request)


class PoloNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/polo_new.html'
    form_class = PoloForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('matriculas:polo_list')


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
    
    def get_success_url(self) -> str:
        return reverse('matriculas:campanha_list')   
    
class ProcessoNewView(LoginRequiredMixin, CreateView):
    template_name = 'matriculas/processo_new.html'
    form_class = ProcessoForm
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('matriculas:processo_list')
    

    
    
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


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'matriculas/user_update.html'
    form_class = UserForm
    model = UserProfile

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
    context['usuarios'] = User.objects.all()

    # Obtém a campanha ativa
    processo_ativo = cad_processo.objects.filter(ativo=True).first()

    if processo_ativo:
        data_inicio = processo_ativo.data_inicial_processo
        data_fim = processo_ativo.data_final_processo

        context['contagem_matriculas'] = []

        for usuario in context['usuarios']:
            contagem = Matriculas.objects.filter(usuario=usuario, create_date__range=[data_inicio, data_fim]).count()

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
    paginate_by = 15
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
    paginate_by = 10
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
            .values('usuario__username')  # Substitua 'usuario__username' pelo nome real do campo que representa o usuário em Matriculas
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
    paginate_by = 10
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
            # Encontrar o usuário com a média mais alta
            user_with_highest_avg_1mens = max(user_data, key=lambda user: user['avg_valor_mensalidade'])
            user_with_highest_avg_2mens = max(user_data, key=lambda user: user['avg_desconto_polo'])
            user_with_highest_avg_desc = min(user_data, key=lambda user: user['avg_desconto_total'])

        # Adiciona os dados ao contexto da view
        context['user_data'] = user_data
        context['user_with_highest_avg_1mens'] = user_with_highest_avg_1mens
        context['user_with_highest_avg_2mens'] = user_with_highest_avg_2mens
        context['user_with_highest_avg_desc'] = user_with_highest_avg_desc

        return context
 


#TODO: COnferir o paginate to das as htmls

#TODO: GERAL : INCLUIR SPACEPOINT NO RESUMO MENSAL ( ANTES FAZER PUSH DAS ATUALIZACOES ANTERIORES)


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
            total_matriculas = matriculas_usuario.count()
            # Dicionário para armazenar o total de matrículas por mês
            total_matriculas_por_mes = {}

            # Iterar sobre todos os meses no período do processo seletivo
            current_date = data_inicial_processo
            while current_date <= data_final_processo:
                total_matriculas_por_mes[current_date.strftime('%Y-%m')] = matriculas_usuario.filter(
                    data_matricula__year=current_date.year,
                    data_matricula__month=current_date.month
                ).count()

                current_date += relativedelta(months=1)

            total_matriculas_por_usuario.append({
                'usuario': usuario,
                'total_matriculas': total_matriculas,
                'total_matriculas_por_mes': total_matriculas_por_mes,
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
    model = Matriculas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Alteração: Obtém todas as campanhas disponíveis
        context['campanhas_disponiveis'] = cad_campanhas.objects.all()

        # Obtém a campanha selecionada a partir dos parâmetros GET
        filtro_campanha = self.request.GET.get('filtro_campanha', None)
        print(f"Filtro Campanha: {filtro_campanha}")

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
            print(f"Campanha Selecionada: {campanha}")

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
                campanha__in=context['campanhas_disponiveis'],  #### ERROOO
                data_matricula__range=[data_inicio_campanha, data_fim_campanha]
            )
            total_matriculas = matriculas_usuario.count()
            # Dicionário para armazenar o total de matrículas por mês
            total_matriculas_por_mes = {}

            # Iterar sobre todos os meses no período da campanha
            current_date = data_inicio_campanha
            while current_date <= data_fim_campanha:
                total_matriculas_por_mes[current_date.strftime('%Y-%m')] = matriculas_usuario.filter(
                    data_matricula__year=current_date.year,
                    data_matricula__month=current_date.month
                ).count()

                current_date += relativedelta(months=1)

            total_matriculas_por_usuario.append({
                'usuario': usuario,
                'total_matriculas': total_matriculas,
                'total_matriculas_por_mes': total_matriculas_por_mes,
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