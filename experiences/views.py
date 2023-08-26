from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Perk, Experience
from .serializers import PerkSerializer, ExperiencesSerializer

from bookings.serialziers import PublicBookingSerializer
from bookings.models import Booking


class Experiences(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        experience = Experience.objects.all()
        serializer = ExperiencesSerializer(experience, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExperiencesSerializer(data=request.data)
        if serializer.is_valid():
            experience = serializer.save(host=request.user)
            serializer = ExperiencesSerializer(experience)
            return Response(serializer.data)


class ExperienceDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk=pk)
        serializer = ExperiencesSerializer(experience)
        return Response(serializer.data)

    def put(self, request, pk):
        experience = self.get_object(pk=pk)
        if experience.host != request.user:
            raise ParseError
        serializer = ExperiencesSerializer(
            experience,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            experience = serializer.save(host=request.user)
            serializer = ExperiencesSerializer(experience)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        experience = self.get_object(pk=pk)
        if experience.host != request.user:
            raise ParseError
        experience.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Perks(APIView):
    def get(self, request):
        all_perks = Perk.objects.all()
        serializer = PerkSerializer(all_perks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PerkSerializer(data=request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(PerkSerializer(perk).data)
        else:
            return Response(serializer.errors)


class PerkDetail(APIView):
    def get_object(self, pk):
        try:
            return Perk.objects.get(pk=pk)
        except Perk.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        perk = self.get_object(pk)
        serializer = PerkSerializer(perk)
        return Response(serializer.data)

    def put(self, request, pk):
        perk = self.get_object(pk)
        # partial 필수 (부분적 업데이트라고 알려주는 부분)
        serializer = PerkSerializer(perk, data=request.data, partial=True)
        if serializer.is_valid():
            updated_perk = serializer.save()
            return Response(PerkSerializer(updated_perk).data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        perk = self.get_object(pk)
        perk.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class ExperiencePerks(APIView):
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk=pk)
        perks = experience.perks.all()
        serializer = PerkSerializer(perks, many=True)
        return Response(serializer.data)


class ExperienceBookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk=pk)
        bookings = experience.bookings.all()
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = PublicBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(
                experience=self.get_object(pk=pk), user=request.user
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ExperienceBookingDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_experinece(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get_booking(self, pk):
        try:
            return Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            raise NotFound

    def get(self, request, experience_pk, booking_pk):
        experience = self.get_experinece(pk=experience_pk)
        try:
            booking = experience.bookings.get(pk=booking_pk)
        except:
            raise ParseError
        serializer = PublicBookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, experience_pk, booking_pk):
        experience = self.get_experinece(pk=experience_pk)
        try:
            booking = experience.bookings.get(pk=booking_pk)
        except:
            raise ParseError
        serializer = PublicBookingSerializer(
            booking,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            booking = serializer.save()
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, experience_pk, booking_pk):
        experience = self.get_experinece(pk=experience_pk)
        try:
            booking = experience.bookings.get(pk=booking_pk)
        except:
            raise ParseError
        booking.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Rooms(APIView):
    def get(self, request):
        pass
