from velmo.scope import is_in_scope


def test_in_scope_for_order_question():
    assert is_in_scope("Où est ma commande 4521 ?") is True


def test_out_of_scope_for_unrelated_question():
    assert is_in_scope("Donne-moi une recette de cookies au chocolat") is False
