import pytest
import backend


def test_pre_init():
    with pytest.raises(backend.exceptions.NotInitialised):
        backend.authenticate("user", "pass")


def test_init(db):
    pass


@pytest.mark.asyncio
async def test_registration(db):
    global vasya_id
    vasya_id = await backend.register(
        "vpleshivy",
        "youllneverguessmypassword",
        "st000000@student.spbu.ru",
        "Вася Плешивый",
    )
    with pytest.raises(backend.exceptions.NickTaken):
        await backend.register(
            "vpleshivy",
            "youllneverguessmypassword",
            "st000000@student.spbu.ru",
            "Вася Плешивый",
        )
    with pytest.raises(backend.exceptions.EmailTaken):
        await backend.register(
            "pppetrov",
            "qwerty12345",
            "st000000@student.spbu.ru",
            "Петров Пётр Петрович",
        )


@pytest.mark.asyncio
async def test_authentication(db):
    assert (
        await backend.authenticate("vpleshivy", "youllneverguessmypassword") == vasya_id
    )
    with pytest.raises(backend.exceptions.AuthenticationError):
        await backend.authenticate("vpleshivy", "youllguessmypassword") == vasya_id
    with pytest.raises(backend.exceptions.AuthenticationError):
        await backend.authenticate("pppetrov", "qwerty12345")
