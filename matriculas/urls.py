from django.urls import path, include
from .views import *
#from django.conf.urls.static import static
from django.conf import settings

from smart_selects import *

try:
    from django.conf.urls.defaults import url
except ImportError:
    from django.urls import  re_path as url


app_name = "matriculas"
urlpatterns = [
    
    
    ##ListView
    path('list/', MatriculasListView.as_view(), name='matriculas_list'),
    #path('consultores/', ConsultorListView.as_view(), name='consultor_list'),
    path('consultores/', UserListView.as_view(), name='user_list'),
    path('campanhas/', CampanhaListView.as_view(), name='campanha_list'),
    path('curso/', CursoListView.as_view(), name='curso_list'),
    path('tipocurso/', TipoCursoListView.as_view(), name='tipo_curso_list'),
    path('polo/', PoloListView.as_view(), name='polo_list'),
    path('processo/', ProcessoListView.as_view(), name='processo_list'),
    path('file/<int:pk>/', MatriculaFileView.as_view(), name='matricula_file'), #Mostra o arquivo da matrícula
    
    #NewView
    path('', MatriculasNewView.as_view(), name='matriculas_new'),
    #path('consultores/novo', ConsultorNewView.as_view(), name='consultor_new'), #apagar se Usercreate funcionar
    path('consultores/new', UserNewView.as_view(), name='user_new'),
    path('polo/novo', PoloNewView.as_view(), name='polo_new'),
    path('curso/novo', CursosNewView.as_view(), name='cursos_new'),
    path('tipocurso/novo', TipoCursoNewView.as_view(), name='tipo_curso_new'),
    path('campanhas/novo', CampanhaNewView.as_view(), name='campanha_new'),
    path('processo/novo', ProcessoNewView.as_view(), name='processo_new'),
    
    #UpdateView
    path('<int:id>/', MatriculasUpdateView.as_view(), name='matriculas_update'),
    path('consultores/<int:id>', ConsultorUpdateView.as_view(), name='consultor_update'),
    path('consultores/<int:id>', UserUpdateView.as_view(), name='user_update'),
    path('campanhas/<int:id>', CampanhaUpdateView.as_view(), name='campanha_update'),
    path('curso/<int:id>', CursoUpdateView.as_view(), name='curso_update'),
    path('tipocurso/<int:id>', TipoCursoUpdateView.as_view(), name='tipo_curso_update'),
    path('polo/<int:id>', PoloUpdateView.as_view(), name='polo_update'),
    path('processo/<int:id>', ProcessoUpdateView.as_view(), name='processo_update'),
    
    #DeleteView
    path('<int:id>/delete', MatriculasDeleteView.as_view(), name='matriculas_delete'),
    path('consultores/<int:id>/delete', ConsultorDeleteView.as_view(), name='consultor_delete'),
    path('campanhas/<int:id>/delete', CampanhaDeleteView.as_view(), name='campanha_delete'),
    path('curso/<int:id>/delete', CursoDeleteView.as_view(), name='curso_delete'),
    path('tipocurso/<int:id>/delete', TipoCursoDeleteView.as_view(), name='tipo_curso_delete'),
    path('polo/<int:id>/delete', PoloDeleteView.as_view(), name='polo_delete'),
    path('processo/<int:id>/delete', ProcessoDeleteView.as_view(), name='processo_delete'),
    
    #Consultas
    path('consulta/', RankView, name= "user_rank" ),
    #path('filtrocursos/', FiltroCursos, name='filtrar_cursos'),
    path('get_cursos/', get_cursos, name='get_cursos'),
    path('processo_ativo', lista_processos, name='processo_ativo'),
  
    
    
   
 
    
]

