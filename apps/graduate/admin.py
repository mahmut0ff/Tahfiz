from django.contrib import admin
from .models import Graduate, GraduateAchievement


@admin.register(Graduate)
class GraduateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'graduation_date', 'graduation_group', 'final_grade', 'diploma_number']
    list_filter = ['graduation_date', 'graduation_group', 'final_grade']
    search_fields = ['student__name', 'student__user__first_name', 'student__user__last_name', 'diploma_number']
    date_hierarchy = 'graduation_date'
    ordering = ['-graduation_date']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('student', 'graduation_date', 'graduation_group', 'final_grade', 'diploma_number')
        }),
        ('Достижения и деятельность', {
            'fields': ('achievements', 'current_occupation')
        }),
        ('Контактная информация', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Дополнительно', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GraduateAchievement)
class GraduateAchievementAdmin(admin.ModelAdmin):
    list_display = ['graduate', 'title', 'category', 'date_achieved']
    list_filter = ['category', 'date_achieved']
    search_fields = ['graduate__student__name', 'title', 'description']
    date_hierarchy = 'date_achieved'
    ordering = ['-date_achieved']