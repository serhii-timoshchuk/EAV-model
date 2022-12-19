from django.contrib import admin
from .models import ATTRIBUTE_TYPES
from .models import ProductType, PropertyType, PropertyInstance, ProductInstance, Choices
from django import forms


admin.site.register(ProductType)
admin.site.register(PropertyInstance)



class ChoicesAdmin(admin.TabularInline):

    model = Choices


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    inlines = [ChoicesAdmin,]


class TEstFrom(forms.ModelForm):

    class Meta:
        model = ProductInstance
        fields = '__all__'



# class PropertyInstanceAdmin(admin.StackedInline):
#
#     model = PropertyInstance
#     extra = 1
#
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#
#
#         if db_field.name == "property_type":
#
#             prod = request.resolver_match.kwargs.get('object_id')
#             result = PropertyType.objects.none()
#
#             try:
#                 prod = ProductInstance.objects.get(id=prod)
#             except ProductInstance.DoesNotExist:
#                 pass
#             else:
#                 if prod.product_type is not None:
#                     result = PropertyType.objects.filter(product_type=prod.product_type)
#                     print(result)
#             finally:
#                 kwargs["queryset"] = result
#
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
#
#
# #
# @admin.register(ProductInstance)
# class ProductTypeAdmin(admin.ModelAdmin):
#     inlines = [PropertyInstanceAdmin,]


@admin.register(ProductInstance)
class ProductTypeAdmin(admin.ModelAdmin):
    form = TEstFrom

    def get_fields(self, request, obj=None):
        gf = super(ProductTypeAdmin, self).get_fields(request, obj)

        all_properties = [x.key for x in PropertyType.objects.all()]

        for x in all_properties:
            if x in gf:
                gf.remove(x)
            if self.form.declared_fields.get(x, False):
                del self.form.declared_fields[x]

        if obj:

            obj_properties = PropertyType.objects.filter(product_type=obj.product_type)
            new_dynamic_fields = []
            for property_type in obj_properties:

                if property_type.type == 'int_choice':
                    try:
                        property = PropertyInstance.objects.get(product_instance=obj, property_type=property_type)
                    except PropertyInstance.DoesNotExist:
                        new_dynamic_fields.append(
                            (property_type.key, ATTRIBUTE_TYPES[property_type.type][1](queryset=Choices.objects.all(),
                                                                                       required=False))
                        )
                    else:
                        new_dynamic_fields.append(
                            (property_type.key, ATTRIBUTE_TYPES[property_type.type][1](queryset=Choices.objects.all(),
                                                                                       required=False, initial=property.value))
                        )



                else:
                    try:
                        property = PropertyInstance.objects.get(product_instance=obj, property_type=property_type)
                    except PropertyInstance.DoesNotExist:
                        new_dynamic_fields.append(
                            (property_type.key, ATTRIBUTE_TYPES[property_type.type][1](required=False))
                        )
                    else:
                        new_dynamic_fields.append(
                            (property_type.key, ATTRIBUTE_TYPES[property_type.type][1](required=False, initial=property.value))
                        )

            # new_dynamic_fields = [
            #     ('test', forms.CharField(required=False)),
            #     ('test2', forms.ModelMultipleChoiceField(ProductInstance.objects.all(),
            #                                              widget=forms.CheckboxSelectMultiple)),
            # ]

            for f in new_dynamic_fields:
                #`gf.append(f[0])` results in multiple instances of the new fields
                gf = gf + [f[0]]
                #updating base_fields seems to have the same effect
                self.form.declared_fields.update({f[0]:f[1]})
        return gf


    def save_model(self, request, obj, form, change):
        print('ENTER SAVE MODEL')
        print(vars(form))
        print(form.cleaned_data)
        print(obj.__dict__)
        s = super().save_model(request, obj, form, change)

        print(obj.__dict__)
        if obj and obj.id is not None and obj.product_type is not None:
            # get all properties for particular product type
            all_properties = PropertyType.objects.filter(product_type=obj.product_type)
            print(all_properties)
            for property in all_properties:
                value = form.cleaned_data.get(property.key, False)
                if value:
                    property_ins = PropertyInstance.objects.filter(product_instance=obj, property_type=property)
                    if property_ins.exists():
                        if property.type == 'int_choice':
                            print(value)
                            property_ins = property_ins.first()
                            property_ins.value = value.choice
                            property_ins.save()
                        else:
                            property_ins = property_ins.first()
                            property_ins.value = value
                            property_ins.save()
                    else:
                        PropertyInstance.objects.create(product_instance=obj, property_type=property, value=value)
