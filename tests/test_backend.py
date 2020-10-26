import pytest
import backend


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
