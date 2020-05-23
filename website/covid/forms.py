import re

from django import forms
from django.utils.html import escape
from django.conf import settings
from covid import models

YEARS = range(2020, 1900, -1)


class PatientLoginForm(forms.Form):
    token = forms.CharField(label="Token", max_length=12)
    dob = forms.DateField(
        label="Date of Birth", widget=forms.SelectDateWidget(years=YEARS)
    )


class NewRecordForm(forms.Form):
    title = forms.CharField(label="Title", max_length=20, required=False)
    first_name = forms.CharField(label="First Name (required)", max_length=40)
    middle_name = forms.CharField(
        label="Middle Name", max_length=40, required=False
    )
    surname = forms.CharField(label="Surname (required)", max_length=40)
    dob = forms.DateField(
        label="Date of Birth", widget=forms.SelectDateWidget(years=YEARS)
    )
    dentist = forms.CharField(
        label="Regular Dentist", max_length=100, required=False
    )
    telephone = forms.CharField(
        label="Telephone number", max_length=20, required=False
    )


class EditRecordForm(forms.ModelForm):
    class Meta:
        model = models.Record
        fields = ["chi", "alt_ref", "dentist", "dob"]
        widgets = {"dob": forms.SelectDateWidget(years=YEARS)}


class EditNameForm(forms.ModelForm):
    class Meta:
        model = models.Name
        fields = [
            "title",
            "first_name",
            "middle_name",
            "surname",
            "is_default",
        ]


class AddNameForm(EditNameForm):
    pass


class AddressEditForm(forms.ModelForm):
    class Meta:
        model = models.Address
        fields = [
            "addr1",
            "addr2",
            "addr3",
            "addr4",
            "town",
            "country",
            "postcode",
        ]


class AddressAddForm(AddressEditForm):
    pass


class TelephoneEditForm(forms.ModelForm):
    class Meta:
        model = models.Telephone
        fields = ["number", "accepts_sms"]


class TelephoneAddForm(TelephoneEditForm):
    pass


class EmailEditForm(forms.ModelForm):
    class Meta:
        model = models.Email
        fields = ["email"]


class EmailAddForm(EmailEditForm):
    pass


class ActionForm(forms.ModelForm):
    class Meta:
        model = models.Action
        fields = ["action", "is_urgent", "is_completed"]


class MedNotesForm(forms.Form):
    """
    fields here should match models.MedicalNote.CATEGORIES
    """

    CATEGORIES = models.MedicalNote.CATEGORIES
    other = forms.CharField(
        label=CATEGORIES[0][1],
        widget=forms.Textarea(attrs={"cols": 40, "rows": 2}),
        strip=True,
        required=False,
    )
    warning = forms.CharField(
        label=CATEGORIES[1][1],
        widget=forms.Textarea(attrs={"cols": 40, "rows": 2}),
        strip=True,
        required=False,
    )
    habit = forms.CharField(
        label=CATEGORIES[2][1],
        widget=forms.Textarea(attrs={"cols": 40, "rows": 2}),
        strip=True,
        required=False,
    )
    heart = forms.CharField(
        label=CATEGORIES[3][1],
        widget=forms.Textarea(attrs={"cols": 40, "rows": 2}),
        strip=True,
        required=False,
    )
    chest = forms.CharField(
        label=CATEGORIES[4][1],
        widget=forms.Textarea(attrs={"cols": 40, "rows": 2}),
        strip=True,
        required=False,
    )
    blood = forms.CharField(
        label=CATEGORIES[5][1],
        widget=forms.Textarea(attrs={"cols": 40, "rows": 2}),
        strip=True,
        required=False,
    )
    allergy = forms.CharField(
        label=CATEGORIES[6][1],
        widget=forms.Textarea(attrs={"cols": 40, "rows": 2}),
        strip=True,
        required=False,
    )
    MAPPING = {
        models.MedicalNote.OTHER: "other",
        models.MedicalNote.WARNING: "warning",
        models.MedicalNote.HABIT: "habit",
        models.MedicalNote.HEART: "heart",
        models.MedicalNote.CHEST: "chest",
        models.MedicalNote.BLOOD: "blood",
        models.MedicalNote.ALLERGY: "allergy",
    }


class MedHistForm(forms.ModelForm):
    class Meta:
        model = models.MedicalHistory
        fields = ["author", "medication_text"]
        labels = {"medication_text": "Medications"}
        widgets = {
            "medication_text": forms.Textarea(attrs={"cols": 40, "rows": 6})
        }

    def __init__(self, *args, **kwargs):
        """
        If called from a CreateView the instance will be a models.Record
        object
        When called during save, however, or when called by an UpdateView,
        the object will bethe instance will be a models.MedicalHistory
        """
        super().__init__(*args, **kwargs)
        if isinstance(self.instance, models.Record):
            record = self.instance
            self.medical_history_object = models.MedicalHistory(record=record)
        else:
            self.medical_history_object = self.instance
        mednoteset = self.medical_history_object.medicalnote_set

        # now load values into the notes form,
        # either from the post data (within kwargs)
        # or from the database
        initial_notes_data = {}
        try:
            data = kwargs["data"]
            for i, field in MedNotesForm.MAPPING.items():
                initial_notes_data[field] = data.get(field, "?")
        except KeyError:  # no data in kwargs
            for i, field in MedNotesForm.MAPPING.items():
                med_notes = mednoteset.filter(category=i)
                med_note = "\n".join([escape(n.note) for n in med_notes])
                initial_notes_data[field] = med_note
        self.notes_form = MedNotesForm(initial_notes_data)

    def as_table(self, *args, **kwargs):
        mednote_set = self.medical_history_object.medicalnote_set
        html = super().as_table(*args, **kwargs)
        html += self.notes_form.as_table()
        return html


class NoteAddForm(forms.ModelForm):
    class Meta:
        model = models.Note
        fields = ["author", "note"]
