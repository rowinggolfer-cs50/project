import datetime

from django.urls import reverse
from django.db import models
from django.db import connection
from django.utils.html import escape
from django.utils import formats

from django.conf import settings

WEEKDAYS = (
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri",
    "Sat",
    "Sun",
)


# with sqlite - this query returns not a datetime.date object but
# a string in the form '2020-05-21'.
# postgres returns datetime.date

ACTIVITY_QUERY = (
    "SELECT d covid_date, count(*) call_count FROM "
    "(SELECT date(date_created) d FROM covid_note GROUP BY "
    "record_id, date(date_created)) AS t GROUP BY d ORDER BY d"
)


class Address(models.Model):
    """
    address table has a many to many relationship with record
    """

    class Meta:
        verbose_name_plural = "Addresses"

    addr1 = models.CharField(max_length=120)
    addr2 = models.CharField(max_length=120, null=True, blank=True)
    addr3 = models.CharField(max_length=120, null=True, blank=True)
    addr4 = models.CharField(max_length=120, null=True, blank=True)
    town = models.CharField(max_length=120, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    date_edited = models.DateTimeField(auto_now=True)

    def formatted_address(self):
        try:
            return get_escaped(
                [
                    self.addr1,
                    self.addr2,
                    self.addr3,
                    self.addr4,
                    self.town,
                    self.country,
                    self.postcode,
                ],
                seperator=", ",
            )
        except:
            return "error getting address"

    def get_edit_url(self):
        return reverse("covid-address-edit", args=[str(self.id)])

    def get_delete_url(self):
        return reverse("covid-address-delete", args=[str(self.id)])

    def record_url(self):
        # TODO this may be problematic if address associated with several
        # records - could give the wrong "success_url"
        return self.record_set.first().get_absolute_url()

    def __str__(self):
        return self.formatted_address()


class Telephone(models.Model):
    number = models.CharField(max_length=20)
    accepts_sms = models.NullBooleanField()
    date_edited = models.DateTimeField(auto_now=True)

    def get_edit_url(self):
        return reverse("covid-telephone-edit", args=[str(self.id)])

    def get_delete_url(self):
        return reverse("covid-telephone-delete", args=[str(self.id)])

    def __str__(self):
        return self.number

    def record_url(self):
        # TODO this may be problematic if address associated with several
        # records - could give the wrong "success_url"
        return self.record_set.first().get_absolute_url()


class Email(models.Model):
    class Meta:
        ordering = ("email",)

    email = models.EmailField()
    date_edited = models.DateTimeField(auto_now=True)

    def get_edit_url(self):
        return reverse("covid-email-edit", args=[str(self.id)])

    def record_url(self):
        return self.record_set.first().get_absolute_url()

    def __str__(self):
        return self.email


class Record(models.Model):
    class Meta:
        ordering = ("-date_created",)

    dob = models.DateField()
    chi = models.CharField(max_length=10, null=True, blank=True)
    alt_ref = models.CharField(max_length=40, null=True, blank=True)
    dentist = models.CharField(max_length=100, null=True, blank=True)
    addresses = models.ManyToManyField(Address, blank=True)
    telephones = models.ManyToManyField(Telephone, blank=True)
    emails = models.ManyToManyField(Email, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def name(self):
        try:
            object = self.name_set.get(is_default=True)
            return object.name
        except:
            return "NAME ERROR"

    @property
    def address_obj(self):
        return self.addresses.order_by("date_edited").last()

    @property
    def address(self):
        try:
            return self.address_obj.formatted_address()
        except AttributeError:
            return "unknown address"

    @property
    def all_addresses(self):
        return "<br />\n".join([ad.formatted_address() for ad in self.addresses.all()])

    @property
    def telephone_numbers(self):
        return "<br />\n".join([escape(t.number) for t in self.telephones.all()])

    @property
    def actions(self):
        return self.action_set.all()

    @property
    def incomplete_actions(self):
        for action in self.action_set.all():
            if not action.is_completed:
                yield action

    def actions_as_list(self):
        return "\n".join(["- %s" % a.action for a in self.incomplete_actions])

    def view_all_actions_url(self):
        return reverse("covid-view-all-actions", args=[str(self.id)])

    def get_add_action_url(self):
        return reverse("covid-action-add", args=[str(self.id)])

    @property
    def has_urgent_actions(self):
        for action in self.actions:
            if action.is_urgent and not action.is_completed:
                return True
        return False

    @property
    def has_actions(self):
        for action in self.actions:
            if not action.is_completed:
                return True
        return False

    @property
    def email_addresses(self):
        def w(email):
            return '<a href="mailto:%s">%s</a>' % (email, email)

        return "<br />\n".join([w(t.email) for t in self.emails.all()])

    @property
    def details_as_table(self):
        html = ""
        for key, value in (
            ("Name", self.name),
            ("Date of Birth", formats.date_format(self.dob, "DATE_FORMAT")),
            ("CHI", self.chi if self.chi else ""),
            ("Regular Dentist", self.dentist if self.dentist else ""),
            ("Address(es)", self.all_addresses),
            ("Telephone(s)", self.telephone_numbers),
            ("Email(s)", self.email_addresses),
        ):
            html += "<tr><th class='text-right'>%s :</th><td>%s</td></tr>\n" % (
                key,
                value,
            )
        return html

    @property
    def has_no_medhists(self):
        """
        do we have multiple medical histories for this patient?
        """
        return self.medicalhistory_set.count() == 0

    @property
    def has_multiple_medhists(self):
        """
        do we have multiple medical histories for this patient?
        """
        return self.medicalhistory_set.count() > 1

    @property
    def current_medical_history(self):
        return self.medicalhistory_set.last()

    def medhist_as_table(self):
        try:
            return self.current_medical_history.details_as_table
        except AttributeError as exc:  # no mh as yet?
            return ""

    def medhist_date(self):
        try:
            return self.current_medical_history.date_created
        except AttributeError as exc:  # no mh as yet?
            return ""

    def medhist_author(self):
        try:
            return self.current_medical_history.author
        except AttributeError as exc:  # no mh as yet?
            return ""

    def view_record_medhists_url(self):
        return reverse("covid-view-all-medhists", args=[str(self.id)])

    def medhist_edit_url(self):
        try:
            return reverse("covid-mh-edit", args=[str(self.current_medical_history.id)])
        except AttributeError as exc:  # no mh as yet?
            print(exc)
            return ""

    @property
    def last_note(self):
        return self.note_set.last()

    def _last_note_date(self):
        """
        returns a tuple.
        (date time created, is_this_week)
        """
        n = self.last_note
        if n:
            now = datetime.datetime.now()
            n_date = n.date_created.astimezone()
            return (n_date, n_date.isocalendar()[1] == now.isocalendar()[1])
        return (None, None)

    @property
    def recent_note_date(self):
        """
        return the datetime of the lastest note on this patient
        in BOLD - template allows this value as safe
        """
        dt, is_this_week = self._last_note_date()
        if dt is not None and is_this_week:
            return "<strong>%s %s:%02d</strong>" % (
                WEEKDAYS[dt.weekday()],
                dt.hour,
                dt.minute,
            )
        return ""

    @property
    def last_note_date(self):
        """
        return the datetime of the lastest notet
        """
        dt, is_this_week = self._last_note_date()
        if dt is not None:
            if not is_this_week:
                return dt.date
        return ""

    @property
    def last_note_initials(self):
        """
        return the initials of the last note author
        """
        note = self.last_note
        if note:
            return note.author_initials
        return ""

    @property
    def notes_as_table(self):
        html = "<tr><th>%s</th><th>%s</th></tr>" % ("Date", "Note")
        for note in self.note_set.all():
            html += note.as_table_row
        return html

    def get_absolute_url(self):
        return reverse("covid-record", args=[str(self.id)])

    def get_edit_url(self):
        return reverse("covid-record-edit", args=[str(self.id)])

    def view_names_url(self):
        return reverse("covid-names", args=[str(self.id)])

    def view_addresses_url(self):
        return reverse("covid-addresses", args=[str(self.id)])

    def get_add_address_url(self):
        return reverse("covid-address-add", args=[str(self.id)])

    def view_telephones_url(self):
        return reverse("covid-telephones", args=[str(self.id)])

    def get_add_telephone_url(self):
        return reverse("covid-telephone-add", args=[str(self.id)])

    def view_emails_url(self):
        return reverse("covid-emails", args=[str(self.id)])

    def get_add_email_url(self):
        return reverse("covid-email-add", args=[str(self.id)])

    def get_add_name_url(self):
        return reverse("covid-name-add", args=[str(self.id)])

    def get_add_mh_url(self):
        return reverse("covid-mh-add", args=[str(self.id)])

    def get_add_note_url(self):
        return reverse("covid-note-add", args=[str(self.id)])

    def __str__(self):
        return "Record %s - %s" % (self.id, self.name)


class Note(models.Model):
    class Meta:
        ordering = ("date_created",)

    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    note = models.TextField()
    author = models.CharField(max_length=120)
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def as_table_row(self):
        return "<tr>%s</tr>" % self.as_table_columns

    @property
    def as_table_columns(self):
        return "<td>%s<br />%s</td><td>%s</td>" % (
            formats.date_format(
                self.date_created.astimezone(), "SHORT_DATETIME_FORMAT"
            ),
            self.author,
            self.note.strip("\ ").replace("\n", "<br />"),
        )

    @property
    def author_initials(self):
        return "".join([n[0] for n in self.author.split(" ")])

    def __str__(self):
        return "Note %s for record %d - %s" % (
            self.date_created,
            self.record.id,
            self.record.name,
        )


class MedicalHistory(models.Model):
    class Meta:
        verbose_name_plural = "Medical Histories"

    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    medication_text = models.TextField(blank=True, default="")
    author = models.CharField(max_length=120)
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def _medication_set(self):
        med_set = set()
        for med in self.medication_text.split("\n"):
            if med:
                med_set.add(med.strip(" \n\r\t"))
        return sorted(med_set)

    @property
    def medication_to_html_list(self):
        return "<br />\n".join(self._medication_set)

    @property
    def medication_to_text(self):
        return "\n".join(self._medication_set)

    @property
    def details_as_table(self):
        html = ""
        html += '<tr><th class="text-right">%s :</th><td>%s</td></tr>' % (
            "Medications",
            self.medication_to_html_list,
        )
        for note in self.medicalnote_set.all():
            html += '<tr><th class="text-right">%s :</th><td>%s</td></tr>' % (
                note.readable_category,
                note.note,
            )

        return html

    def __str__(self):
        try:
            return "MedicalHistory %s for record %d - %s" % (
                self.id,
                self.record.id,
                self.record.name,
            )
        except Exception as exc:
            return "MedicalHistory %s - unbound" % self.id


class MedicalNote(models.Model):
    OTHER = 0
    WARNING = 1
    HABIT = 2
    HEART = 3
    CHEST = 4
    BLOOD = 5
    ALLERGY = 6
    CATEGORIES = [
        (OTHER, "Other Conditions"),
        (WARNING, "Warnings"),
        (HABIT, "Habits"),
        (HEART, "Heart"),
        (CHEST, "Chest"),
        (BLOOD, "Blood"),
        (ALLERGY, "Allergies"),
    ]
    _cat_dict = None

    medhist = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE)
    category = models.SmallIntegerField(choices=CATEGORIES, default=OTHER)
    note = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    @property
    def cat_dict(self):
        if self._cat_dict is None:
            self._cat_dict = {}
            for key, value in self.CATEGORIES:
                self._cat_dict[key] = value
        return self._cat_dict

    @property
    def readable_category(self):
        return self.cat_dict.get(self.category, "Other")

    def __str__(self):
        return "Medical Note (%s) for record %d - %s" % (
            self.readable_category,
            self.medhist.record.id,
            self.medhist.record.name,
        )


class Name(models.Model):
    class Meta:
        ordering = ("surname", "first_name")

    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    title = models.CharField(max_length=40, null=True, blank=True)
    first_name = models.CharField(max_length=40)
    middle_name = models.CharField(max_length=40, null=True, blank=True)
    surname = models.CharField(max_length=40)
    is_default = models.BooleanField(default=True)
    date_edited = models.DateTimeField(auto_now=True)

    def get_edit_url(self):
        return reverse("covid-name-edit", args=[str(self.id)])

    @property
    def name(self):
        try:
            return get_escaped(
                [self.title, self.first_name, self.middle_name, self.surname]
            )
        except Exception as exc:
            print(exc)
            return "error getting name"

    def __str__(self):
        return "%s - associated with record %d" % (self.name, self.record.id)


class Action(models.Model):
    """
    an action may be "call patient back", "refer to PDS", "post prescription"
    etc.
    """

    class Meta:
        ordering = ("record", "is_urgent", "is_completed", "-date_edited")

    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    action = models.CharField(max_length=240)
    is_urgent = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    date_edited = models.DateTimeField(auto_now=True)

    def get_edit_url(self):
        return reverse("covid-action-edit", args=[str(self.id)])

    def __str__(self):
        return "%sAction for record %d - %s - %s" % (
            " ".join(
                [
                    "COMPLETED" if self.is_completed else "",
                    "URGENT" if self.is_urgent else "",
                ]
            ),
            self.record.id,
            self.record.name,
            self.action,
        )


class Pharmacy(models.Model):
    class Meta:
        ordering = ("town", "name")
        verbose_name_plural = "Pharmacies"

    name = models.CharField(max_length=120)
    contractor_code = models.CharField(max_length=10, null=True, default="")
    owner = models.CharField(max_length=120, null=True, default="")
    address1 = models.CharField(max_length=120, null=True, default="")
    address2 = models.CharField(max_length=120, null=True, default="")
    address3 = models.CharField(max_length=120, null=True, default="")
    address4 = models.CharField(max_length=120, null=True, default="")
    town = models.CharField(max_length=40, null=True, default="")
    pcde = models.CharField(max_length=10, null=True, default="")
    tel = models.CharField(max_length=20, null=True, default="")
    fax = models.CharField(max_length=20, null=True, default="")
    email = models.EmailField(null=True)

    @property
    def email_link(self):
        return (
            f'<a href="mailto:{self.name}'
            f" {self.town}<{self.email}>?subject=Dental Prescription for"
            " &body=Dear Sirs%0D%0A%0D%0APlease can you dispense the attached"
            " prescription.%0D%0A%0D%0AI will forward the"
            " original.%0D%0A%0D%0AYours"
            f' Sincerely%0D%0A%0D%0A">{self.email}</a>'
        )

    @property
    def address(self):
        try:
            return get_escaped(
                [
                    self.address1,
                    self.address2,
                    self.address3,
                    self.address4,
                    self.town,
                    self.pcde,
                ],
                seperator="<br />",
            )
        except:
            return "error getting address"
        return ()

    def __str__(self):
        return f"Pharmacy {self.name} {self.address}"


class ActivityGraph(object):
    """
    a class which provides readable data about how the system has been
    accessed.
    """

    _activities = None

    def __init__(self):
        try:
            self.d1 = Note.objects.first().date_created.date()
        except AttributeError:  # no notes yet??
            self.d1 = datetime.date.today()
        try:
            self.d2 = Note.objects.last().date_created.date()
        except AttributeError:  # no notes yet??
            self.d2 = datetime.date.today()
        self.count = (self.d2 - self.d1).days + 1

    @property
    def activities(self):
        if self._activities is None:
            self._activities = {}
            with connection.cursor() as cursor:
                cursor.execute(ACTIVITY_QUERY)
                for date_, count in cursor.fetchall():
                    # query returns string object with sqlite
                    try:
                        key = datetime.date.fromisoformat(date_)
                    except TypeError:
                        key = date_
                    self._activities[key] = count

        return self._activities

    def dates(self):
        for i in range(self.count):
            yield self.d1 + datetime.timedelta(days=i)

    def date_range(self):
        for d in self.dates():
            yield d.strftime("%s %%d/%%m" % WEEKDAYS[d.weekday()])

    def activity_counts(self):
        for d in self.dates():
            yield ([self.activities.get(d, 0)])

    def as_table(self):
        counts = [c[0] for c in self.activity_counts()]
        html = "<thead><tr><th>Date</th><th>Activities</th></tr></thead>"
        html += "<tbody>"
        for i, d in enumerate(self.date_range()):
            cell = f"{counts[i]} contacts" if counts[i] else "-"
            html += f"<tr><td>{d}</td><td>{cell}</td></tr>"
        html += "</tbody>"
        return html


def get_escaped(iterable, seperator=" "):
    return seperator.join([escape(x) for x in iterable if x])
