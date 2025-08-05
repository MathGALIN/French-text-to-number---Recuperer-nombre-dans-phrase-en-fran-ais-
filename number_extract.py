import re
from typing import Optional, List, Dict, Tuple

import re

def text_to_understanding(input_text: str) -> str:
    """
    Fonction principale qui convertit un texte français en pourcentage ou nombre.

    Args:
        input_text (str): Le texte d'entrée à analyser

    Returns:
        str: Le résultat sous forme de pourcentage (ex: "75%") ou nombre,
             ou "AUCUN CHIFFRE" si aucun nombre n'est détecté

    Exemples:
        - "trois sur quatre" -> "75%"
        - "50 pourcent" -> "50%"
        - "vingt-trois" -> "23"
        - "aucun" -> "0%"
        - "il n y a aucun chiffre" -> "AUCUN CHIFFRE"
        - "moins quatre" -> "-4"
        - " -5" -> "-5"
        - "-400%" -> "-400%"
    """

    # Détection du signe négatif dans le texte original (avant normalisation)
    input_text_lower = input_text.lower()
    is_negative = False

    # Cas 1 : "moins" sans "de"
    if re.search(r'\bmoins\b(?!\s+de)', input_text_lower):
        is_negative = True
        
    #Mais si il y a moins "moins deu" alors on remet en positif
    if "moins deu" in input_text.lower() :
        is_negative = True

    # Cas 2 : "-" ou "_" suivi d’un chiffre
    if re.search(r'(?<!\w)[-_]\s*\d+', input_text):
        is_negative = True

    # Texte normalisé pour traitement
    normalized_text = normalize_text(input_text)

    # Liste des indicateurs de pourcentage
    percentage_indicators = [
        "pourcent", "%", "prcent", "prcnt", "pour cent", "pour cents",
        "demi", "moitie", "tiers", "tier", "quart", "quarts",
        "totalite", "quasi", "tout", "tous", "aucun", "rien", "presque",
        "sur", " / "
    ]

    # Détection des fractions numériques (ex: 3/4)
    fraction_numeric_match = re.search(r'(\d+)\s*/\s*(\d+)', normalized_text)
    if fraction_numeric_match:
        numerator = int(fraction_numeric_match.group(1))
        denominator = int(fraction_numeric_match.group(2))
        if denominator != 0:
            percentage_value = (numerator / denominator) * 100
            if is_negative:
                percentage_value *= -1
            return f"{round(percentage_value)}%"

    # Détection des fractions textuelles (ex: trois sur quatre)
    fraction_sur_match = re.search(r'(\S+)\s+sur\s+(\S+)', normalized_text)
    if fraction_sur_match:
        numerator_text = fraction_sur_match.group(1)
        denominator_text = fraction_sur_match.group(2)

        numerator_value = text_to_number(numerator_text)
        denominator_value = text_to_number(denominator_text)

        if numerator_value is not None and denominator_value not in (None, 0):
            percentage_value = (numerator_value / denominator_value) * 100
            if is_negative:
                percentage_value *= -1
            return f"{round(percentage_value)}%"

    # Détection des ordinaux (ex: cinquième -> 5%)
    if re.search(r'(?:ieme|iemes|ième|ièmes)', normalized_text):
        ordinal_number = text_to_number(normalized_text)
        if ordinal_number is not None:
            if is_negative:
                ordinal_number *= -1
            return f"{ordinal_number}%"

    # Extraction du nombre principal
    extracted_number = text_to_number(normalized_text)

    # Vérification des indicateurs de pourcentage
    for indicator in percentage_indicators:
        if indicator == "%" and "%" in normalized_text:
            if extracted_number is not None:
                if is_negative:
                    extracted_number *= -1
                return f"{extracted_number}%"
        elif indicator != "%" and re.search(r'\b' + re.escape(indicator) + r'\b', normalized_text):
            if extracted_number is not None:
                if is_negative:
                    extracted_number *= -1
                return f"{extracted_number}%"
            # Cas spéciaux pour les expressions absolues
            if indicator in ["totalite", "tout", "tous"]:
                return "100%"
            elif indicator in ["aucun", "rien"]:
                return "0%"

    # Retour du nombre s'il est trouvé
    if extracted_number is not None:
        if is_negative:
            extracted_number *= -1
        return str(extracted_number)

    # Aucun chiffre détecté
    return "AUCUN CHIFFRE"




def normalize_text(input_text: str) -> str:
    """
    Normalise le texte pour faciliter l'analyse numérique.

    Opérations effectuées :
    - Conversion en minuscules
    - Suppression des accents
    - Remplacement des tirets et underscores par des espaces et . a la fin annuler
    - Suppression du mot 'et'
    - Conversion des nombres français complexes en formes belges/suisses simplifiées
    - Correction des fautes d'orthographe courantes
    - Nettoyage des espaces multiples
    - Si on voit le mot virgule(s) ou point(s) on enlève la suite de la chaîne (ex: "quatre virgule cinq" devient "quatre")

    Args:
        input_text (str): Le texte à normaliser

    Returns:
        str: Le texte normalisé
    """
    # 1. Conversion en minuscules et remplacement des séparateurs
    normalized = input_text.lower()
    normalized = normalized.replace('-', ' ').replace('_', ' ')
    

    if normalized[-1] == '.':
        normalized = normalized[:-1]

    # 2. Suppression du mot "et"
    normalized = re.sub(r'\bet\b', '', normalized)

    # 3. Suppression des accents français
    accent_mapping = str.maketrans({
        'à': 'a', 'â': 'a', 'ä': 'a', 'á': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'î': 'i', 'ï': 'i', 'í': 'i',
        'ô': 'o', 'ö': 'o', 'ó': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u', 'ú': 'u',
        'ÿ': 'y', 'ý': 'y',
        'ç': 'c'
    })
    normalized = normalized.translate(accent_mapping)

    # 4. Conversion des nombres français complexes en formes simplifiées
    french_to_simple_patterns = [
        # soixante-dix → septante
        (r'\bsoixante\s*dix\s*neuf\b', 'septante neuf'),
        (r'\bsoixante\s*dix\s*huit\b', 'septante huit'),
        (r'\bsoixante\s*dix\s*sept\b', 'septante sept'),
        (r'\bsoixante\s*dix\s*six\b', 'septante six'),
        (r'\bsoixante\s*dix\s*cinq\b', 'septante cinq'),
        (r'\bsoixante\s*dix\s*quatre\b', 'septante quatre'),
        (r'\bsoixante\s*dix\s*trois\b', 'septante trois'),
        (r'\bsoixante\s*dix\s*deux\b', 'septante deux'),
        (r'\bsoixante\s*dix\s*un\b', 'septante un'),
        (r'\bsoixante\s*dix\b', 'septante'),

        # quatre-vingt-dix → nonante
        (r'\bquatre\s*vingt[s]?\s*dix\s*neuf\b', 'nonante neuf'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*huit\b', 'nonante huit'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*sept\b', 'nonante sept'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*six\b', 'nonante six'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*cinq\b', 'nonante cinq'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*quatre\b', 'nonante quatre'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*trois\b', 'nonante trois'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*deux\b', 'nonante deux'),
        (r'\bquatre\s*vingt[s]?\s*dix\s*un\b', 'nonante un'),
        (r'\bquatre\s*vingt[s]?\s*dix\b', 'nonante'),

        # quatre-vingt → octante
        (r'\bquatre\s*vingt[s]?\s*neuf\b', 'octante neuf'),
        (r'\bquatre\s*vingt[s]?\s*huit\b', 'octante huit'),
        (r'\bquatre\s*vingt[s]?\s*sept\b', 'octante sept'),
        (r'\bquatre\s*vingt[s]?\s*six\b', 'octante six'),
        (r'\bquatre\s*vingt[s]?\s*cinq\b', 'octante cinq'),
        (r'\bquatre\s*vingt[s]?\s*quatre\b', 'octante quatre'),
        (r'\bquatre\s*vingt[s]?\s*trois\b', 'octante trois'),
        (r'\bquatre\s*vingt[s]?\s*deux\b', 'octante deux'),
        (r'\bquatre\s*vingt[s]?\s*un\b', 'octante un'),
        (r'\bquatre\s*vingt[s]?\b', 'octante'),
    ]
    for pattern, replacement in french_to_simple_patterns:
        normalized = re.sub(pattern, replacement, normalized)

    # 5. Suppression de la suite après "virgule" ou "point"
    normalized = re.split(r'\b(virgule|virgules|point|points)\b', normalized)[0]

    # 6. Nettoyage final : suppression des espaces multiples
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized



def text_to_number(input_text: str) -> Optional[int]:
    """
    Extrait et convertit un nombre à partir d'un texte français.
    
    Stratégie d'extraction par ordre de priorité :
    1. Pourcentages explicites (50%, cinquante pourcent)
    2. Fractions génériques (3/4, trois sur quatre)
    3. Nombres en chiffres (123, 45.67)
    4. Expressions spéciales (tout, rien, presque)
    5. Nombres écrits en lettres (vingt-trois, quatre-vingts)
    
    Args:
        input_text (str): Le texte à analyser
        
    Returns:
        Optional[int]: Le nombre extrait ou None si aucun nombre trouvé
    """
    normalized_input = normalize_text(input_text)
    if not normalized_input:
        return None  # Changé de 0 à None
    
    # 1. Recherche de pourcentages
    percentage_value = find_percentages(normalized_input)
    if percentage_value is not None:
        return percentage_value
    
    # 2. Recherche de fractions génériques
    fraction_value = find_fractions_generic(normalized_input)
    if fraction_value is not None:
        return fraction_value
    
    # 3. Recherche de nombres explicites en chiffres
    explicit_number = find_explicit_numbers(normalized_input)
    if explicit_number is not None:
        return explicit_number
    
    # 4. Recherche d'expressions spéciales
    special_expression = find_special_expressions(normalized_input)
    if special_expression is not None:
        return special_expression
    
    # 5. Parsing des nombres écrits en lettres
    written_number = parse_french_numbers(normalized_input)
    if written_number is not None:
        return written_number
    
    return None  # Changé de 0 à None


def find_explicit_numbers(text: str) -> Optional[int]:
    """
    Trouve les nombres écrits en chiffres dans le texte.
    Exclut les fractions pour éviter les faux positifs.
    
    Args:
        text (str): Le texte à analyser
        
    Returns:
        Optional[int]: Le plus grand nombre trouvé ou None
    """
    # Suppression des fractions pour éviter de prendre juste le dénominateur
    text_without_fractions = re.sub(r'\d+\s*/\s*\d+', '', text)
    
    # Recherche de tous les nombres (entiers ou décimaux)
    number_matches = re.findall(r'\b(\d+(?:[.,]\d+)?)\b', text_without_fractions)
    if number_matches:
        numeric_values = []
        for number_string in number_matches:
            try:
                # Conversion en entier (gestion des décimales avec virgule)
                numeric_values.append(int(float(number_string.replace(',', '.'))))
            except ValueError:
                continue
        
        if numeric_values:
            return max(numeric_values)  # Retour du plus grand nombre trouvé
    
    return None


def find_percentages(text: str) -> Optional[int]:
    """
    Trouve les pourcentages dans le texte avec gestion des erreurs courantes.
    
    Formats supportés :
    - Avec symbole % : "50%", "75 %"
    - Avec mot : "cinquante pourcent", "vingt pour cent"
    
    Args:
        text (str): Le texte à analyser
        
    Returns:
        Optional[int]: La valeur du pourcentage ou None
    """
    # Recherche avec symbole %
    percent_symbol_match = re.search(r'(\d+(?:[.,]\d+)?)\s*%', text)
    if percent_symbol_match:
        return int(float(percent_symbol_match.group(1).replace(',', '.')))
    
    # Recherche avec le mot "pourcent" ou "pour cent"
    if re.search(r'\b(?:pour\s*cent|pourcent)\b', text):
        # Capture du nombre qui précède le mot "pourcent"
        percent_word_match = re.search(r'([\w\s]+?)\s+(?:pour\s*cent|pourcent)', text)
        if percent_word_match:
            number_text = percent_word_match.group(1).strip()
            # Nettoyage des articles en fin de chaîne
            number_text = re.sub(r'\b(?:est|de|le|la|les|du|des)\s*$', '', number_text).strip()
            parsed_number = parse_french_numbers(number_text)
            if parsed_number is not None:
                return parsed_number
    
    return None


def find_fractions_generic(text: str) -> Optional[int]:
    """
    Trouve les fractions dans le texte et les convertit en pourcentages.
    
    Formats supportés :
    - Fractions numériques : "3/4", "1 / 2"
    - Fractions avec "sur" : "3 sur 4", "trois sur quatre"
    - Fractions ordinales : "trois quarts", "un demi", "deux tiers"
    - Groupes : "une douzaine", "trois vingtaines"
    
    Args:
        text (str): Le texte à analyser
        
    Returns:
        Optional[int]: Le pourcentage équivalent de la fraction ou None
    """
    
    # 1. Fractions numériques X/Y (priorité élevée)
    numeric_fraction_match = re.search(r'(\d+)\s*/\s*(\d+)', text)
    if numeric_fraction_match:
        numerator, denominator = int(numeric_fraction_match.group(1)), int(numeric_fraction_match.group(2))
        if denominator != 0:
            result = (numerator / denominator) * 100
            return int(round(result))
    
    # 2. Fractions "X sur Y" avec nombres
    numeric_sur_match = re.search(r'(\d+)\s+sur\s+(\d+)', text)
    if numeric_sur_match:
        numerator, denominator = int(numeric_sur_match.group(1)), int(numeric_sur_match.group(2))
        if denominator != 0:
            result = (numerator / denominator) * 100
            return int(round(result))
    
    # 3. Fractions "X sur Y" avec mots
    word_sur_match = re.search(r'(\w+(?:\s+\w+)*?)\s+sur\s+(\w+(?:\s+\w+)*)', text)
    if word_sur_match:
        numerator_text = word_sur_match.group(1).strip()
        denominator_text = word_sur_match.group(2).strip()
        numerator_value = parse_french_numbers(numerator_text)
        denominator_value = parse_french_numbers(denominator_text)
        if numerator_value is not None and denominator_value is not None and denominator_value > 0:
            result = (numerator_value / denominator_value) * 100
            return int(round(result))
    
    # 4. Dénominateurs ordinaux français (quarts, tiers, etc.)
    ordinal_fraction_patterns = {
        r'\b(?:demie?s?|moitie|moytie|moytee|demiess?|moitye)\b': 2,
        r'\bquarts?|quardts?|quartes?\b': 4,
        r'\btiers|tierss|tierrs\b': 3,
        r'\bquatriemes?|quatriemes|quatriemess?|quatrimes\b': 4,
        r'\bcinquiemes?|cinqiemes?|cinqièmes?|cinquiemess?\b': 5,
        r'\bsixiemes?|sixièmes?|sixiemess?|siximes\b': 6,
        r'\bseptiemes?|septièmes?|septiemess?|septimes\b': 7,
        r'\bhuitiemes?|huitemes?|huitiemess?|huitimes\b': 8,
        r'\bneuviemes?|neuviemes?|neuviémes?|neuviemess?|nevimes\b': 9,
        r'\bdixiemes?|dixièmes?|dixiemess?|diximes\b': 10,
        r'\bonziemes?|onzièmes?|onziemess?|onzimes\b': 11,
        r'\bdouziemes?|douzièmes?|douziemess?|douzimes\b': 12,
        r'\btreiziemes?|treiziémes?|treziemess?|trezimes\b': 13,
        r'\bquatorziemes?|quatorziémes?|quatorziemess?|quatorzimes\b': 14,
        r'\bquinziemes?|quinziémes?|quinziemess?|quinzimes\b': 15,
        r'\bseiziemes?|seiziémes?|seiziemess?|seizimes\b': 16,
        r'\bdixseptiemes?|dix-septiemes?|dixseptiemess?|dixseptimes\b': 17,
        r'\bdixhuitiemes?|dix-huitiemes?|dixhuitiemess?|dixhuitimes\b': 18,
        r'\bdixneuviemes?|dix-neuviemes?|dixneuviemess?|dixnevimes\b': 19,
        r'\bvingtiemes?|vingtiémes?|vingtiemess?|vingtimes?|vingt(i|y)emes?\b': 20,
        r'\btrentiemes?|trentiémes?|trentiemess?|trentimes\b': 30,
        r'\bquarantiemes?|quarantiémes?|quarantiemess?|quarantimes\b': 40,
        r'\bcinquantiemes?|cinquantiémes?|cinquantiemess?|cinquantimes\b': 50,
        r'\bsoixantiemes?|soixantiémes?|soixantiemess?|soixantimes?\b': 60,
        r'\bsoixante[-\s]?dixiemes?|soixante[-\s]?dixiémes?|soixante[-\s]?dixiemess?|soixante[-\s]?diximes?\b': 70,
        r'\bquatre[-\s]?vingtiemes?|quatre[-\s]?vingtiémes?|quatre[-\s]?vingtiemess?|quatre[-\s]?vingtimes?\b': 80,
        r'\bquatre[-\s]?vingt[-\s]?dixiemes?|quatre[-\s]?vingt[-\s]?dixiémes?|quatre[-\s]?vingt[-\s]?dixiemess?|quatre[-\s]?vingt[-\s]?diximes?\b': 90,
        r'\bcente?siemes?|centiemes?|centiemess?|centimes\b': 100,
        r'\bmilliemes?|milliémes?|milliemess?|millimes\b': 1000,
    }
    
    # Recherche des fractions ordinales
    for ordinal_pattern, denominator_value in ordinal_fraction_patterns.items():
        # Construction du pattern pour capturer le numérateur
        numerator_pattern = rf'(\w+(?:\s+\w+)*?)\s+{ordinal_pattern[2:-2]}'
        ordinal_match = re.search(numerator_pattern, text)
        if ordinal_match:
            numerator_text = ordinal_match.group(1).strip()
            
            # Filtrage des articles et mots non numériques
            numerator_text = re.sub(r'\b(?:le|la|les|des?|du)\b', '', numerator_text).strip()
            
            numerator_value = parse_french_numbers(numerator_text)
            if numerator_value is not None and denominator_value > 0:
                result = (numerator_value / denominator_value) * 100
                return int(round(result))
    
    # 5. Cas spéciaux et groupes
    special_fraction_patterns = [
        (r'\b(?:un\s+)?(?:demi|moitie)\b', 50),
        (r'\b(?:la\s+)?moitie\b', 50),
        (r'\b(?:dizaine|douzaine|vingtaine|trentaine|quarantaine|cinquantaine|soixantaine|septantaine|quatre-vingtaine|octantaine|nonantaine|centaine)s?\b', lambda: handle_grouped_numbers(text)),
    ]
    
    for pattern, value_or_function in special_fraction_patterns:
        if re.search(pattern, text):
            if callable(value_or_function):
                result = value_or_function()
                if result is not None:
                    return result
            else:
                return value_or_function
    
    return None


def handle_grouped_numbers(text: str) -> Optional[int]:
    """
    Gère les expressions avec des groupes numériques.
    
    Exemples :
    - "3 douzaines" -> 36
    - "une vingtaine" -> 20
    - "dizaine" -> 10
    
    Args:
        text (str): Le texte contenant l'expression de groupe
        
    Returns:
        Optional[int]: La valeur numérique du groupe ou None
    """
    # Dictionnaire des multiplicateurs de groupe
    group_multipliers = {
        'dizaine': 10,
        'douzaine': 12,
        'vingtaine': 20,
        'trentaine': 30,
        'quarantaine': 40,
        'cinquantaine': 50,
        'soixantaine': 60,
        'septantaine': 70,
        'quatre-vingtaine': 80,
        'octantaine': 80,
        'nonantaine': 90,
        'centaine': 100,
    }

    # Pattern pour capturer multiplicateur + groupe
    group_pattern = r'(\w+(?:\s+\w+)*?)?\s*(%s)s?' % '|'.join(group_multipliers.keys())
    group_match = re.search(group_pattern, text)
    
    if group_match:
        multiplier_text = group_match.group(1)
        group_word = group_match.group(2)
        
        # Nettoyage du multiplicateur (suppression des articles)
        if multiplier_text:
            multiplier_text = multiplier_text.strip()
            multiplier_text = re.sub(r'\b(?:une?|des?|du|les?|la|le)\b', '', multiplier_text).strip()
        
        # Valeur par défaut du multiplicateur
        multiplier_value = 1
        if multiplier_text:
            parsed_multiplier = parse_french_numbers(multiplier_text)
            if parsed_multiplier is not None:
                multiplier_value = parsed_multiplier
        
        # Calcul de la valeur finale
        base_value = group_multipliers.get(group_word)
        if base_value:
            return multiplier_value * base_value

    return None


def find_special_expressions(text: str) -> Optional[int]:
    """
    Trouve les expressions spéciales et les convertit en valeurs numériques.
    
    Expressions supportées :
    - Expressions de zéro : "aucun", "rien", "personne", "nul", "nulle", "zero"
    - Expressions de totalité : "tout", "tous", "totalité"
    - Expressions approximatives : "presque tout", "quasi rien"
    
    Args:
        text (str): Le texte à analyser
        
    Returns:
        Optional[int]: La valeur numérique de l'expression ou None
    """
    
    # Expressions approximatives spéciales
    if re.search(r'\bpresque\s+(?:rien|aucun)\b', text):
        return 5  # "presque rien" = petite quantité
    
    # Expressions de zéro absolu
    # "zero" est traité séparément sans restriction sur "de", "du", "des"
    if re.search(r'\bzero\b', text):
        return 0
    
    # Autres expressions de zéro avec restriction sur "de", "du", "des"
    zero_expression_patterns = [
        r'\b(?:aucun|rien|personne|nul|nulle)\b(?!\s+(?:de|du|des))',
        r'\bpas\s+(?:un|une|de)\b'
    ]
    
    for zero_pattern in zero_expression_patterns:
        if re.search(zero_pattern, text):
            return 0
    
    # Expressions de totalité approximative
    if re.search(r'\b(?:presque|quasi|quasiment)\s+(?:tout|tous|toutes|totalite)\b', text):
        return 95  # "presque tout" = 95% (pas 100%)
    
    # Expressions de totalité absolue
    total_expression_patterns = [
        r'\b(?:tout|tous|toutes|totalite|entierement|completement|integralement)\b',
        r'\b(?:cent\s+pour\s+cent|100\s*%)\b'
    ]
    
    for total_pattern in total_expression_patterns:
        if re.search(total_pattern, text) and not re.search(r'\b(?:presque|quasi|quasiment)\b', text):
            return 100
    
    return None


def parse_french_numbers(text: str) -> Optional[int]:
    """
    Parse généraliste des nombres français écrits en lettres.
    
    Supporte :
    - Nombres simples : "vingt-trois", "quarante-cinq"
    - Nombres complexes : "deux cent trente-quatre"
    - Variantes belges/suisses : "septante", "nonante"
    - Fautes d'orthographe courantes
    - Approximations : "environ cinquante", "plus de cent"
    
    Args:
        text (str): Le texte contenant le nombre en lettres
        
    Returns:
        Optional[int]: Le nombre parsé ou None si non trouvé
    """
    
    if not text:
        return None
    
    # Dictionnaire des mots numériques de base
    number_word_dictionary = get_french_number_words()
    
    # Extraction des tokens potentiellement numériques
    numeric_tokens = extract_numeric_tokens(text)
    
    if not numeric_tokens:
        return None
    
    # Parsing de la séquence de tokens numériques
    return parse_numeric_sequence(numeric_tokens, number_word_dictionary)


def get_french_number_words() -> Dict[str, int]:
    """
    Dictionnaire complet des mots numériques français avec variantes et fautes courantes.
    
    Inclut :
    - Formes standard françaises
    - Variantes belges/suisses (septante, octante, nonante)
    - Fautes d'orthographe fréquentes
    - Formes plurielles
    
    Returns:
        Dict[str, int]: Dictionnaire mot -> valeur numérique
    """
    return {
        # Unités de base (0-9)
        'zero': 0, 'zéro': 0, 'zeero': 0,
        'un': 1, 'une': 1, 'uhn': 1,
        'deux': 2, 'deu': 2,
        'trois': 3, 'troi': 3, 'trois': 3, "troua": 3,
        'quatre': 4, 'quatr': 4, 'catre': 4, "quatres": 4,
        'cinq': 5, 'sinq': 5, 'cing': 5, "cinqs": 5,
        'six': 6, 'sis': 6,
        'sept': 7, 'set': 7, "septs": 7,
        'huit': 8, 'uit': 8, "huits": 8,
        'neuf': 9, 'noeuf': 9, "neufs": 9,

        # Nombres 10-19
        'dix': 10, 'dis': 10,
        'onze': 11, 'onzes': 11, "onz": 11,
        'douze': 12, 'douzes': 12, "douz": 12,
        'treize': 13, 'treizes': 13, "treiz": 13,
        'quatorze': 14, 'quatorz': 14, "quatorzes": 14,
        'quinze': 15, 'quinz': 15, "quinzes": 15,
        'seize': 16, 'seiz': 16, "seizes": 16,

        # Dizaines (20, 30, 40, 50, 60)
        'vingt': 20, 'vint': 20, "vingts": 20,
        'trente': 30, 'trent': 30, "trentes": 30,
        'quarante': 40, 'quarente': 40, "quarantes": 40,
        'cinquante': 50, 'cinqante': 50, 'sinquante': 50, "cinquantes": 50, "cinquente": 50,
        'soixante': 60, 'soissante': 60, "soixantes": 60,

        # Variantes belges/suisses simplifiées (70, 80, 90)
        'septante': 70, 'septente': 70, "septantes": 70, "septentes": 70,
        'huitante': 80, 'uitante': 80, "huitantes": 80,
        'octante': 80, "octantes": 80,
        'nonante': 90, 'nonente': 90, "nonantes": 90,

        # Centaines et milliers
        'cent': 100, 'cents': 100, 'centaine': 100, 'centaines': 100,
        'sant': 100,  # Faute courante
        'mille': 1000, 'milles': 1000, 'millier': 1000, 'milliers': 1000,

        # Millions et plus
        'million': 1000000, 'millions': 1000000,
        'milliard': 1000000000, 'milliards': 1000000000,
        'billion': 1000000000000, 'billions': 1000000000000
    }


def extract_numeric_tokens(text: str) -> List[str]:
    """
    Extrait les tokens (mots) potentiellement numériques d'un texte.
    
    Inclut :
    - Mots numériques directs (un, deux, trois...)
    - Connecteurs numériques (et, de, des, du)
    - Mots approximatifs (environ, plus, moins, presque)
    - Nombres avec tirets
    
    Args:
        text (str): Le texte à analyser
        
    Returns:
        List[str]: Liste des tokens numériques extraits
    """
    
    number_word_dictionary = get_french_number_words()
    text_tokens = text.split()
    extracted_tokens = []
    
    # Mots de liaison numériques
    numeric_connectors = {'et', 'de', 'des', 'du'}
    # Mots d'approximation
    approximation_words = {'environ', 'autour', 'plus', 'moins de', 'presque'}
    
    for token_index, current_token in enumerate(text_tokens):
        # Mots numériques directs
        if current_token in number_word_dictionary:
            extracted_tokens.append(current_token)
        
        # Connecteurs numériques (seulement dans un contexte numérique)
        elif current_token in numeric_connectors:
            has_numeric_context = (
                (token_index > 0 and text_tokens[token_index-1] in number_word_dictionary) or 
                (token_index < len(text_tokens)-1 and text_tokens[token_index+1] in number_word_dictionary)
            )
            if has_numeric_context:
                extracted_tokens.append(current_token)
        
        # Mots d'approximation
        elif current_token in approximation_words:
            if token_index < len(text_tokens) - 1:  # Garder si suivi d'autre chose
                extracted_tokens.append(current_token)
        
        # Nombres composés avec tirets (sécurité si normalize_text n'a pas tout traité)
        elif '-' in current_token and any(part in number_word_dictionary for part in current_token.split('-')):
            extracted_tokens.append(current_token)
    
    return extracted_tokens


def parse_numeric_sequence(token_list: List[str], number_words: Dict[str, int]) -> Optional[int]:
    """
    Parse une séquence de tokens numériques et gère les approximations.
    
    Gère :
    - Modificateurs d'approximation (environ, plus de, moins de, presque)
    - Filtrage des articles (de, des, du)
    - Parsing du nombre principal
    
    Args:
        token_list (List[str]): Liste des tokens numériques
        number_words (Dict[str, int]): Dictionnaire des mots numériques
        
    Returns:
        Optional[int]: Le nombre parsé avec modifications d'approximation ou None
    """
    
    if not token_list:
        return None
    
    # Gestion des modificateurs d'approximation
    approximation_modifiers = {'environ': 0, 'autour': 0, 'plus': 1, 'moins de': -1, 'presque': -4}
    approximation_adjustment = 0
    
    # Filtrage des tokens : séparation approximations / nombres
    filtered_number_tokens = []
    for token in token_list:
        if token in approximation_modifiers:
            approximation_adjustment = approximation_modifiers[token]
        elif token not in {'des', 'du'}:  # Suppression des articles
            filtered_number_tokens.append(token)
    
    if not filtered_number_tokens:
        return None
    
    # Parsing du nombre principal
    parsed_result = parse_compound_number(filtered_number_tokens, number_words)
    
    # Application des modifications d'approximation
    if parsed_result is not None and approximation_adjustment != 0:
        if approximation_adjustment == 1:  # "plus de"
            parsed_result += 1
        elif approximation_adjustment == -1:  # "moins de"
            parsed_result = max(0, parsed_result - 1)
        # Pour "presque", c'est géré dans find_special_expressions
    
    return parsed_result


def parse_compound_number(token_list: List[str], number_words: Dict[str, int]) -> Optional[int]:
    """
    Parse un nombre composé français complexe.
    
    Gère :
    - Formes belges/suisses (septante, octante, nonante) en priorité
    - Formes françaises traditionnelles (soixante-dix, quatre-vingts) en fallback
    - Grandes unités (millions, milliers, centaines)
    - Composition additive et multiplicative
    
    Exemples :
    - "vingt-trois" -> 23
    - "deux cent trente-quatre" -> 234
    - "trois millions cinq cent mille" -> 3500000
    
    Args:
        token_list (List[str]): Liste des tokens du nombre
        number_words (Dict[str, int]): Dictionnaire des mots numériques
        
    Returns:
        Optional[int]: Le nombre composé parsé ou None
    """
    
    total_value = 0
    current_value = 0
    
    token_index = 0
    while token_index < len(token_list):
        current_token = token_list[token_index]
        
        # Priorité aux formes belges/suisses simplifiées
        if current_token == 'septante':
            current_value += 70
        elif current_token in ['huitante', 'octante']:
            current_value += 80
        elif current_token == 'nonante':
            current_value += 90
        elif current_token in number_words:
            token_value = number_words[current_token]
            
            # Gestion des grandes unités (milliards, millions, milliers)
            if token_value >= 1000000000:  # Milliards
                total_value += (current_value or 1) * token_value
                current_value = 0
            elif token_value >= 1000000:  # Millions
                total_value += (current_value or 1) * token_value
                current_value = 0
            elif token_value >= 1000:  # Milliers
                total_value += (current_value or 1) * token_value
                current_value = 0
            elif token_value == 100:  # Centaines
                current_value = (current_value or 1) * 100
            else:  # Unités et dizaines
                current_value += token_value
        
        # Gestion des formes françaises traditionnelles (fallback)
        elif current_token == 'soixante' and token_index + 1 < len(token_list) and token_list[token_index + 1] == 'dix':
            # "soixante dix" -> 70 (si "septante" n'a pas été utilisé)
            base_value = 70
            token_index += 1  # Skip "dix"
            
            # Vérification d'un nombre suivant (soixante dix sept)
            if token_index + 1 < len(token_list) and token_list[token_index + 1] in number_words:
                next_value = number_words[token_list[token_index + 1]]
                if next_value < 10:  # soixante dix un, soixante dix deux, etc.
                    current_value += base_value + next_value
                    token_index += 1
                else:
                    current_value += base_value
            else:
                current_value += base_value
        
        elif current_token == 'quatre' and token_index + 1 < len(token_list) and token_list[token_index + 1] in ['vingt', 'vingts']:
            # "quatre vingt" -> 80 (si "huitante/octante" n'a pas été utilisé)
            base_value = 80
            token_index += 1  # Skip "vingt"
            
            # Vérification d'un nombre suivant
            if token_index + 1 < len(token_list) and token_list[token_index + 1] in number_words:
                next_value = number_words[token_list[token_index + 1]]
                if next_value <= 19:  # quatre vingt dix, quatre vingt un, etc.
                    current_value += base_value + next_value
                    token_index += 1
                else:
                    current_value += base_value
            elif token_index + 1 < len(token_list) and token_list[token_index + 1] == 'dix':  # quatre vingt dix
                current_value += 90
                token_index += 1
            else:
                current_value += base_value
        
        token_index += 1
    
    final_result = total_value + current_value
    return final_result if final_result > 0 else None