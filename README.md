# French Text to number or percentages / Analyseur de Texte Français vers nombres ou pourcentages

## Description

**English:** A comprehensive French text parser that extracts numerical values and percentages from French natural language input. Handles fractions, ordinals, spelled-out numbers, and common language variations including Belgian/Swiss French forms.

**Français:** Un analyseur de texte français complet qui extrait les valeurs numériques et pourcentages à partir de texte en français naturel. Gère les fractions, négatif, ordinaux, nombres écrits en lettres, et variations linguistiques courantes incluant les formes belges/suisses.

## Features / Fonctionnalités

### ✅ Number Recognition / Reconnaissance de Nombres
- **Digits**: `12`, `1234`, `99.9`
- **Written numbers**: `douze`, `mille deux cent trente quatre`, `quatre-vingt-dix-neuf`
- **Large numbers**: `millions`, `milliards`, `billions`
- **Regional variants**: `septante` (70), `huitante`/`octante` (80), `nonante` (90)

### ✅ Percentage Handling / Gestion des Pourcentages
- **Direct percentages**: `50%`, `quatre-vingt-dix pour cent`
- **Fractions as percentages**: `1/2` → `50%`, `trois quarts` → `75%`
- **Ordinals**: `un cinquième` → `20%`, `trois dixièmes` → `30%`

### ✅ Special Expressions / Expressions Spéciales
- **Zero expressions**: `aucun`, `rien`, `personne` → `0%`
- **Totality**: `tout`, `tous`, `totalité` → `100%`
- **Approximations**: `presque tout` → `95%`, `quasi rien` → `5%`

### ✅ Robust Error Handling / Gestion d'Erreurs Robuste
- **Typos**: `quatr` → `quatre`, `cinqante` → `cinquante`
- **Missing accents**: `moitie` → `moitié`
- **Plural forms**: `quarts`, `tiers`, `cinquièmes`

## ✅ Negative number / Nombre négatif
- "moins 10" → "-10"
- "moins mille deux centre quatre vingt quatorze pourcent" → "-1294%"

```python
from number_extract import *

# Basic numbers / Nombres de base
print(text_to_understanding("vingt-trois"))  # "23"
print(text_to_understanding("mille deux cent"))  # "1200"

# Percentages / Pourcentages
print(text_to_understanding("cinquante pourcent"))  # "50%"
print(text_to_understanding("trois quarts"))  # "75%"
print(text_to_understanding("1/4"))  # "25%"

# Complex expressions / Expressions complexes
print(text_to_understanding("j'en ai bu les trois quarts"))  # "75%"
print(text_to_understanding("presque la totalité"))  # "95%"
print(text_to_understanding("environ un tiers"))  # "33%"

# Regional variants / Variantes régionales
print(text_to_understanding("nonante-deux"))  # "92"
print(text_to_understanding("septante-quatre"))  # "74"
```

## Test Results / Résultats des Tests

The parser includes **350+ test cases** covering:
- Basic numbers (0-999)
- Large numbers (thousands, millions, billions)
- All fraction types (halves, thirds, quarters, fifths, etc.)
- Percentage expressions
- Regional French variants
- Common typos and variations
- Complex contextual phrases
- Negative phrases

## Examples / Exemples

| Input (French)                  | Output        | Type             |
|--------------------------------|---------------|------------------|
| `"aucun"`                      | `"0%"`        | Zero expression  |
| `"la moitié"`                  | `"50%"`       | Fraction         |
| `"trois quarts"`               | `"75%"`       | Fraction         |
| `"85 / 100"`                   | `"85%"`       | Numeric fraction |
| `"nonante-deux"`               | `"92"`        | Regional variant |
| `"presque tout"`               | `"95%"`       | Approximation    |
| `"mille deux cent"`            | `"1200"`      | Large number     |
| `"un cinquième"`               | `"20%"`       | Ordinal          |
| `"moins cent quatre-vingt dix"`| `"-190%"`     | Negative percent |
| `"moins trois cent"`           | `"-300"`      | Negative text    |
| `"moins trois quarts"`         | `"-75%"`      | Negative fraction|
| `"nous sommes mardi"`           | `"aucun chiffre"` | No digits    |
