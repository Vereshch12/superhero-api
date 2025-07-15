from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Hero
from .serializers import HeroSerializer
from .services import SuperheroAPIService

class HeroView(APIView):
    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

        service = SuperheroAPIService()
        try:
            hero_data = service.get_hero_by_name(name)
            if hero_data['response'] == 'success' and hero_data['results']:
                # Check for exact name match
                for result in hero_data['results']:
                    if result['name'].lower() == name.lower():
                        # Check if hero exists in DB
                        if Hero.objects.filter(name__iexact=name).exists():
                            return Response({'error': 'Hero already exists'}, status=status.HTTP_400_BAD_REQUEST)

                        data = {
                            'api_id': result['id'],
                            'name': result['name'],
                            'intelligence': int(result['powerstats'].get('intelligence', 0) or 0),
                            'strength': int(result['powerstats'].get('strength', 0) or 0),
                            'speed': int(result['powerstats'].get('speed', 0) or 0),
                            'power': int(result['powerstats'].get('power', 0) or 0),
                        }
                        serializer = HeroSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(serializer.data, status=status.HTTP_201_CREATED)
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': 'Hero not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Hero not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        name = request.query_params.get('name')
        intelligence = request.query_params.get('intelligence')
        intelligence_op = request.query_params.get('intelligence_op', 'eq')
        strength = request.query_params.get('strength')
        strength_op = request.query_params.get('strength_op', 'eq')
        speed = request.query_params.get('speed')
        speed_op = request.query_params.get('speed_op', 'eq')
        power = request.query_params.get('power')
        power_op = request.query_params.get('power_op', 'eq')

        queryset = Hero.objects.all()

        if name:
            queryset = queryset.filter(name__iexact=name)

        def apply_filter(field, value, op):
            if value is not None:
                value = int(value)
                if op == 'gte':
                    return Q(**{f'{field}__gte': value})
                elif op == 'lte':
                    return Q(**{f'{field}__lte': value})
                else:  # eq
                    return Q(**{f'{field}': value})

        filters = Q()
        if intelligence:
            filters &= apply_filter('intelligence', intelligence, intelligence_op)
        if strength:
            filters &= apply_filter('strength', strength, strength_op)
        if speed:
            filters &= apply_filter('speed', speed, speed_op)
        if power:
            filters &= apply_filter('power', power, power_op)

        queryset = queryset.filter(filters)

        if not queryset.exists():
            return Response({'error': 'No heroes found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HeroSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)