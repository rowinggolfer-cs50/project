from django.urls import path, re_path

from covid import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="covid-homepage"),
    path("patients/", views.PatientsView.as_view(), name="covid-patients"),
    path(
        "recent-notes/",
        views.RecentNotesView.as_view(),
        name="covid-recent-notes",
    ),
    path("records/", views.RecordListView.as_view(), name="covid-records"),
    path(
        "duplicates/<int:year>/<int:month>/<int:day>/" "<slug:sname>/<slug:fname>/",
        views.DuplicatesView.as_view(),
        name="covid-duplicates",
    ),
    path("record/add/", views.NewRecordView.as_view(), name="covid-new-record"),
    path("search", views.SearchView.as_view(), name="covid-search"),
    path(
        "search-result/<int:year>/<int:month>/<int:day>/<slug:sname>/<slug:fname>/",
        views.SearchResultView.as_view(),
        name="covid-search-result",
    ),
    path(
        "record/edit/<int:pk>/",
        views.EditRecordView.as_view(),
        name="covid-record-edit",
    ),
    path(
        "record/<int:pk>/",
        views.RecordView.as_view(),
        name="covid-record",
    ),
    path(
        "record/names/<int:pk>/",
        views.NamesView.as_view(),
        name="covid-names",
    ),
    path(
        "record/names/edit/<int:pk>/",
        views.NameEditView.as_view(),
        name="covid-name-edit",
    ),
    path(
        "record/names/add/<int:pk>/",
        views.NameAddView.as_view(),
        name="covid-name-add",
    ),
    path(
        "record/address/<int:pk>/",
        views.AddressView.as_view(),
        name="covid-addresses",
    ),
    path(
        "record/address/edit/<int:pk>/",
        views.AddressEditView.as_view(),
        name="covid-address-edit",
    ),
    path(
        "record/address/delete/<int:pk>/",
        views.AddressDeleteView.as_view(),
        name="covid-address-delete",
    ),
    path(
        "record/address/add/<int:pk>/",
        views.AddressAddView.as_view(),
        name="covid-address-add",
    ),
    path(
        "record/telephone/<int:pk>/",
        views.TelephoneView.as_view(),
        name="covid-telephones",
    ),
    path(
        "record/telephone/edit/<int:pk>/",
        views.TelephoneEditView.as_view(),
        name="covid-telephone-edit",
    ),
    path(
        "record/telephone/delete/<int:pk>/",
        views.TelephoneDeleteView.as_view(),
        name="covid-telephone-delete",
    ),
    path(
        "record/telephone/add/<int:pk>/",
        views.TelephoneAddView.as_view(),
        name="covid-telephone-add",
    ),
    path(
        "record/email/<int:pk>/",
        views.EmailView.as_view(),
        name="covid-emails",
    ),
    path(
        "record/email/edit/<int:pk>/",
        views.EmailEditView.as_view(),
        name="covid-email-edit",
    ),
    path(
        "record/email/add/<int:pk>/",
        views.EmailAddView.as_view(),
        name="covid-email-add",
    ),
    path(
        "actions",
        views.AllActionsView.as_view(),
        name="covid-view-actions",
    ),
    path(
        "record/actions/view-all/<int:pk>/",
        views.ActionsView.as_view(),
        name="covid-view-all-actions",
    ),
    path(
        "record/action/edit/<int:pk>/",
        views.ActionEditView.as_view(),
        name="covid-action-edit",
    ),
    path(
        "record/action/add/<int:pk>/",
        views.ActionAddView.as_view(),
        name="covid-action-add",
    ),
    path(
        "record/mh/add/<int:pk>/",
        views.MedHistAddView.as_view(),
        name="covid-mh-add",
    ),
    path(
        "record/mh/view-all/<int:pk>/",
        views.MedHistsView.as_view(),
        name="covid-view-all-medhists",
    ),
    path(
        "record/mh/edit/<int:pk>/",
        views.MedHistEditView.as_view(),
        name="covid-mh-edit",
    ),
    path(
        "record/note/add/<int:pk>/",
        views.NoteAddView.as_view(),
        name="covid-note-add",
    ),
    re_path(
        "pharmacy",
        views.PharmacyView.as_view(),
        name="pharmacy",
    ),
    path("help", views.HelpView.as_view(), name="covid-help"),
    path(
        "read-permission/help",
        views.ReadPermmissionHelpView.as_view(),
        name="covid-read-permission-help",
    ),
    path(
        "write-permission/help",
        views.WritePermmissionHelpView.as_view(),
        name="covid-write-permission-help",
    ),
    path(
        "activity",
        views.ActivityView.as_view(),
        name="covid-activity",
    ),
]
