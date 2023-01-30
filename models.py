from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit_num_of_pennies = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.user.username

class Booking(models.Model):
    booking_date = models.DateField()

    showing_id = models.ForeignKey('Showing', on_delete=models.CASCADE)
    student_id = models.ForeignKey('Student', null=True, on_delete=models.CASCADE)
    
    student_ticket_quantity = models.IntegerField(default=0)
    adult_ticket_quantity = models.IntegerField(default=0)
    child_ticket_quantity = models.IntegerField(default=0)

    total_price = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    club_booking = models.BooleanField(null=True)
    club_id = models.ForeignKey('Club', null=True, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)

    card_num = models.CharField(max_length=16, null=True)
    card_exp_date = models.CharField(max_length=4, null=True)
    card_cvv = models.IntegerField(null=True)

    def __str__(self) -> str:
        return str(self.booking_date) + " " + str(self.showing_id)
class BookingHasSeats(models.Model):
    booking_id = models.ForeignKey('Booking', on_delete=models.CASCADE)
    seat_id = models.ForeignKey('Seat', on_delete=models.CASCADE)

class Ticket(models.Model):
    ticket_type = models.CharField(max_length=50)
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.ticket_type

class Showing(models.Model):
    showing_date = models.DateField()
    showing_time = models.TimeField()

    film_id = models.ForeignKey('Film', on_delete=models.CASCADE)
    screen_id = models.ForeignKey('Screen', on_delete=models.CASCADE)

    def __str__(self):
        return self.showing_date.strftime("%d/%m/%Y") + ' ' + self.showing_time.strftime("%H:%M")

class Film(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    duration = models.IntegerField()
    age_rating = models.CharField(max_length=10)

    def __str__(self):
        return self.title

class Club(models.Model):
    club_name = models.CharField(max_length=50)
    club_rep = models.ForeignKey('Student', on_delete=models.CASCADE, null=True)

    club_credit_num_of_pennies = models.IntegerField(default=0)

    def __str__(self):
        return self.club_name

class Screen(models.Model):
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.id}"

    def create_seats(self):
        """CREATES A LIST OF SEATS FOR THE SCREEN"""
        for i in range(1, self.capacity + 1):
            seat = Seat.objects.create(screen_id=self, seat_num=i)
            seat.save()

class Seat(models.Model):
    screen_id = models.ForeignKey('Screen', on_delete=models.CASCADE)
    seat_num = models.CharField(max_length=10)
    booked = models.BooleanField(default=False)

    def __str__(self):
        return self.seat_num

class CinemaControls(models.Model):
    club_discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    general_discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    covid_distancing = models.BooleanField(default=False)

    def __str__(self):
        return self.club_discount + ' ' + self.general_discount + ' ' + self.covid_distancing