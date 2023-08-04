from rest_framework.views import APIView


#/api/v1/rooms/amenities

class Amenities(APIView):

    def get(self, request):
        pass

    def post(self, request):
        pass


class AmenityDetail(APIView):

    def get(self, request, pk):
        pass

    def put(self, request, pk):
        pass