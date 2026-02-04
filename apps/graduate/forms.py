from django import forms
from .models import Graduate, GraduateAchievement
from apps.student.models import Student
from apps.group.models import Group


class GraduateForm(forms.ModelForm):
    class Meta:
        model = Graduate
        fields = [
            'student', 'graduation_date', 'graduation_group', 'final_grade',
            'diploma_number', 'achievements', 'current_occupation',
            'contact_phone', 'contact_email', 'notes'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'graduation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'graduation_group': forms.Select(attrs={'class': 'form-control'}),
            'final_grade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '1', 'max': '5'}),
            'diploma_number': forms.TextInput(attrs={'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'current_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'student': 'Студент',
            'graduation_date': 'Дата выпуска',
            'graduation_group': 'Группа выпуска',
            'final_grade': 'Итоговая оценка',
            'diploma_number': 'Номер диплома',
            'achievements': 'Достижения во время обучения',
            'current_occupation': 'Текущая деятельность',
            'contact_phone': 'Контактный телефон',
            'contact_email': 'Email',
            'notes': 'Примечания',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Настраиваем отображение групп
        self.fields['graduation_group'].queryset = Group.objects.all()
        self.fields['graduation_group'].empty_label = "Выберите группу"
        
        # Настраиваем отображение студентов
        self.fields['student'].queryset = Student.objects.filter(student_status='active')
        self.fields['student'].empty_label = "Выберите студента"

    def clean_final_grade(self):
        final_grade = self.cleaned_data.get('final_grade')
        if final_grade is not None and (final_grade < 1 or final_grade > 5):
            raise forms.ValidationError('Оценка должна быть от 1 до 5')
        return final_grade

    def clean_student(self):
        student = self.cleaned_data.get('student')
        if student:
            # Проверяем, не является ли студент уже выпускником
            if hasattr(student, 'graduate_info'):
                raise forms.ValidationError('Этот студент уже является выпускником.')
            # Проверяем статус студента
            if student.student_status != 'active':
                raise forms.ValidationError('Можно переводить в выпускники только активных студентов.')
        return student


class MakeGraduateForm(forms.ModelForm):
    """Специальная форма для перевода студента в выпускники"""
    
    graduation_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Дата выпуска',
        required=True
    )
    
    class Meta:
        model = Graduate
        fields = [
            'graduation_date', 'graduation_group', 'final_grade',
            'diploma_number', 'achievements', 'current_occupation',
            'contact_phone', 'contact_email', 'notes'
        ]
        widgets = {
            'graduation_group': forms.Select(attrs={'class': 'form-control'}),
            'final_grade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '1', 'max': '5'}),
            'diploma_number': forms.TextInput(attrs={'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'current_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'graduation_group': 'Группа выпуска',
            'final_grade': 'Итоговая оценка',
            'diploma_number': 'Номер диплома',
            'achievements': 'Достижения во время обучения',
            'current_occupation': 'Текущая деятельность',
            'contact_phone': 'Контактный телефон',
            'contact_email': 'Email',
            'notes': 'Примечания',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Настраиваем отображение групп
        self.fields['graduation_group'].queryset = Group.objects.all()
        self.fields['graduation_group'].empty_label = "Выберите группу"
    def clean_final_grade(self):
        final_grade = self.cleaned_data.get('final_grade')
        if final_grade is not None and (final_grade < 1 or final_grade > 5):
            raise forms.ValidationError('Оценка должна быть от 1 до 5')
        return final_grade

    def clean_diploma_number(self):
        diploma_number = self.cleaned_data.get('diploma_number')
        if diploma_number:
            # Проверяем уникальность номера диплома
            if Graduate.objects.filter(diploma_number=diploma_number).exists():
                raise forms.ValidationError('Выпускник с таким номером диплома уже существует.')
        return diploma_number


class GraduateAchievementForm(forms.ModelForm):
    class Meta:
        model = GraduateAchievement
        fields = ['title', 'description', 'date_achieved', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_achieved': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название достижения',
            'description': 'Описание',
            'date_achieved': 'Дата достижения',
            'category': 'Категория',
        }


class GraduateSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по имени или номеру диплома...'
        })
    )
    year = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[('', 'Все годы')]
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        empty_label="Все группы",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически добавляем годы выпуска
        years = Graduate.objects.values_list('graduation_date__year', flat=True).distinct().order_by('-graduation_date__year')
        year_choices = [('', 'Все годы')] + [(year, str(year)) for year in years]
        self.fields['year'].choices = year_choices