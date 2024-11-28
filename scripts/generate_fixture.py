import itertools
import json
import random
import datetime
from pathlib import Path


FIRST_NAMES = (
    "Anna",
    "Bengt",
    "Cecilia",
    "David",
    "Ella",
    "Farokh",
    "Gunilla",
    "Hans",
    "Inga",
    "Johan",
    "Karin",
    "Ludvid",
    "Malin",
    "Nils",
    "Ofelia",
    "Patrik",
    "Rebecka",
    "Sten",
    "Tara",
    "Urban",
    "Viveka",
    "William",
    "Zara",
    "Åke",
    "Ärna",
    "Örjan",
)

LAST_NAMES = (
    "Andersson",
    "Bankler",
    "Carlsson",
    "Duva",
    "Erlander",
    "Forsberg",
    "Grip",
    "Hansson",
    "Ingesson",
    "Johansson",
    "Karlsson",
    "Lindahl",
    "Magnusson",
    "Nilsson",
    "Oskarsson",
    "Petersson",
    "Runkvist",
    "Svensson",
    "Tillberg",
    "Unosson",
    "Vidén",
    "Wahlberg",
    "Yngvesson",
    "Åkesson",
    "Östensson",
)

PRODUCTION_NAME_COMPONENTS = [
    "apor",
    "bovar",
    "cirkus",
    "drama",
    "elände",
    "fasor",
    "galenskap",
    "hemskheter",
    "intriger",
    "jubelidioter",
    "korv",
    "lögner",
    "mord",
    "nördar",
    "otur",
    "pangpang",
    "rajtantajtan",
    "sjörövare",
    "tavlor",
    "ufon",
    "vintunnor",
    "yxor",
    "ångest",
    "älskare",
    "ölbulteljer",
]

GROUP_TYPES = ("Skådis", "Orkestern", "Dekor", "KSP", "Ledningen", "Manus")
ASSOCIATION_GROUP_TYPES = ("Styrelsen", "Revisorer", "Valberedning")


def _base_model(model, **fields):
    return {
        "model": f"batadasen.{model}",
        "fields": fields,
    }


def create_person(member_number, first_name, last_name):
    return _base_model(
        "Person",
        member_number=member_number,
        first_name=first_name,
        last_name=last_name,
        email=f"{first_name.lower()}@{last_name.lower()}.se",
    )


def create_spex(number, year, main_title):
    return _base_model(
        "Production",
        number=number,
        year=year,
        main_title=main_title,
        short_name=f"Spex-{str(year)[-2:]}",
    )


def create_production_group_type(name: str):
    return _base_model("ProductionGroupType", name=name, short_name=name[:3].upper())


def create_production_group(id, production, group):
    return _base_model(
        "ProductionGroup", id=id, production=production, group_type=group
    )


def create_production_membership(id, person, group):
    return _base_model("ProductionMembership", id=id, person=person, group=group)


def create_association_year(end_year):
    return _base_model("AssociationYear", end_year=end_year)


def create_association_group_type(name):
    return _base_model("AssociationGroupType", name=name, short_name=name[:3].upper())


def create_association_group(id, year, group):
    return _base_model("AssociationGroup", id=id, year=year, group_type=group)


def create_association_membership(id, person, group):
    return _base_model("AssociationActivity", id=id, person=person, group=group)


def main(number_of_members, number_of_years):
    unique_names = set()
    while len(unique_names) < number_of_members:
        unique_names.add((random.choice(FIRST_NAMES), random.choice(LAST_NAMES)))

    persons = []
    for n, (first_name, last_name) in enumerate(unique_names, start=1):
        person = create_person(n, first_name, last_name)
        persons.append(person)

    end_year = datetime.datetime.now().year + 2
    start_year = end_year - number_of_years
    years = range(start_year, end_year)

    ##############  Uppsättningar  ##############

    productions = []
    for n, year in enumerate(years, start=1):
        a, b = random.choices(PRODUCTION_NAME_COMPONENTS, k=2)
        production = create_spex(n, year, f"{a} och {b}".capitalize())
        productions.append(production)

    production_group_types = [
        create_production_group_type(group_name) for group_name in GROUP_TYPES
    ]

    production_groups = [
        create_production_group(
            n, production["fields"]["number"], group["fields"]["short_name"]
        )
        for n, (production, group) in enumerate(
            itertools.product(productions, production_group_types)
        )
    ]

    production_memberships = []
    for group in production_groups:
        for person in random.choices(persons, k=random.randint(5, 10)):
            production_memberships.append(
                create_production_membership(
                    len(production_memberships) + 1,
                    person["fields"]["member_number"],
                    group["fields"]["id"],
                )
            )

    ##############  Verksamhetsår  ##############

    association_years = [create_association_year(year) for year in years]
    association_group_types = [
        create_association_group_type(group_name)
        for group_name in ASSOCIATION_GROUP_TYPES
    ]

    association_groups = [
        create_association_group(
            n, year["fields"]["end_year"], group["fields"]["short_name"]
        )
        for n, (year, group) in enumerate(
            itertools.product(association_years, association_group_types)
        )
    ]

    association_memberships = []
    for group in association_groups:
        for person in random.choices(persons, k=5):
            association_memberships.append(
                create_association_membership(
                    len(association_memberships) + 1,
                    person["fields"]["member_number"],
                    group["fields"]["id"],
                )
            )

    ##########  Generera fixture.json  ##########

    output = Path("fixture.json")
    output.write_text(
        json.dumps(
            persons
            + productions
            + production_group_types
            + production_groups
            + production_memberships
            + association_years
            + association_group_types
            + association_groups
            + association_memberships,
            indent=4,
        )
    )


if __name__ == "__main__":
    main(number_of_members=200, number_of_years=5)
