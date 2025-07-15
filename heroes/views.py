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
        if not name or not isinstance(name, str) or not name.strip():
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

        service = SuperheroAPIService()
        try:
            hero_data = service.get_hero_by_name(name)
            if hero_data['response'] == 'success' and hero_data['results']:
                for result in hero_data['results']:
                    if result['name'].lower() == name.lower():
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
            try:
                value = int(value)
                if value < 0:
                    raise ValueError("Value must be non-negative")
                if op == 'gte':
                    return Q(**{f'{field}__gte': value})
                elif op == 'lte':
                    return Q(**{f'{field}__lte': value})
                else:  # eq
                    return Q(**{f'{field}': value})
            except (ValueError, TypeError):
                return Response({'error': f'Invalid value for {field}'}, status=status.HTTP_400_BAD_REQUEST)

        filters = Q()
        for field, value, op in [
            ('intelligence', intelligence, intelligence_op),
            ('strength', strength, strength_op),
            ('speed', speed, speed_op),
            ('power', power, power_op)
        ]:
            if value:
                result = apply_filter(field, value, op)
                if isinstance(result, Response):
                    return result
                filters &= result

        queryset = queryset.filter(filters)

        if not queryset.exists():
            return Response({'error': 'No heroes found matching the criteria'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HeroSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)