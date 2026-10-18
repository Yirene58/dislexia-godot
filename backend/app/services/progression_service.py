def experience_required(level: int) -> int:
    """Experiencia total necesaria para alcanzar un nivel."""
    return (level - 1) ** 2 * 100


def calculate_level(total_experience: int) -> int:
    """Calcula el nivel según la experiencia acumulada."""
    level = 1

    while experience_required(level + 1) <= total_experience:
        level += 1

    return level


def add_experience(character, amount: int):
    """Agrega experiencia y actualiza el nivel."""
    if type(amount) is not int or amount <= 0:
        raise ValueError("La experiencia debe ser un entero positivo")

    character.experience += amount
    character.level = calculate_level(character.experience)

    return character
