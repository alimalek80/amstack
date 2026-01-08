from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Service, ServiceCategory


class ServiceListView(ListView):
    """Display all active services with optional category filtering."""
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        """Return active services, optionally filtered by category."""
        queryset = Service.objects.filter(is_active=True).select_related('category')
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True)
        
        # Add selected category to context
        category_slug = self.request.GET.get('category')
        if category_slug:
            context['selected_category'] = get_object_or_404(
                ServiceCategory,
                slug=category_slug,
                is_active=True
            )
        
        # Separate featured and regular services
        all_services = context['services']
        context['featured_services'] = [s for s in all_services if s.is_featured]
        context['regular_services'] = [s for s in all_services if not s.is_featured]
        
        return context


class ServiceDetailView(DetailView):
    """Display detailed view of a single service."""
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'

    def get_queryset(self):
        """Only show active services."""
        return Service.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object
        
        # Add pricing display information
        context['pricing_display'] = self.get_pricing_display(service)
        
        # Add parsed lists
        context['deliverables'] = service.get_deliverables_list()
        context['requirements'] = service.get_requirements_list()
        
        # Parse FAQs into Q&A pairs
        context['faqs'] = self.parse_faqs(service.faqs)
        
        # Add CTA URLs
        context['hire_url'] = f'/hire/?service={service.slug}'
        if service.pricing_type == 'fixed':
            context['order_url'] = f'/orders/create/?service={service.slug}'
        
        return context

    def parse_faqs(self, faq_text):
        """Parse FAQ text into Q&A pairs."""
        if not faq_text:
            return []
        
        faqs = []
        lines = faq_text.strip().split('\n')
        current_q = None
        current_a = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                # Save previous Q&A pair if exists
                if current_q and current_a:
                    faqs.append({'question': current_q, 'answer': current_a})
                current_q = line[2:].strip()
                current_a = None
            elif line.startswith('A:'):
                current_a = line[2:].strip()
        
        # Don't forget the last pair
        if current_q and current_a:
            faqs.append({'question': current_q, 'answer': current_a})
        
        return faqs

    def get_pricing_display(self, service):
        """Return formatted pricing information."""
        if service.pricing_type == 'starting_at' and service.starting_price:
            return f'Starting at ${service.starting_price:,.2f}'
        elif service.pricing_type == 'fixed' and service.fixed_price:
            return f'${service.fixed_price:,.2f}'
        elif service.pricing_type == 'hourly' and service.starting_price:
            return f'${service.starting_price:,.2f}/hr'
        return 'Contact for pricing'
