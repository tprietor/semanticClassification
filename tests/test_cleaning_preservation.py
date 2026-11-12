from src.services.cleaning import CleaningService


def test_cleaning_preserves_english_paragraphs_and_removes_end_matter():
    markdown = """# Agroforestry Systems

Agroforestry systems combine crops and trees in the same field.

Farmers maintain these systems to produce food throughout the year.

These practices also help communities care for the soil and retain useful trees.

**Author Contributions:** The authors wrote this article.

## **References**

Smith, J. Agroforestry and food systems. 2020.
"""

    cleaned = CleaningService.structuralCleaning(markdown)

    assert "Agroforestry systems combine crops and trees" in cleaned
    assert "Farmers maintain these systems" in cleaned
    assert "field.\n\nFarmers" in cleaned
    assert "Author Contributions" not in cleaned
    assert "Smith, J." not in cleaned


def test_cleaning_cuts_only_at_bibliography_heading():
    markdown = """# Sistemas agroforestales

La bibliografía sobre el cultivo describe prácticas de conservación.

Las familias producen alimentos en sus parcelas agroforestales.

## Bibliografía

Pérez, A. Cultivo y conservación. 2020.
"""

    cleaned = CleaningService.structuralCleaning(markdown)

    assert "La bibliografía sobre el cultivo" in cleaned
    assert "Las familias producen alimentos" in cleaned
    assert "Pérez, A." not in cleaned


def test_cleaning_recognizes_plain_reference_heading():
    markdown = """A paragraph about forest management and local farming practices.

References

Smith, J. Forest management in the region. 2020.
"""

    cleaned = CleaningService.structuralCleaning(markdown)

    assert "forest management and local farming" in cleaned
    assert "Smith, J." not in cleaned


def test_cleaning_cuts_funding_section_before_references():
    markdown = """Farmers manage agroforestry systems to produce food.

They also maintain native trees and monitor changes in the soil across seasons.

###### Funding

Grant information for this research.

###### References

Smith, J. Agroforestry systems. 2020.
"""

    cleaned = CleaningService.structuralCleaning(markdown)

    assert "Farmers manage agroforestry systems" in cleaned
    assert "monitor changes in the soil" in cleaned
    assert "Grant information" not in cleaned


def test_cleaning_keeps_body_after_early_acknowledgments():
    markdown = """# Reporte territorial

## Agradecimientos

Agradecemos a las familias que participaron en el informe.

## Resultados

Las familias cultivan cacao y conservan árboles en sus parcelas.

Los sistemas agroforestales producen alimentos durante todo el año.
"""

    cleaned = CleaningService.structuralCleaning(markdown)

    assert "Las familias cultivan cacao" in cleaned
    assert "Los sistemas agroforestales producen alimentos" in cleaned


def test_cleaning_uses_last_bibliography_in_multichapter_book():
    markdown = """# Capítulo uno

Las comunidades manejan sus bosques y huertos agroforestales.

## Bibliografía

Referencia del primer capítulo.

# Capítulo dos

Las familias siembran cacao y mantienen árboles de sombra.

## Bibliografía

Referencia del segundo capítulo.
"""

    cleaned = CleaningService.structuralCleaning(markdown)

    assert "Las familias siembran cacao" in cleaned
    assert "Referencia del primer capítulo" not in cleaned
    assert "Referencia del segundo capítulo" not in cleaned


def test_cleaning_recognizes_numbered_and_consulted_bibliographies():
    markdown = """# Sistemas agroforestales

Las comunidades cultivan cacao bajo árboles de sombra.

**10. Referencias bibliográficas**

Pérez, A. Cacao y árboles. 2020.
"""

    cleaned = CleaningService.structuralCleaning(markdown)

    assert "Las comunidades cultivan cacao" in cleaned
    assert "Pérez, A." not in cleaned

    consulted = """La comunidad conserva su bosque y produce alimentos.

## **BIBLIOGRAFÍA CONSULTADA**

Pérez, A. Bosques. 2020.
"""

    assert "Pérez, A." not in CleaningService.structuralCleaning(consulted)


def test_cleaning_recognizes_bibliography_variants_from_converted_documents():
    for heading in (
        "#### G. Bibliografía",
        "##### **VIII. Referencias bibliográficas**",
        "6. **Bibliografía Citada**",
        "# **Referencias biblográficas**",
    ):
        markdown = (
            "# Informe\n\nLas familias cultivan cacao y conservan árboles.\n\n"
            f"{heading}\n\nPérez, A. Libro sobre cacao. 2020.\n"
        )
        cleaned = CleaningService.structuralCleaning(markdown)
        assert "Las familias cultivan cacao" in cleaned
        assert "Pérez, A." not in cleaned


def test_cleaning_keeps_substantive_table_cells():
    markdown = """# Monitoreo agroforestal

| Actividad | Resultado |
| --- | --- |
| Capacitación agroforestal | Participaron quince jóvenes de la comunidad |
"""
    cleaned = CleaningService.structuralCleaning(markdown)
    assert "Capacitación agroforestal" in cleaned
    assert "Participaron quince jóvenes" in cleaned
    assert "---" not in cleaned


def test_cleaning_restores_annex_after_bibliography_despite_heading_level():
    markdown = """# Estudio agroforestal

Las familias combinan cacao y árboles en sus parcelas.

### Referencias bibliográficas

Pérez, A. Cultivo de cacao. 2020.

##### Anexo 1: costos e ingresos de SAF

El anexo registra ingresos de las familias productoras.

### Anexo 4, bibliográfico: bases de datos

García, B. Catálogo de especies. 2021.
"""
    cleaned = CleaningService.structuralCleaning(markdown)
    assert "El anexo registra ingresos" in cleaned
    assert "Pérez, A." not in cleaned
    assert "García, B." not in cleaned


def test_cleaning_restores_next_book_chapter_after_bibliography():
    markdown = """#### Capítulo 1

Las familias manejan huertos agroforestales.

#### Bibliografía

Pérez, A. Manual de huertos. 2020.

###### Capítulo 2

Las familias mantienen árboles de sombra.
"""
    cleaned = CleaningService.structuralCleaning(markdown)
    assert "Las familias mantienen árboles de sombra" in cleaned
    assert "Pérez, A." not in cleaned


def test_cleaning_removes_singular_agradecimiento_section():
    markdown = """### Conclusiones

Los productores mantienen árboles de sombra en sus fincas.

### Agradecimiento

Agradecemos a la entidad financiadora por su apoyo.

### Referencias

Pérez, A. Sistemas agroforestales. 2020.
"""
    cleaned = CleaningService.structuralCleaning(markdown)
    assert "Los productores mantienen árboles" in cleaned
    assert "entidad financiadora" not in cleaned
    assert "Pérez, A." not in cleaned


def test_cleaning_keeps_abstract_with_institution_words_and_sample_size():
    markdown = """# Caracterización de fincas

Se aplicó una entrevista estructurada a 183 ganaderos del departamento de Madre de Dios, y el grupo de investigación analizó los resultados para describir las diferencias entre distritos y sistemas productivos de las fincas.
"""
    cleaned = CleaningService.structuralCleaning(markdown)
    assert "183 ganaderos" in cleaned
    assert "grupo de investigación" in cleaned
