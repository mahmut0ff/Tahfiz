from django import forms
from .models import *


class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'id': 'name',
                'placeholder': 'Название предмета...'
            }),

        }


class ScheduleForm(forms.ModelForm):

    class Meta:
        model = Schedule
        fields = ['group', 'day', 'subject', 'time_slot']
        widgets = {
            'group': forms.Select(attrs={
                    'class': 'form-control',
                    'id': 'group',
                }),
            'day': forms.Select(attrs={
                    'class': 'form-control',
                    'id': 'day',
                }),
            'subject': forms.Select(attrs={
                    'class': 'form-control',
                    'id': 'subject',
                }),
            'time_slot': forms.NumberInput(attrs={
                    'class': 'form-control',
                    'id': 'time_slot',
                    'max': 6,
                    'min': 1
                })
        }
