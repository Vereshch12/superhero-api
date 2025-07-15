import pytest
import json
from rest_framework.test import APIClient
from django.urls import reverse
from heroes.models import Hero

@pytest.mark.django_db
def test_post_hero_success():
    client = APIClient()
    payload = {'name': 'Superman'}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 201
    assert Hero.objects.filter(name='Superman').exists()
    data = response.json()
    assert data['name'] == 'Superman'
    assert 'api_id' in data
    assert 'intelligence' in data
    assert 'strength' in data
    assert 'speed' in data
    assert 'power' in data

@pytest.mark.django_db
def test_post_hero_already_exists():
    Hero.objects.create(api_id=1, name='Superman', intelligence=90, strength=100, speed=100, power=100)
    client = APIClient()
    payload = {'name': 'Superman'}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 400
    assert response.json() == {'error': 'Hero already exists'}

@pytest.mark.django_db
def test_post_hero_not_found():
    client = APIClient()
    payload = {'name': 'NonExistentHero'}
    response = client.post(reverse('hero'), data=payload, format='json')
    assert response.status_code == 404
    assert response.json() == {'error': 'Hero not found'}

@pytest.mark.django_db
def test_get_hero_by_name():
    Hero.objects.create(api_id=1, name='Superman', intelligence=90, strength=100, speed=100, power=100)
    client = APIClient()
    response = client.get(reverse('hero'), {'name': 'Superman'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_by_intelligence_gte():
    Hero.objects.create(api_id=1, name='Superman', intelligence=90, strength=100, speed=100, power=100)
    Hero.objects.create(api_id=2, name='Batman', intelligence=80, strength=85, speed=90, power=95)
    client = APIClient()
    response = client.get(reverse('hero'), {'intelligence': 85, 'intelligence_op': 'gte'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Superman'

@pytest.mark.django_db
def test_get_hero_no_results():
    client = APIClient()
    response = client.get(reverse('hero'), {'name': 'NonExistentHero'})
    assert response.status_code == 404
    assert response.json() == {'error': 'No heroes found matching the criteria'}