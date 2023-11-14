from typing import Optional

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    SelectField,
    SelectMultipleField,
    StringField,
    validators,
    widgets,
)
from wtforms.widgets import HiddenInput


class EditionForm(FlaskForm):
    edition = SelectField(label="Édition de votre export")


class ArticleForm(FlaskForm):
    name = StringField(
        "Nom de votre export",
        validators=[
            validators.InputRequired(message="Veuillez saisir un nom."),
        ],
    )
    kind = SelectField(
        label="Type d’export",
        choices=[
            ("article", "Article unique"),
        ],
        validators=[
            validators.InputRequired(message="Il est nécessaire de choisir un type.")
        ],
    )
    domain = SelectField(
        label="Domaine de votre article",
        validators=[
            validators.InputRequired(message="Il est nécessaire de choisir le domaine.")
        ],
    )
    article_id = StringField(
        "ID de votre article",
        validators=[
            validators.InputRequired(message="Il est nécessaire de soumettre un ID.")
        ],
    )
    with_toc = BooleanField("Avec une Table des Matières (TOC)")
    with_ascii = BooleanField("Avec une conversion des caractères spéciaux (ASCII)")

    def filter_name(self, field: str) -> Optional[str]:
        if not field:
            return None
        return field.strip()

    def filter_article_id(self, field: str) -> Optional[str]:
        if not field:
            return None
        return field.strip()


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.

    From:
    https://wtforms.readthedocs.io/en/3.0.x/specific_problems/#specialty-field-tricks
    """

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ExportForm(FlaskForm):
    with_toc = BooleanField(
        widget=HiddenInput(), false_values=(False, "false", "", "0")
    )
    with_ascii = BooleanField(
        widget=HiddenInput(), false_values=(False, "false", "", "0")
    )
    version = SelectField(label="Version de votre article")


class ExportGeneriqueForm(ExportForm):
    bibliography_style = SelectField(label="Feuille de styles bibliographiques")
    formats = MultiCheckboxField(label="Formats inclus dans votre archive")

    class Meta:
        csrf = False


class ExportRevueForm(ExportForm):
    formats = SelectField(label="Format de votre export")

    class Meta:
        csrf = False
