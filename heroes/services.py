import requests
import os

class SuperheroAPIService:
    def __init__(self):
        self.base_url = "https://superheroapi.com/api"
        self.api_token = os.getenv('SUPERHERO_API_TOKEN')

    def get_hero_by_name(self, name):
        url = f"{self.base_url}/{self.api_token}/search/{name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()