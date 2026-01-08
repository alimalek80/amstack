from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Lead
from .forms import LeadCreateForm, LeadStatusUpdateForm


class LeadCreateView(CreateView):
    """Public form for creating new leads."""
    model = Lead
    form_class = LeadCreateForm
    template_name = 'leads/lead_form.html'
    success_url = reverse_lazy('leads:lead_success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_slug = self.request.GET.get('service', '')
        service_title = None
        
        # Try to resolve service from services app if available
        if service_slug:
            try:
                from services.models import Service
                service = Service.objects.get(slug=service_slug, is_active=True)
                service_title = service.title
            except ImportError:
                # services app not installed, use slug as fallback
                pass
            except Exception:
                # Service not found or other error
                pass
        
        context['service_slug'] = service_slug
        context['service_title'] = service_title
        return context

    def form_valid(self, form):
        """Set service_slug and source before saving."""
        instance = form.save(commit=False)
        
        service_slug = self.request.GET.get('service', '')
        instance.service_slug = service_slug
        
        # Try to get service title if available
        if service_slug:
            try:
                from services.models import Service
                service = Service.objects.get(slug=service_slug, is_active=True)
                instance.service_title = service.title
            except:
                pass
        
        # Set source
        if service_slug:
            instance.source = 'services'
        else:
            instance.source = 'direct'
        
        return super().form_valid(form)


class LeadSuccessView(TemplateView):
    """Thank you page after form submission."""
    template_name = 'leads/lead_success.html'


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require staff access."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    login_url = 'accounts:login'


class LeadListView(StaffRequiredMixin, ListView):
    """Dashboard view for listing all leads."""
    model = Lead
    template_name = 'leads/dashboard/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 20

    def get_queryset(self):
        queryset = Lead.objects.all()
        
        # Filter by status if provided
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search across name, email, service, and message
        search = self.request.GET.get('q', '')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(service_title__icontains=search) |
                Q(service_slug__icontains=search) |
                Q(message__icontains=search)
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add status counts
        context['status_counts'] = {
            'new': Lead.objects.filter(status='new').count(),
            'contacted': Lead.objects.filter(status='contacted').count(),
            'qualified': Lead.objects.filter(status='qualified').count(),
            'won': Lead.objects.filter(status='won').count(),
            'lost': Lead.objects.filter(status='lost').count(),
        }
        
        # Add current filters to context
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('q', '')
        
        return context


class LeadDetailView(StaffRequiredMixin, DetailView):
    """Dashboard view for viewing and updating a single lead."""
    model = Lead
    template_name = 'leads/dashboard/lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_form'] = LeadStatusUpdateForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        """Handle status update form submission."""
        self.object = self.get_object()
        form = LeadStatusUpdateForm(request.POST, instance=self.object)
        
        if form.is_valid():
            form.save()
            return redirect('leads:lead_detail', pk=self.object.pk)
        
        context = self.get_context_data()
        context['status_form'] = form
        return self.render_to_response(context)

