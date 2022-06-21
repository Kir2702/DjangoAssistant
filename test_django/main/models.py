from django.db import models

class Templates(models.Model):
    title = models.CharField(max_length=100, verbose_name='Тип')
    content = models.TextField(null=True, blank=True, verbose_name='Шаблон')

    class Meta:
        verbose_name_plural = 'Шаблоны ответов'
        verbose_name = 'Шаблон ответа'