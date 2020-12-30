import datetime

from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    DetailView,
    TemplateView,
    UpdateView,
)
from django.utils.html import escape
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from django.conf import settings

from covid import mixins
from covid import models
from covid import forms


class IndexView(mixins.LoginRequiredMixin, TemplateView):
    template_name = "covid/index.html"


class HelpView(TemplateView):
    template_name = "covid/help.html"


class ReadPermmissionHelpView(TemplateView):
    template_name = "covid/read_permission_help.html"


class WritePermmissionHelpView(TemplateView):
    template_name = "covid/write_permission_help.html"


class PatientsView(mixins.UserCheckMixin, ListView):
    context_object_name = "PATIENTS"
    queryset = models.Name.objects.order_by("surname", "first_name").filter(
        is_default=True
    )
    template_name = "covid/patient_list.html"


class RecordListView(mixins.UserCheckMixin, ListView):
    context_object_name = "RECORDS"
    model = models.Record
    template_name = "covid/record_list.html"


class RecordView(mixins.UserCheckMixin, DetailView):
    context_object_name = "RECORD"
    model = models.Record
    template_name = "covid/record.html"


class RecentNotesView(mixins.UserCheckMixin, ListView):
    context_object_name = "NOTES"
    template_name = "covid/recent_notes.html"

    def get_queryset(self):
        d = datetime.date.today() - datetime.timedelta(days=7)
        return models.Note.objects.filter(date_created__gt=d).order_by("-date_created")


class NamesView(mixins.UserCheckMixin, DetailView):
    context_object_name = "RECORD"
    model = models.Record
    template_name = "covid/record_names.html"


class NameAddView(mixins.CovidWriteRecordsMixin, DetailView, CreateView):
    context_object_name = "RECORD"
    form_class = forms.AddNameForm
    model = models.Record
    template_name = "covid/record_name_edit.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        # because of many_to_1 and is_default
        record_obj = self.get_object()
        name_obj = form.instance
        name_obj.record = record_obj
        response = super().form_valid(form)
        if name_obj.is_default:
            for other_name in record_obj.name_set.all():
                other_name.is_default = False
                other_name.save()
        name_obj.save()
        return response


class NameEditView(mixins.CovidWriteRecordsMixin, UpdateView):
    context_object_name = "NAME"
    form_class = forms.EditNameForm
    model = models.Name
    template_name = "covid/record_name_edit.html"

    def get_success_url(self):
        return self.get_object().record.get_absolute_url()

    def form_valid(self, form):
        # do some jiggling upon name save
        # because of many_to_many and is_default
        response = super().form_valid(form)
        name_obj = self.get_object()
        if name_obj.is_default:
            record_obj = name_obj.record
            for other_name in record_obj.name_set.all():
                if other_name.id == name_obj.id:
                    continue
                other_name.is_default = False
                other_name.save()
        return response


class AllActionsView(mixins.UserCheckMixin, ListView):
    """
    View all actions on the system.
    """

    context_object_name = "ACTIONS"
    model = models.Action
    template_name = "covid/action_list.html"


class ActionsView(mixins.UserCheckMixin, DetailView):
    """
    View all actions for a given record.
    """

    context_object_name = "RECORD"
    model = models.Record
    template_name = "covid/actions.html"


class ActionAddView(mixins.CovidWriteRecordsMixin, DetailView, CreateView):
    context_object_name = "RECORD"
    form_class = forms.ActionForm
    model = models.Record
    template_name = "covid/action_new.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        record_obj = self.get_object()
        action_obj = form.instance
        action_obj.record = record_obj
        action_obj.save()
        return super().form_valid(form)


class ActionEditView(mixins.CovidWriteRecordsMixin, UpdateView):
    context_object_name = "ACTION"
    form_class = forms.ActionForm
    model = models.Action
    template_name = "covid/action_edit.html"

    def get_success_url(self):
        return self.get_object().record.get_absolute_url()


class AddressView(mixins.UserCheckMixin, DetailView):
    context_object_name = "RECORD"
    model = models.Record
    template_name = "covid/record_address.html"


class AddressAddView(mixins.CovidWriteRecordsMixin, DetailView, CreateView):
    context_object_name = "RECORD"
    form_class = forms.AddressAddForm
    model = models.Record
    template_name = "covid/record_address_edit.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        # do some jiggling upon name save
        # because of many_to_many and is_default
        record_obj = self.get_object()
        response = super().form_valid(form)
        address_obj = self.object
        address_obj.record_set.add(record_obj)
        return response


class AddressEditView(mixins.CovidWriteRecordsMixin, UpdateView):
    context_object_name = "RECORD"
    form_class = forms.AddressEditForm
    model = models.Address
    template_name = "covid/record_address_edit.html"

    def get_success_url(self):
        return self.get_object().record_url()


class AddressDeleteView(mixins.CovidWriteRecordsMixin, DeleteView):
    model = models.Address
    template_name = "covid/address_confirm_delete.html"

    def get_success_url(self):
        return self.get_object().record_url()


class TelephoneView(mixins.UserCheckMixin, DetailView):
    context_object_name = "RECORD"
    model = models.Record
    template_name = "covid/record_telephone.html"


class TelephoneAddView(mixins.CovidWriteRecordsMixin, DetailView, CreateView):
    context_object_name = "RECORD"
    form_class = forms.TelephoneAddForm
    model = models.Record
    template_name = "covid/record_telephone_edit.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        # do some jiggling upon name save
        # because of many_to_many and is_default
        record_obj = self.get_object()
        response = super().form_valid(form)
        telephone_obj = self.object
        telephone_obj.record_set.add(record_obj)
        return response


class TelephoneEditView(mixins.CovidWriteRecordsMixin, UpdateView):
    form_class = forms.TelephoneEditForm
    model = models.Telephone
    template_name = "covid/record_telephone_edit.html"

    def get_success_url(self):
        return self.get_object().record_url()


class TelephoneDeleteView(mixins.CovidWriteRecordsMixin, DeleteView):
    model = models.Telephone
    template_name = "covid/telephone_confirm_delete.html"

    def get_success_url(self):
        return self.get_object().record_url()


class EmailView(mixins.UserCheckMixin, DetailView):
    context_object_name = "RECORD"
    model = models.Record
    template_name = "covid/record_email.html"


class EmailAddView(mixins.CovidWriteRecordsMixin, DetailView, CreateView):
    context_object_name = "RECORD"
    form_class = forms.EmailAddForm
    model = models.Record
    template_name = "covid/record_email_edit.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        # do some jiggling upon name save
        # because of many_to_many and is_default
        record_obj = self.get_object()
        response = super().form_valid(form)
        email_obj = self.object
        email_obj.record_set.add(record_obj)
        return response


class EmailEditView(mixins.CovidWriteRecordsMixin, UpdateView):
    form_class = forms.EmailEditForm
    model = models.Email
    template_name = "covid/record_email_edit.html"

    def get_success_url(self):
        return self.get_object().record_url()


@method_decorator(csrf_exempt, name="dispatch")
class SearchView(mixins.CovidWriteRecordsMixin, FormView):
    context_object_name = "RECORD"
    form_class = forms.SearchForm
    template_name = "covid/search.html"
    year, month, day = (0, 0, 0)
    first_name = "-"
    surname = "-"

    def get_success_url(self):
        return reverse(
            "covid-search-result",
            args=[
                self.year,
                self.month,
                self.day,
                "SN" + self.surname,
                "FN" + self.first_name,
            ],
        )

    def form_valid(self, form):
        dob = form.cleaned_data["dob"]
        self.year = dob.year
        self.month = dob.month
        self.day = dob.day
        self.first_name = form.cleaned_data["first_name"]
        self.surname = form.cleaned_data["surname"]
        response = super().form_valid(form)
        return response


class SearchResultView(mixins.CovidWriteRecordsMixin, ListView):
    context_object_name = "RECORDS"
    template_name = "covid/search_results.html"

    def get_queryset(self):
        dob = datetime.date(
            self.kwargs["year"], self.kwargs["month"], self.kwargs["day"]
        )
        sname = self.kwargs["sname"][2:]
        fname = self.kwargs["fname"][2:]

        if dob != datetime.date(2020, 1, 1):  # default
            for obj in models.Record.objects.filter(dob=dob):
                yield obj
        for obj in (
            models.Name.objects.filter(surname__istartswith=sname)
            .filter(first_name__istartswith=fname)
            .order_by("surname")
            .order_by("first_name")
        ):
            yield obj.record


@method_decorator(csrf_exempt, name="dispatch")
class DuplicatesView(mixins.UserCheckMixin, TemplateView):
    """
    return a list of duplicates

    url is in the form covid/new/dupes/year/month/day/SNsurname/FNfirstname/
    (SN and FN allow for null values)
    """

    template_name = "covid/duplicate_list.html"

    def get_context_data(self, *args, **kwargs):
        dob_dupes, name_dupes = [], []
        context = super().get_context_data(*args, **kwargs)
        dob = datetime.date(kwargs["year"], kwargs["month"], kwargs["day"])
        sname = kwargs["sname"][2:]
        fname = kwargs["fname"][2:]
        if dob != datetime.date(2020, 1, 1):  # default
            context["DOB_DUPLICATES"] = models.Record.objects.filter(dob=dob)
        if sname or fname:
            context["NAME_DUPLICATES"] = (
                models.Name.objects.filter(surname__istartswith=sname)
                .filter(first_name__istartswith=fname)
                .order_by("surname")
                .order_by("first_name")
            )
        return context


@method_decorator(csrf_exempt, name="dispatch")
class NewRecordView(
    mixins.CovidWriteRecordsMixin,
    FormView,
):
    context_object_name = "RECORD"
    form_class = forms.NewRecordForm
    template_name = "covid/new_record.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        record = models.Record()
        record.dob = form.cleaned_data["dob"]
        record.dentist = form.cleaned_data["dentist"]
        record.save()
        self.object = record
        name = models.Name()
        name.title = form.cleaned_data["title"]
        name.first_name = form.cleaned_data["first_name"]
        name.middle_name = form.cleaned_data["middle_name"]
        name.surname = form.cleaned_data["surname"]
        name.record = record
        name.save()
        tel_number = form.cleaned_data["telephone"]
        if tel_number:
            telephone = models.Telephone()
            telephone.number = tel_number
            telephone.save()
            record.telephones.add(telephone)
        response = super().form_valid(form)

        return response


class EditRecordView(mixins.CovidWriteRecordsMixin, UpdateView):
    context_object_name = "RECORD"
    form_class = forms.EditRecordForm
    model = models.Record
    template_name = "covid/record_edit.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class MedHistAddView(mixins.CovidWriteRecordsMixin, DetailView, CreateView):
    context_object_name = "RECORD"
    form_class = forms.MedHistForm
    model = models.Record
    template_name = "covid/medical_history.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        record_obj = self.get_object()
        mh_obj = form.instance
        mh_obj.record = record_obj
        mh_obj.save()
        notes_form = form.notes_form
        notes_form.is_valid()
        for category, field in notes_form.MAPPING.items():
            value = notes_form.cleaned_data[field]
            if value:
                mednote = models.MedicalNote(
                    category=category, note=value, medhist=mh_obj
                )
                mednote.save()
        return super().form_valid(form)


class MedHistEditView(mixins.CovidWriteRecordsMixin, UpdateView):
    context_object_name = "MEDHIST"
    form_class = forms.MedHistForm
    model = models.MedicalHistory
    template_name = "covid/medical_history_edit.html"

    def get_initial(self):
        return {
            "medication_text": self.object.medication_to_text,
        }

    def get_success_url(self):
        return self.get_object().record.get_absolute_url()

    def _new_medication_text(self):
        text = self.get_object().medication_text
        med_set = sorted(set(text.split("\n")))
        return "\n".join([escape(m) for m in med_set])

    def form_valid(self, form):
        mh_obj = self.get_object()
        mh_obj.medication_text = self._new_medication_text()
        mh_obj.save()

        notes_form = form.notes_form
        notes_form.is_valid()
        if notes_form.has_changed:
            for n in mh_obj.medicalnote_set.all():
                n.delete()
            for category, field in notes_form.MAPPING.items():
                value = notes_form.cleaned_data[field]
                if value:
                    mednote = models.MedicalNote(
                        category=category, note=value, medhist=mh_obj
                    )
                    mednote.save()
        return super().form_valid(form)


class MedHistsView(mixins.UserCheckMixin, DetailView):
    model = models.Record
    template_name = "covid/medical_history_view.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["MEDHISTS"] = models.MedicalHistory.objects.filter(
            record=self.get_object()
        )
        return context


class NoteAddView(mixins.CovidWriteRecordsMixin, DetailView, CreateView):
    context_object_name = "RECORD"
    form_class = forms.NoteAddForm
    model = models.Record
    template_name = "covid/new_note.html"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        record_obj = self.get_object()
        note_obj = form.instance
        note_obj.record = record_obj
        note_obj.save()
        return super().form_valid(form)


class PharmacyView(ListView):
    context_object_name = "PHARMACIES"
    model = models.Pharmacy
    template_name = "covid/pharmacies.html"


class ActivityView(TemplateView):
    template_name = "covid/activity.html"

    def get_context_data(self):
        context = super().get_context_data()

        ag = models.ActivityGraph()

        context["categories"] = list(ag.date_range())
        context["values"] = list(ag.activity_counts())
        context["table_data"] = ag.as_table()

        return context
