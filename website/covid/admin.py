from django.contrib import admin

from covid import models

admin.site.register(models.Record)
admin.site.register(models.Name)
admin.site.register(models.Address)
admin.site.register(models.Telephone)
admin.site.register(models.Email)
admin.site.register(models.Note)
admin.site.register(models.MedicalHistory)
admin.site.register(models.MedicalNote)
admin.site.register(models.Action)
admin.site.register(models.Pharmacy)
