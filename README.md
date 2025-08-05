## Description

Analyseur de texte français complet qui extrait les valeurs numériques et pourcentages à partir de texte en français naturel. Gère les fractions, négatif, ordinaux, nombres écrits en lettres, et variations linguistiques courantes incluant les formes belges/suisses.

## Fonctionnalités

### ✅ Reconnaissance de Nombres
- **Chiffres** : `12`, `1234`, `99.9`
- **Nombres écrits** : `douze`, `mille deux cent trente-quatre`, `quatre-vingt-dix-neuf`
- **Grands nombres** : `millions`, `milliards`, `billions`
- **Variantes régionales** : `septante` (70), `huitante`/`octante` (80), `nonante` (90)

### ✅ Gestion des Pourcentages
- **Pourcentages directs** : `50%`, `quatre-vingt-dix pour cent`
- **Fractions en pourcentages** : `1/2` → `50%`, `trois quarts` → `75%`
- **Nombres ordinaux** : `un cinquième` → `20%`, `trois dixièmes` → `30%`

### ✅ Expressions Spéciales
- **Expressions de zéro** : `aucun`, `rien`, `personne` → `0%`
- **Totalité** : `tout`, `tous`, `totalité` → `100%`
- **Approximations** : `presque tout` → `95%`, `quasi rien` → `5%`

### ✅ Gestion d'Erreurs Robuste
- **Fautes de frappe** : `quatr` → `quatre`, `cinqante` → `cinquante`
- **Accents manquants** : `moitie` → `moitié`
- **Formes plurielles** : `quarts`, `tiers`, `cinquièmes`

## ✅ Nombres négatifs
- "moins 10" → "-10"
- "moins mille deux cent quatre-vingt-quatorze pour cent" → "-1294%"

## Utilisation

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

...

```

## Résultats des Tests

Le parseur comprend **plus de 350 cas de test** couvrant :
- Nombres de base (0-999)
- Grands nombres (milliers, millions, milliards)
- Tous les types de fractions (demi, tiers, quart, cinquième, etc.)
- Expressions de pourcentage
- Variantes régionales du français
- Fautes de frappe et variations courantes
- Phrases contextuelles complexes
- Expressions négatives

## Examples / Exemples

| Entrée               | Sortie        | Type               |
|--------------------------------|---------------|--------------------|
| `"aucun"`                      | `"0%"`        | Expression zéro    |
| `"la moitié"`                  | `"50%"`       | Fraction           |
| `"trois quarts"`               | `"75%"`       | Fraction           |
| `"85 / 100"`                   | `"85%"`       | Fraction numérique |
| `"nonante-deux"`               | `"92"`        | Variante régionale |
| `"presque tout"`               | `"95%"`       | Approximation      |
| `"mille deux cent"`            | `"1200"`      | Grand nombre       |
| `"un cinquième"`               | `"20%"`       | Ordinal            |
| `"moins cent quatre-vingt dix %"`| `"-190%"`     | Pourcentage négatif|
| `"trente pourcent"`| `"30%"`     | Pourcentage|
| `"moins trois cent"`           | `"-300"`      | Texte négatif      |
| `"moins trois quarts"`         | `"-75%"`      | Fraction négative  |
| `"nous sommes mardi"`           | `"aucun chiffre"` | Pas de chiffre  |
