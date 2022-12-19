from django.db import models
from django import forms


ATTRIBUTE_TYPES = {
    'string': ('string', forms.CharField),
    'boolean': ('boolean', forms.BooleanField),
    'integer': ('integer', forms.IntegerField),
    'decimal': ('decimal', forms.DecimalField),
    'int_choice': ('int_choice', forms.ModelChoiceField),
}





class ProductType(models.Model):

    name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.name



class ProductInstance(models.Model):

    product_type = models.ForeignKey(ProductType, blank=True, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=150, blank=False)

    def __str__(self):
        return self.name


class PropertyType(models.Model):

    TYPES = (
        ('string', 'string'),
        ('boolean', 'boolean'),
        ('integer', 'integer'),
        ('decimal', 'decimal'),
        ('int_choice', 'int_choice'),
    )

    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    key = models.SlugField(unique=True, blank=False, null=False)
    name = models.CharField(max_length=150, blank=True)
    type = models.CharField(max_length=150, choices=TYPES)


    def __str__(self):
        return self.name


class PropertyInstance(models.Model):

    product_instance = models.ForeignKey(ProductInstance, on_delete=models.CASCADE)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ('product_instance', 'property_type',)

    def __str__(self):
        return self.value


class Choices(models.Model):

    choice = models.CharField(max_length=150)
    property_instance = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
