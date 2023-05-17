import pytest

from api import PetFriends
from settings import valid_email, valid_password, not_valid_password, not_valid_email
import os

pf = PetFriends()

NEGATIVE_PARAMS = [
    ('Пес', 'Собака', 'четыре'),
    ('Пес', 'Собака', 0),
    ('Пес', 'Собака', 4.5),
    ('Пес', 'Собака', 1000**10),
    ('a'*257, 'Собака', 5),
    ('Пес', 'Собака', ''),
    ('', '', ''),
    (' ` | /  , ; : & < > ^ * ? Tab « »', '}{=*&', '}{=*&'),
    ('♣ ☺ ♂', '}{=*&', '}{=*&'),
    ('Барбос', 2, 2),
    ('Radjy', 'Собака', -7)
]


def test_get_api_key(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_pets_list_all(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Пэс', animal_type='Пэсшнауцер',
                                     age='4', pet_photo='images/dog.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name


@pytest.mark.parametrize('name, animal_type, age', [
    ('Кэт', 'кит', 4),
    ('КОТС', 'СТОК', 2),
    ('Rubi', 'CAT', 7)
])
def test_successful_update_self_pet_info(name, animal_type, age):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")


@pytest.mark.parametrize('name, animal_type, age', [
    ('Пес', 'Собака', 4),
    ('Барбос', 'Собака', 2),
    ('Radjy', 'Собака', 7)
])
def test_successful_add_pet_without_photo(name, animal_type, age):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name


def test_successful_set_photo(pet_photo='images/dog.jpg'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
        assert status == 200
        assert result['pet_photo'] is not None
    else:
        raise Exception("There is no my pets")


def test_successful_delete_self_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Кот", "кот", "3", "images/cat.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200
    assert pet_id not in my_pets.values()


@pytest.mark.parametrize('name, animal_type, age', NEGATIVE_PARAMS)
def test_negative_add_pet_without_photo(name, animal_type, age):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400
    assert result['name'] is None


def test_negative_get_api_key(email=not_valid_email, password=not_valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result


def test_negative_get_pets_list_all(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    auth_key['key'] += '1'
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403


@pytest.mark.parametrize('name, animal_type, age', NEGATIVE_PARAMS)
def test_negative_update_self_pet_info(name, animal_type, age):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 400
        assert result is None
    else:
        raise Exception("There is no my pets")


def teardown():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        for i in my_pets['pets']:
            pet_id = i['id']
            pf.delete_pet(auth_key, pet_id)
    print('\nTEARDOWN DONE')