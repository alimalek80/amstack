from django import forms
from django.core.exceptions import ValidationError
from .models import Lead


class LeadCreateForm(forms.ModelForm):
    """Form for creating new leads from the public form."""
    
    class Meta:
        model = Lead
        fields = ['full_name', 'email', 'phone', 'company', 'budget', 'timeline', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to form fields
        field_classes = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
        
        self.fields['full_name'].widget.attrs.update({
            'class': field_classes,
            'placeholder': 'Your full name',
            'required': True
        })
        
        self.fields['email'].widget.attrs.update({
            'class': field_classes,
            'placeholder': 'your@email.com',
            'required': True
        })
        
        self.fields['phone'].widget.attrs.update({
            'class': field_classes,
            'placeholder': '+1 (555) 000-0000 (optional)',
        })
        
        self.fields['company'].widget.attrs.update({
            'class': field_classes,
            'placeholder': 'Your company (optional)',
        })
        
        self.fields['budget'].widget.attrs.update({
            'class': field_classes,
            'placeholder': 'e.g., $500-$1k (optional)',
        })
        
        self.fields['timeline'].widget.attrs.update({
            'class': field_classes,
            'placeholder': 'e.g., this week, 2-4 weeks (optional)',
        })
        
        self.fields['message'].widget = forms.Textarea(attrs={
            'class': field_classes,
            'placeholder': 'Tell me about your project, requirements, and goals...',
            'rows': 6,
            'required': True
        })
        
        # Update labels
        self.fields['full_name'].label = 'Full Name'
        self.fields['email'].label = 'Email Address'
        self.fields['phone'].label = 'Phone Number'
        self.fields['company'].label = 'Company'
        self.fields['budget'].label = 'Budget Range'
        self.fields['timeline'].label = 'Timeline'
        self.fields['message'].label = 'Project Details'

    def clean_message(self):
        """Validate message length."""
        message = self.cleaned_data.get('message')
        if message and len(message) < 20:
            raise ValidationError("Message must be at least 20 characters long.")
        return message


class LeadStatusUpdateForm(forms.ModelForm):
    """Form for updating lead status on dashboard."""
    
    class Meta:
        model = Lead
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['status'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600'
        })
        self.fields['status'].label = 'Status'
