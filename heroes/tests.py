import pytest
import json
import requests_mock
from rest_framework.test import APIClient
from django.urls import reverse
from heroes.models import Hero
from heroes.services import SuperheroAPIService

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def mock_superhero_api():
    with requests_mock.Mocker() as m:
        yield m

@pytest.mark.django_db
def test_post_hero_success(client, mock_superhero_api):
    mock_superhero_api.get(
        f"https://superheroapi.com/api/{SuperheroAPIService().api_token}/search/Superman",
        json={
            "response": "success",
            "results": [{
                "id": "644",
                "name": "Superman",
                "powerstats": {
                    "intelligence": "94",
                    "strength": "100",
                    "speed": "100",
                    "power": "100"
                }
            }]
        }
    )
    payload = {'name': 'Superman'}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 201
    assert Hero.objects.filter(name='Superman').exists()
    data = response.json()
    assert data['name'] == 'Superman'
    assert data['api_id'] == 644
    assert data['intelligence'] == 94
    assert data['strength'] == 100
    assert data['speed'] == 100
    assert data['power'] == 100

@pytest.mark.django_db
def test_post_hero_already_exists(client, mock_superhero_api):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    mock_superhero_api.get(
        f"https://superheroapi.com/api/{SuperheroAPIService().api_token}/search/Superman",
        json={
            "response": "success",
            "results": [{
                "id": "644",
                "name": "Superman",
                "powerstats": {
                    "intelligence": "94",
                    "strength": "100",
                    "speed": "100",
                    "power": "100"
                }
            }]
        }
    )
    payload = {'name': 'Superman'}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 400
    assert response.json() == {'error': 'Hero already exists'}

@pytest.mark.django_db
def test_post_hero_not_found(client, mock_superhero_api):
    mock_superhero_api.get(
        f"https://superheroapi.com/api/{SuperheroAPIService().api_token}/search/NonExistentHero",
        json={"response": "error", "results": []}
    )
    payload = {'name': 'NonExistentHero'}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 404
    assert response.json() == {'error': 'Hero not found'}

@pytest.mark.django_db
def test_post_hero_missing_name(client):
    payload = {}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 400
    assert response.json() == {'error': 'Name is required'}

@pytest.mark.django_db
def test_post_hero_empty_name(client):
    payload = {'name': ''}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 400
    assert response.json() == {'error': 'Name is required'}

@pytest.mark.django_db
def test_post_hero_api_error(client, mock_superhero_api):
    mock_superhero_api.get(
        f"https://superheroapi.com/api/{SuperheroAPIService().api_token}/search/Superman",
        status_code=500
    )
    payload = {'name': 'Superman'}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 500
    assert 'error' in response.json()

@pytest.mark.django_db
def test_get_hero_by_name(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    response = client.get(reverse('hero'), {'name': 'Superman'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'
    assert data[0]['api_id'] == 644

@pytest.mark.django_db
def test_get_hero_by_intelligence_eq(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'intelligence': 94, 'intelligence_op': 'eq'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_by_intelligence_gte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'intelligence': 95, 'intelligence_op': 'gte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Batman'

@pytest.mark.django_db
def test_get_hero_by_intelligence_lte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'intelligence': 94, 'intelligence_op': 'lte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_by_strength_eq(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'strength': 85, 'strength_op': 'eq'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Batman'

@pytest.mark.django_db
def test_get_hero_by_strength_gte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'strength': 90, 'strength_op': 'gte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_by_strength_lte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'strength': 90, 'strength_op': 'lte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Batman'

@pytest.mark.django_db
def test_get_hero_by_speed_eq(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'speed': 90, 'speed_op': 'eq'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Batman'

@pytest.mark.django_db
def test_get_hero_by_speed_gte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'speed': 95, 'speed_op': 'gte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_by_speed_lte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'speed': 95, 'speed_op': 'lte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Batman'

@pytest.mark.django_db
def test_get_hero_by_power_eq(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'power': 95, 'power_op': 'eq'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Batman'

@pytest.mark.django_db
def test_get_hero_by_power_gte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'power': 100, 'power_op': 'gte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_by_power_lte(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {'power': 95, 'power_op': 'lte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Batman'

@pytest.mark.django_db
def test_get_hero_combined_filters(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=70, name='Batman', intelligence=100, strength=85, speed=90, power=95)
    response = client.get(reverse('hero'), {
        'name': 'Superman',
        'intelligence': 90,
        'intelligence_op': 'gte',
        'strength': 100,
        'strength_op': 'eq'
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_no_results(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    response = client.get(reverse('hero'), {'name': 'NonExistentHero'})
    assert response.status_code == 404
    assert response.json() == {'error': 'No heroes found matching the criteria'}

@pytest.mark.django_db
def test_get_hero_invalid_numeric_param(client):
    Hero.objects.create(api_id=644, name='Superman', intelligence=94, strength=100, speed=100, power=100)
    response = client.get(reverse('hero'), {'intelligence': 'invalid', 'intelligence_op': 'eq'})
    assert response.status_code == 400  # Assuming view handles invalid input