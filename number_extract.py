import re
from typing import Optional, List, Dict, Tuple

def text_to_understanding(text: str) -> str:
    # Normalize the text early for easier processing of keywords and fractions
    normalized_input_text = normalize_text(text)

    # Define words and symbols that indicate a percentage or a quantity that should be expressed as a percentage
    percentage_indicators = [
        "pourcent", "%", "prcent", "prcnt", "pour cent", "pour cents", "demi", "moitie", "tiers", "tier", "quart", "quarts",
        "totalite", "quasi", "tout", "tous", "aucun", "rien", "presque",
        "sur", " / "
    ]

    # --- Handle Fractional Patterns ---
    # Pattern 1: number / number (e.g., "1/4")
    match_num_slash_num = re.search(r'(\d+)\s*/\s*(\d+)', normalized_input_text)
    if match_num_slash_num:
        numerator = int(match_num_slash_num.group(1))
        denominator = int(match_num_slash_num.group(2))
        if denominator != 0:
            percentage_value = (numerator / denominator) * 100
            return f"{round(percentage_value)}%"

    # Pattern 2: number "sur" number (e.g., "1 sur 4") or word "sur" word (e.g., "un sur quatre")
    match_num_sur_num = re.search(r'(\S+)\s+sur\s+(\S+)', normalized_input_text)
    if match_num_sur_num:
        # text_to_number already applies normalize_text internally, so no need here
        first_part = match_num_sur_num.group(1)
        second_part = match_num_sur_num.group(2)
        
        # Convert identified parts to numbers using text_to_number (which extracts digits)
        numerator = text_to_number(first_part)
        denominator = text_to_number(second_part)

        if numerator is not None and denominator is not None:
            try:
                if denominator != 0:
                    percentage_value = (numerator / denominator) * 100
                    return f"{round(percentage_value)}%"
            except ValueError:
                pass  # If conversion fails, it's not a valid numerical fraction, continue to next checks

    # --- Handle "ième" or "ièmes" suffix (anywhere in the text) ---
    # This is now handled before other percentage indicators if a number is present.
    # We look for "ieme" or "iemes" within any word.
    if re.search(r'(?:ieme|iemes|ième|ièmes)', normalized_input_text):
        nombre = text_to_number(normalized_input_text)
        if nombre is not None:
            return f"{nombre}%"

    # --- Handle Direct Percentage and Keyword Indicators ---
    # Get the base number from the text
    nombre = text_to_number(normalized_input_text)

    for indicator in percentage_indicators:
        # Use word boundaries for words to prevent partial matches (e.g., "sur" in "surcharge")
        # For '%' symbol, direct search is fine.
        if indicator == "%" and indicator in normalized_input_text:
            if nombre is not None:
                return f"{nombre}%"
        elif indicator != "%" and re.search(r'\b' + re.escape(indicator) + r'\b', normalized_input_text):
            if nombre is not None:  # Only append % if a number was found
                return f"{nombre}%"
            # Special handling for "totalité", "tout", "tous", "aucun", "rien" if no number is present
            if indicator in ["totalite", "tout", "tous"]:
                return "100%"
            elif indicator in ["aucun", "rien"]:
                return "0%"

    # If no fractional pattern, direct percentage, or strong percentage-implying keyword is found,
    # return just the number if one exists, otherwise "0".
    if nombre is not None:
        return str(nombre)
    
    return "0"

def normalize_text(text: str) -> str:
    """
    Normalise le texte :
    - Met en minuscules.
    - Supprime les accents.
    - Remplace les tirets et underscores par des espaces.
    - Supprime le mot 'et'.
    - Convertit les nombres 'soixante-dix' à 'quatre-vingt-dix-neuf' en 'septante/octante/nonante'.
    - Tolère fautes fréquentes : oublis de 's', tirets manquants, etc.
    - Supprime les espaces multiples.
    """
    # 1. Minuscule + tirets/underscores → espace
    text = text.lower()
    text = text.replace('-', ' ').replace('_', ' ')
    
    # 2. Supprimer "et"
    text = re.sub(r'\bet\b', '', text)

    # 3. Supprimer accents
    accent_map = str.maketrans({
        'à': 'a', 'â': 'a', 'ä': 'a', 'á': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'î': 'i', 'ï': 'i', 'í': 'i',
        'ô': 'o', 'ö': 'o', 'ó': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u', 'ú': 'u',
        'ÿ': 'y', 'ý': 'y',
        'ç': 'c'
    })
    text = text.translate(accent_map)

    # 4. Correction des nombres fautifs (regex robustes)
    number_word_patterns = [
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

    for pattern, remplacement in number_word_patterns:
        text = re.sub(pattern, remplacement, text)

    # 5. Nettoyage final
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def text_to_number(text: str) -> int:
    """
    Extrait un nombre à partir de n'importe quel texte français.
    Corrigé pour gérer les erreurs de logique sans sur-apprentissage.
    """
    normalized_text = normalize_text(text) # Normalize at the very beginning
    if not normalized_text: # Check normalized text for emptiness
        return 0
    
    # 1. Pourcentages (avant les nombres explicites car "50%" doit donner 50, pas 50)
    percentage = find_percentages(normalized_text)
    if percentage is not None:
        return percentage
    
    # 2. Fractions génériques (avant nombres explicites)
    fraction = find_fractions_generic(normalized_text)
    if fraction is not None:
        return fraction
    
    # 3. Nombres explicites (chiffres)
    explicit_number = find_explicit_numbers(normalized_text)
    if explicit_number is not None:
        return explicit_number
    
    # 4. Expressions spéciales avec nuances
    special = find_special_expressions(normalized_text)
    if special is not None:
        return special
    
    # 5. Nombres en lettres (parsing généraliste)
    written_number = parse_french_numbers(normalized_text)
    if written_number is not None:
        return written_number
    
    return 0

def find_explicit_numbers(text: str) -> Optional[int]:
    """Trouve les nombres en chiffres - ne pas confondre avec fractions"""
    # Exclure les fractions X/Y pour éviter de prendre juste le dénominateur
    text_without_fractions = re.sub(r'\d+\s*/\s*\d+', '', text)
    
    numbers = re.findall(r'\b(\d+(?:[.,]\d+)?)\b', text_without_fractions)
    if numbers:
        numeric_values = []
        for num_str in numbers:
            try:
                numeric_values.append(int(float(num_str.replace(',', '.'))))
            except ValueError:
                continue
        
        if numeric_values:
            return max(numeric_values)
    
    return None

def find_percentages(text: str) -> Optional[int]:
    """Trouve les pourcentages avec gestion des erreurs courantes"""
    # Avec symbole %
    percent_match = re.search(r'(\d+(?:[.,]\d+)?)\s*%', text)
    if percent_match:
        return int(float(percent_match.group(1).replace(',', '.')))
    
    # Avec le mot "pourcent" - chercher le nombre qui précède
    if re.search(r'\b(?:pour\s*cent|pourcent)\b', text):
        # Pattern plus robuste pour capturer le nombre avant "pourcent"
        match = re.search(r'([\w\s]+?)\s+(?:pour\s*cent|pourcent)', text)
        if match:
            number_text = match.group(1).strip()
            # Nettoyer les mots non numériques en fin
            number_text = re.sub(r'\b(?:est|de|le|la|les|du|des)\s*$', '', number_text).strip()
            number = parse_french_numbers(number_text)
            if number is not None:
                return number
    
    return None

def find_fractions_generic(text: str) -> Optional[int]:
    """Trouve les fractions de manière générique avec corrections"""
    
    # Fractions numériques X/Y avec priorité
    fraction_match = re.search(r'(\d+)\s*/\s*(\d+)', text)
    if fraction_match:
        num, den = int(fraction_match.group(1)), int(fraction_match.group(2))
        if den != 0:
            result = (num / den) * 100
            return int(round(result))
    
    # Fractions "X sur Y"
    sur_match = re.search(r'(\d+)\s+sur\s+(\d+)', text)
    if sur_match:
        num, den = int(sur_match.group(1)), int(sur_match.group(2))
        if den != 0:
            result = (num / den) * 100
            return int(round(result))
    
    # Fractions avec mots : "X sur Y"
    sur_word_match = re.search(r'(\w+(?:\s+\w+)*?)\s+sur\s+(\w+(?:\s+\w+)*)', text)
    if sur_word_match:
        num_text = sur_word_match.group(1).strip()
        den_text = sur_word_match.group(2).strip()
        num = parse_french_numbers(num_text)
        den = parse_french_numbers(den_text)
        if num is not None and den is not None and den > 0:
            result = (num / den) * 100
            return int(round(result))
    
    # Dénominateurs ordinaux français - patterns plus précis
    ordinal_map = {
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
    
    # 70 : soixante-dixièmes (FR)
    r'\bsoixante[-\s]?dixiemes?|soixante[-\s]?dixiémes?|soixante[-\s]?dixiemess?|soixante[-\s]?diximes?\b': 70,
    
    # 80 : quatre-vingtièmes (FR)
    r'\bquatre[-\s]?vingtiemes?|quatre[-\s]?vingtiémes?|quatre[-\s]?vingtiemess?|quatre[-\s]?vingtimes?\b': 80,
    
    # 90 : quatre-vingt-dixièmes (FR)
    r'\bquatre[-\s]?vingt[-\s]?dixiemes?|quatre[-\s]?vingt[-\s]?dixiémes?|quatre[-\s]?vingt[-\s]?dixiemess?|quatre[-\s]?vingt[-\s]?diximes?\b': 90,

    r'\bcente?siemes?|centiemes?|centiemess?|centimes\b': 100,

    r'\bmilliemes?|milliémes?|milliemess?|millimes\b': 1000,
}
    
    for ordinal_pattern, denominator in ordinal_map.items():
        # Pattern plus strict pour capturer le numérateur
        # The 'ordinal_pattern[2:-2]' removes the '\b(?:...)\b' to get just the word part
        pattern = rf'(\w+(?:\s+\w+)*?)\s+{ordinal_pattern[2:-2]}' 
        match = re.search(pattern, text)
        if match:
            numerator_text = match.group(1).strip()
            
            # Filtrer les articles et mots non numériques
            numerator_text = re.sub(r'\b(?:le|la|les|des?|du)\b', '', numerator_text).strip()
            
            numerator = parse_french_numbers(numerator_text)
            if numerator is not None and denominator > 0:
                result = (numerator / denominator) * 100
                return int(round(result))
    
    # Cas spéciaux mais génériques
    special_fraction_patterns = [
        (r'\b(?:un\s+)?(?:demi|moitie)\b', 50),
        (r'\b(?:la\s+)?moitie\b', 50),
        (r'\b(?:dizaine|douzaine|vingtaine|trentaine|quarantaine|cinquantaine|soixantaine|septantaine|quatre-vingtaine|octantaine|nonantaine|centaine)s?\b', lambda: handle_grouped_numbers(text)),
    ]
    
    for pattern, value in special_fraction_patterns:
        if re.search(pattern, text):
            if callable(value):
                result = value()
                if result is not None:
                    return result
            else:
                return value
    
    return None

def handle_grouped_numbers(text: str) -> Optional[int]:
    """
    Gère les expressions avec des groupes comme 'douzaine', 'dizaine', 'vingtaine', 'trentaine', etc.
    Exemple : "3 douzaines" => 36, "une vingtaine" => 20, "dizaine" => 10
    """
    multiples = {
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

    # Créer un pattern regex pour tous les termes possibles (au singulier et pluriel)
    pattern = r'(\w+(?:\s+\w+)*?)?\s*(%s)s?' % '|'.join(multiples.keys())

    match = re.search(pattern, text)
    if match:
        multiplier_text = match.group(1)
        group_word = match.group(2)
        
        # Nettoyer le texte du multiplicateur (articles, espaces)
        if multiplier_text:
            multiplier_text = multiplier_text.strip()
            multiplier_text = re.sub(r'\b(?:une?|des?|du|les?|la|le)\b', '', multiplier_text).strip()
        
        # Si pas de multiplicateur, on considère 1
        multiplier = 1
        if multiplier_text:
            # parse_french_numbers est supposé être une fonction qui transforme texte en nombre
            multiplier_parsed = parse_french_numbers(multiplier_text)
            if multiplier_parsed is not None:
                multiplier = multiplier_parsed
        
        base_value = multiples.get(group_word)
        if base_value:
            return multiplier * base_value

    return None

def find_special_expressions(text: str) -> Optional[int]:
    """Trouve les expressions spéciales avec nuances correctes"""
    
    # Presque rien/aucun = petite quantité (5)
    if re.search(r'\bpresque\s+(?:rien|aucun)\b', text):
        return 5
    
    # Expressions de zéro
    zero_patterns = [
        r'\b(?:aucun|rien|zero|personne|nul|nulle)\b(?!\s+(?:de|du|des))',
        r'\bpas\s+(?:un|une|de)\b'
    ]
    
    for pattern in zero_patterns:
        if re.search(pattern, text):
            return 0
    
    # Presque tout/totalité = 95 (pas 100)
    if re.search(r'\b(?:presque|quasi|quasiment)\s+(?:tout|tous|toutes|totalite)\b', text):
        return 95
    
    # Expressions de totalité = 100
    total_patterns = [
        r'\b(?:tout|tous|toutes|totalite|entierement|completement|integralement)\b',
        r'\b(?:cent\s+pour\s+cent|100\s*%)\b'
    ]
    
    for pattern in total_patterns:
        if re.search(pattern, text) and not re.search(r'\b(?:presque|quasi|quasiment)\b', text):
            return 100
    
    return None

def parse_french_numbers(text: str) -> Optional[int]:
    """Parse généraliste des nombres français avec corrections"""
    
    if not text:
        return None
    
    # Dictionnaire des nombres de base
    number_words = get_french_number_words()
    
    # Handling hyphenated numbers is now implicitly handled by normalize_text
    # which replaces hyphens with spaces at the start.
    
    # Filtrer pour ne garder que les mots potentiellement numériques
    tokens = extract_numeric_tokens(text)
    
    if not tokens:
        return None
    
    # Parser la séquence de tokens numériques
    return parse_numeric_sequence(tokens, number_words)


def get_french_number_words() -> Dict[str, int]:
    """Dictionnaire des mots numériques français de base, incluant des fautes fréquentes."""
    return {
        # Unités
        'zero': 0, 'zéro': 0, 'zeero': 0,
        'un': 1, 'une': 1, 'uhn': 1,
        'deux': 2, 'deu': 2,
        'trois': 3, 'troi': 3, 'trois': 3, "troua" : 3,
        'quatre': 4, 'quatr': 4, 'catre': 4, "quatres" : 4,
        'cinq': 5, 'sinq': 5, 'cing': 5, "cinqs" : 5,
        'six': 6, 'sis': 6,
        'sept': 7, 'set': 7, "septs" : 7,
        'huit': 8, 'uit': 8, "huits" : 8,
        'neuf': 9, 'noeuf': 9, "neufs" : 9,

        # Dixaines simples
        'dix': 10, 'dis': 10,
        'onze': 11, 'onzes': 11, "onz" : 11,
        'douze': 12, 'douzes': 12, "douz" : 12,
        'treize': 13, 'treizes': 13, "treiz" : 13,
        'quatorze': 14, 'quatorz': 14, "quatorzes" : 14,
        'quinze': 15, 'quinz': 15, "quinzes" : 15,
        'seize': 16, 'seiz': 16, "seizes" : 16,

        # Dizaines
        'vingt': 20, 'vint': 20, "vingts" : 20,
        'trente': 30, 'trent': 30, "trentes" : 30,
        'quarante': 40, 'quarente': 40, "quarantes" : 40,
        'cinquante': 50, 'cinqante': 50, 'sinquante': 50, "cinquantes" : 50, "cinquente" : 50,
        'soixante': 60, 'soissante': 60, "soixantes" : 60,

        # Variantes belges/suisses
        'septante': 70, 'septente': 70, "septantes" : 70, "septentes" : 70,
        'huitante': 80, 'uitante': 80, "huitantes" : 80,
        'octante': 80, "octantes" : 80,
        'nonante': 90, 'nonente': 90, "nonantes" : 90,

        # Centaines
        'cent': 100, 'cents': 100, 'centaine': 100, 'centaines': 100,
        'sant': 100,

        # Milliers
        'mille': 1000, 'milles': 1000, 'millier': 1000, 'milliers': 1000,

        # Millions et plus
        'million': 1000000, 'millions': 1000000,
        'milliard': 1000000000, 'milliards': 1000000000,
        'billion': 1000000000000, 'billions': 1000000000000
    }

def extract_numeric_tokens(text: str) -> List[str]:
    """Extrait les tokens potentiellement numériques"""
    
    number_words = get_french_number_words()
    tokens = text.split()
    numeric_tokens = []
    
    numeric_connectors = {'et', 'de', 'des', 'du'}
    approximative_words = {'environ', 'autour', 'plus', 'moins', 'presque'}
    
    for i, token in enumerate(tokens):
        # Mots numériques directs
        if token in number_words:
            numeric_tokens.append(token)
        
        # Connecteurs numériques si dans contexte numérique
        elif token in numeric_connectors:
            if (i > 0 and tokens[i-1] in number_words) or (i < len(tokens)-1 and tokens[i+1] in number_words):
                numeric_tokens.append(token)
        
        # Mots approximatifs
        elif token in approximative_words:
            if i < len(tokens) - 1:  # Garder si suivi d'autre chose
                numeric_tokens.append(token)
        
        # Nombres avec tirets (already handled by normalize_text, but keep for robustness if not all are caught)
        elif '-' in token and any(part in number_words for part in token.split('-')):
            numeric_tokens.append(token)
    
    return numeric_tokens

def parse_numeric_sequence(tokens: List[str], number_words: Dict[str, int]) -> Optional[int]:
    """Parse une séquence de tokens numériques avec corrections"""
    
    if not tokens:
        return None
    
    # Gestion des approximations
    approximations = {'environ': 0, 'autour': 0, 'plus': 1, 'moins': -1, 'presque': -4}
    approximation_modifier = 0
    
    # Filtrer les mots d'approximation
    filtered_tokens = []
    for token in tokens:
        if token in approximations:
            approximation_modifier = approximations[token]
        elif token not in {'de', 'des', 'du'}:
            filtered_tokens.append(token)
    
    if not filtered_tokens:
        return None
    
    # Parse the main number
    result = parse_compound_number(filtered_tokens, number_words)
    
    if result is not None and approximation_modifier != 0:
        if approximation_modifier == 1:  # "plus de"
            result += 1
        elif approximation_modifier == -1:  # "moins de"
            result = max(0, result - 1)
        # For "presque", it's handled in find_special_expressions
    
    return result

def parse_compound_number(tokens: List[str], number_words: Dict[str, int]) -> Optional[int]:
    """
    Parse un nombre composé français, priorisant les formes belges/suisses
    et gérant correctement les formes françaises si les formes belges/suisses ne sont pas utilisées.
    """
    
    total = 0
    current = 0
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Prioriser les formes belges/suisses
        if token == 'septante':
            current += 70
        elif token == 'huitante' or token == 'octante':
            current += 80
        elif token == 'nonante':
            current += 90
        elif token in number_words:
            value = number_words[token]
            
            # Grandes unités (milliards, millions, milliers)
            if value >= 1000000000:
                total += (current or 1) * value
                current = 0
            elif value >= 1000000:
                total += (current or 1) * value
                current = 0
            elif value >= 1000:
                total += (current or 1) * value
                current = 0
            elif value == 100:
                current = (current or 1) * 100
            else:
                current += value
        
        # Gestion des formes françaises (soixante-dix, quatre-vingt-dix) si les formes belges/suisses n'ont pas été utilisées
        elif token == 'soixante' and i + 1 < len(tokens) and tokens[i + 1] == 'dix':
            # If "soixante dix" is found, and "septante" was not captured before, treat as 70
            base = 70
            i += 1  # Skip "dix"
            
            # Look for a trailing number (soixante-dix-sept -> soixante dix sept)
            if i + 1 < len(tokens) and tokens[i + 1] in number_words:
                next_val = number_words[tokens[i + 1]]
                if next_val < 10:  # soixante dix un, soixante dix deux, etc.
                    current += base + next_val
                    i += 1
                else:
                    current += base
            else:
                current += base
        
        elif token == 'quatre' and i + 1 < len(tokens) and tokens[i + 1] in ['vingt', 'vingts']:
            # If "quatre vingt" is found, and "huitante/octante" was not captured before, treat as 80
            base = 80
            i += 1  # Skip "vingt"
            
            # Look for a trailing number (quatre vingt onze)
            if i + 1 < len(tokens) and tokens[i + 1] in number_words:
                next_val = number_words[tokens[i + 1]]
                if next_val <= 19:  # quatre vingt dix, quatre vingt un, etc.
                    current += base + next_val
                    i += 1
                else:
                    current += base
            elif i + 1 < len(tokens) and tokens[i + 1] == 'dix': # Specific case for quatre vingt dix
                current += 90
                i += 1
            else:
                current += base
        
        i += 1
    
    result = total + current
    return result if result > 0 else None