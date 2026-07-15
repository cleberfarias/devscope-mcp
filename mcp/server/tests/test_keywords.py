from devscope.services.keywords import extract_keywords


def test_extracts_significant_words_only() -> None:
    task = "Implementar um novo fluxo de login para contas trial expiradas."

    terms = extract_keywords(task)

    assert "login" in terms
    assert "trial" in terms
    assert "fluxo" in terms
    assert "expiradas" in terms
    assert "implementar" not in [t.lower() for t in terms]


def test_strips_punctuation_and_keeps_identifiers() -> None:
    terms = extract_keywords("Corrigir bug no UserService, urgente!")

    assert "UserService" in terms
    assert "urgente" in terms


def test_deduplicates_case_insensitively() -> None:
    terms = extract_keywords("login LOGIN Login precisa de ajuste")

    matches = [t for t in terms if t.lower() == "login"]
    assert len(matches) == 1
    assert "precisa" in terms
    assert "ajuste" in terms


def test_respects_limit() -> None:
    task = "abelha bicicleta cachorro dinamarca elefante formiga girafa"

    terms = extract_keywords(task, limit=3)

    assert len(terms) == 3


def test_short_words_are_ignored() -> None:
    terms = extract_keywords("de um no para com")

    assert terms == []
