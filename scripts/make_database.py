#! /usr/bin/env python

"""
This python script populates the database with demo records.
In true CS50 tradition, we are using characters from 
Harry Potter novels.
"""
import os
import datetime
import random
import re
import sys
import django


# change working directory to the website directory so that django is configured
# correctly
if __file__ == "<stdin>":  # this is the case when running from vim
    SCRIPT_PATH = "/home/neil/prog/CS50/project/scripts/make_database.py"
else:
    SCRIPT_PATH = os.path.abspath(__file__)
SCRIPTS_DIR = os.path.dirname(SCRIPT_PATH)
PROJECT_PATH = os.path.dirname(SCRIPTS_DIR)
print(PROJECT_PATH)
WEBSITE_PATH = os.path.join(PROJECT_PATH, "website")
DATA_FILE = os.path.join(PROJECT_PATH, "resources", "demo_patients.txt")

SETTINGS_MODULE = "cs50.settings"


def setup_django_environment():
    """
    this is similar to wsgi.py or "python manag.py shell"
    it initialises the django environment for this website
    and ensure application import will work
    """
    os.chdir(WEBSITE_PATH)
    sys.path.append(WEBSITE_PATH)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    django.setup()


def create_guest_user():
    """
    create our user for the site.
    """
    from django.contrib.auth.models import User

    try:
        user = User.objects.create_user("Guest", "guest@guest.com", "Guest")
    except Exception as exc:
        print("guest user already exists?")
        print(exc)


def random_date():
    """
    return a random date for a date of birth
    """
    return datetime.date(
        random.randint(1900, 2005),
        random.randint(1, 12),
        random.randint(1, 28),
    )


def random_note_date(earliest=datetime.date(2020, 4, 1)):
    """
    return a random date within a sensible range for the application usage
    """
    d = datetime.date(2020, 1, 1)
    while d < earliest:
        d = datetime.date(
            2020,
            random.randint(4, 12),
            random.randint(1, 28),
        )
    return datetime.datetime(
        d.year,
        d.month,
        d.day,
        random.randint(9, 18),
        random.randint(0, 59),
    )


def random_dentist():
    """
    return a random date
    """
    return random.choice(
        [
            "Neil Wallace (Inshes)",
            "John Smith (Culloden)",
            "Carole Peters (Torwood)",
            "Susan Harding (Diabolo)",
            "Ken Portillo (Eden)",
        ]
    )


def random_phoneno():
    """
    return a random phonenumber
    """
    number = ""
    for i in range(10):
        number += str(random.randint(0, 9))
    return f"+44 (0){number}"


def random_note():
    return random.choice(
        [
            (
                "Patient has lost a filling. No pain. \nUnderstands we are "
                "currently operating a reduced service.\n\nPatient to contact "
                "their own practice when quarantine is over"
            ),
            ("Broken Denture.\nDetails of emergency postal lab given."),
            (
                "Terrible pain and swelling since yesterday\n"
                "Prescription given for Amoxicillin 500mg tds for 5 days."
            ),
            (
                "Pt made contact through website. "
                "All practices are closed due to Covid-19).\n"
                "Pt reports had pain last Thursday UL back which has now gone.\n"
                "Gum was red. \n\n"
                "Not taking regular pain relief and not interrupting sleep. \n"
                "No swelling. No broken teeth or filling out. No trauma.\n\n"
            ),
        ]
    )


def random_action():
    return random.choice(
        ["phone patient back", "consult with pt's GP", "Refer to Hospital"]
    )


def create_records():
    from covid.models import (
        Name,
        Record,
        Address,
        Note,
        Telephone,
        Email,
        Action,
    )

    with open(DATA_FILE) as f:
        for line_ in f:
            title, fname, sname = line_.split(" ")
            if title.startswith("#"):
                continue
            record_obj = Record.objects.create(
                dob=random_date(),
                dentist=random_dentist(),
            )
            record_obj.date_created = random_note_date()
            record_obj.save()
            Name.objects.create(
                record=record_obj,
                title=title.title(),
                first_name=fname.title(),
                surname=sname.title(),
            )
            address_obj = Address.objects.create(
                addr1="Hogwarts School of Wizardry",
                town="Hogsmeade",
                postcode="W1Z ARD",
            )
            tel_obj = Telephone.objects.create(
                number=random_phoneno(),
            )
            email_obj = Email.objects.create(
                email=f"{fname.lower()}.{sname.lower()}@hogwarts.com"
            )
            record_obj.addresses.add(address_obj)
            record_obj.telephones.add(tel_obj)
            record_obj.emails.add(email_obj)
            Action.objects.create(
                record=record_obj,
                action=random_action(),
                is_urgent=random.choice([True, False, False, False]),
                is_completed=random.choice([True, False, True, True]),
            )
            for i in range(random.randint(1, 6)):
                # for author - remove practice from dentist name
                author = re.match(r"\w+ \w+", random_dentist()).group()

                note_obj = Note.objects.create(
                    record=record_obj, author=author, note=random_note()
                )
                note_obj.date_created = random_note_date(
                    record_obj.date_created.date()
                )
                note_obj.save()


if __name__ == "__main__":
    setup_django_environment()
    create_guest_user()
    create_records()
