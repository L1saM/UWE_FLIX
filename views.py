from asyncio import constants
from decimal import Decimal
import imp
from locale import currency
from django.shortcuts import redirect, render
from sqlalchemy import null
from .forms import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
from django.contrib import messages

from datetime import datetime

from .models import *

# CHECK IF THE NEEDED GROUPS EXISTS IF NOT CREATE THEM
student_group = Group.objects.get_or_create(name='Student')[0]
club_representitive_group = Group.objects.get_or_create(name='Club Representitive')[0]
cinema_manager_group = Group.objects.get_or_create(name='Cinema Manager')[0]
account_manager_group = Group.objects.get_or_create(name='Account Manager')[0]

# CREATE THE DEFAULT TICKETS
student_ticket = Ticket.objects.get_or_create(ticket_type='Student', ticket_price=4.00)[0]
child_ticket = Ticket.objects.get_or_create(ticket_type='Child', ticket_price=4.00)[0]
adult_ticker = Ticket.objects.get_or_create(ticket_type='Adult', ticket_price=7.00)[0]

#CREATE THE DEFAULT CINEMA MANAGEMENT RECORDS
cinema_controls = CinemaControls.objects.get_or_create(id=1)

def home(request):

    film_objs = Film.objects.all()
    showing_objs = Showing.objects.all()
    showing_dates = []
    for showing in showing_objs:
        if showing.showing_date not in showing_dates:
            showing_dates.append(showing.showing_date)

    showing_dates.sort()

    dates = ()
    for date in showing_dates:
        dates += (date, date),

    films_with_showings = []
    for showing in showing_objs:
        if showing.showing_date >= datetime.now().date():
            film = Film.objects.get(id=showing.film_id_id)

            if film not in films_with_showings:
                films_with_showings.append(film)

    if request.method == 'POST':
        # GET THE DATE FROM THE FORM
        print(request.POST)
        booking_date = request.POST['booking_date']

        #SET CLUB BOOKING SESSION VAR TO FALSE
        request.session['club_booking'] = False

        return redirect('booking_show_showings', booking_date=booking_date)
        #return booking_show_showings(request, date=booking_date)

    else:
        form = BookingDateForm(dates=dates)

    return render(request, 'home.html', {'films': films_with_showings, 'form': form})

#region : DASHBOARDS
def cinema_manager_dashboard(request):
    # created loginSection variable 
    current_user = request.user

    films = Film.objects.all()
    screens = Screen.objects.all()
    showings = Showing.objects.all()

    if request.method == 'POST':
        form = CinemaControlsForm(request.POST)
        if form.is_valid():
            cinema_controls = CinemaControls.objects.get(id=1)
            cinema_controls.club_discount = form.cleaned_data['club_discount']
            cinema_controls.general_discount = form.cleaned_data['general_discount']
            cinema_controls.covid_distancing = form.cleaned_data['covid_distancing']
            cinema_controls.save()
            messages.success(request, 'Cinema controls updated successfully!')
            
            # RESET THE REQUEST
            request.method = 'GET'
            return cinema_manager_dashboard(request)
    
    else:
        cinema_controls = CinemaControls.objects.get(id=1)
        club_discount = cinema_controls.club_discount
        general_discount = cinema_controls.general_discount
        covid_distancing = cinema_controls.covid_distancing
        form = CinemaControlsForm(initial={'club_discount': club_discount, 'general_discount': general_discount, 'covid_distancing': covid_distancing})

    if current_user.groups.filter(name='Cinema Manager').exists():
        return render(request, "dashboard/cinema_manager_dashboard.html", {"films": films, "screens": screens, "showings": showings, "form": form})
    
    else:
        return home(request)

def student_dashboard(request):
    current_user = request.user

    if current_user.groups.filter(name='Student').exists():
        
        if request.method == 'POST':
            form = AddCreditForm(request.POST)
            if form.is_valid():
                student = Student.objects.get(user=current_user)
                credit = form.cleaned_data['credit']
                #convert credit to value in pennies
                credit = credit * 100

                student.credit_num_of_pennies += credit
                student.save()
                messages.success(request, 'Credit added successfully!')
                
                # RESET THE REQUEST
                request.method = 'GET'

                return student_dashboard(request)
        
        else:
            form = AddCreditForm()
            student = Student.objects.get(user=current_user)
            current_credit = student.credit_num_of_pennies / 100

        return render(request, 'dashboard/student_dashboard.html', {'form': form, 'credit': current_credit})
                
    else:
        return home(request)

def club_rep_dashboard(request):
    current_user = request.user
    student = Student.objects.get(user=current_user)
    club = Club.objects.get(club_rep_id=student.id)

    if current_user.groups.filter(name='Club Representitive').exists():
        
        if request.method == 'POST':
            form = AddCreditForm(request.POST)
            if form.is_valid():
                credit = form.cleaned_data['credit']
                #convert credit to value in pennies
                credit = credit * 100

                club.club_credit_num_of_pennies += credit
                club.save()
                messages.success(request, 'Credit added successfully!')
                
                # RESET THE REQUEST
                request.method = 'GET'

                return club_rep_dashboard(request)
        
        else:
            form = AddCreditForm()
            current_credit = club.club_credit_num_of_pennies / 100

        return render(request, 'dashboard/club_rep_dashboard.html', {'form': form, 'club': club.club_name, 'credit': current_credit})
                
    else:
        return home(request)

def account_manager_dashboard(request):
    current_user = request.user

    if current_user.groups.filter(name='Account Manager').exists():
        return render(request, 'dashboard/accounts.html')
    
    else:
        return home(request)
#endregion

#region : AUTHENTICATION
def register_request(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            student_group.user_set.add(user)
            student = Student.objects.get_or_create(user=user)[0]

            login(request, user)
            messages.success(request, 'Account created successfully!')
            return render(request, 'home.html', {'user': user})
        
        messages.error(request, 'Error creating account!')

    else:
        form = SignUpForm()

    return render(request, 'accounts/register.html', {'form': form})

#LOGIN USING SESSIONS THAT EXPIRES IN 20 MINUTES
def login_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return render(request, 'home.html', {'user': user})
        
        else:
            messages.error(request, 'Error logging in!')
    
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_request(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return home(request)
#endregion

#region : FILMS CRUD
def create_film(request):
    # created loginSection variable 

    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':
            form = FilmForm(request.POST)
            if form.is_valid():
                film = form.save()
                film.save()
                messages.success(request, 'Film created successfully!')
                #RESET REQUEST
                request.method = 'GET'
                return cinema_manager_dashboard(request)
        
        else:
            form = FilmForm()

        return render(request, 'create_film.html', {'form': form})
    
    else:
        return home(request)

def get_film(request, id):
    #CHECK IF USER IS A CINEMA MANAGER
    film = Film.objects.get(id=id)
    return render(request, 'films/get_film.html', {'film': film})

def get_all_films(request):
    films = Film.objects.all()
    return render(request, 'films/get_films.html', {'films': films})

def update_film(request, id):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        film = Film.objects.get(id=id)

        if request.method == 'POST':
            form = FilmForm(request.POST, instance=film)
            if form.is_valid():
                film = form.save()
                film.save()
                messages.success(request, 'Film updated successfully!')
                return render(request, 'home.html', {'user': current_user})
        
        else:
            form = FilmForm(instance=film)

def delete_film(request):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':
            #form = DeleteFilmForm(request=request.POST, films=films)

            #GET FILM ID
            film_id = request.POST['film_id']

            #if form.is_valid():
                #GET THE ID FROM THE FORM
                #film_id = form.cleaned_data['film_id']

            if Showing.objects.filter(film_id=film_id).exists():
                messages.error(request, 'There are showings for this film! Cannot delete!')
                #RESET REQUEST
                request.method = 'GET'
                return cinema_manager_dashboard(request)

            else:
                film = Film.objects.get(id=film_id)
                film.delete()

            messages.success(request, 'Film Deleted successfully!')
            #RESET REQUEST
            request.method = 'GET'
            return cinema_manager_dashboard(request)
        
        else:
            film_objs = Film.objects.all()
            
            films = ()
            for film in film_objs:
                films += (film.id, film.title),

            form = DeleteFilmForm(films=films)

        return render(request, 'delete_film.html', {'form': form})
    
    else:
        return home(request)

#endregion

#region : SCREEN CRUD
def create_screen(request):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':
            form = ScreenForm(request.POST)
            if form.is_valid():
                screen = form.save()
                screen.save()

                screen.create_seats()

                messages.success(request, 'Screen created successfully!')

                #RESET REQUEST
                request.method = 'GET'
                return cinema_manager_dashboard(request)
        
        else:
            form = ScreenForm()

        return render(request, 'create_screen.html', {'form': form})
    
    else:
        return home(request)

def get_screen(request, id):
    screen = Screen.objects.get(id=id)
    return render(request, 'screens/get_screen.html', {'screen': screen})

def get_screens(request):
    screens = Screen.objects.all()
    return render(request, 'screens/get_screens.html', {'screens': screens})

def update_screen(request, id):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        screen = Screen.objects.get(id=id)

        if request.method == 'POST':
            form = ScreenForm(request.POST, instance=screen)
            if form.is_valid():
                screen = form.save()
                screen.save()

                screen.create_seats()

                messages.success(request, 'Screen updated successfully!')
                return render(request, 'home.html', {'user': current_user})
        
        else:
            form = ScreenForm(instance=screen)

def delete_screen(request):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':

            #GET Screen ID
            screen_id = request.POST['screen_id']

            if Showing.objects.filter(screen_id=screen_id).exists():
                messages.error(request, 'There are showings for this screen! Cannot Delete!')
                #RESET REQUEST
                request.method = 'GET'
                return cinema_manager_dashboard(request)

            else:
                screen = Screen.objects.get(id=screen_id)
                screen.delete()

            messages.success(request, 'Screen Deleted successfully!')
            #RESET REQUEST
            request.method = 'GET'
            return cinema_manager_dashboard(request)
        
        else:
            screen_objs = Screen.objects.all()
            
            screens = ()
            for screen in screen_objs:
                screens += (screen.id, screen.id),
                
            form = DeleteScreenForm(screens=screens)

        return render(request, 'delete_screen.html', {'form': form})
    
    else:
        return home(request)
#endregion

#region : SHOWING CRUD
def create_showing(request):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':
            form = ShowingForm(request.POST)
            if form.is_valid():
                showing = form.save()
                showing.save()
                messages.success(request, 'Showing created successfully!')
                #RESET REQUEST
                request.method = 'GET'
                return cinema_manager_dashboard(request)
        
        else:
            form = ShowingForm()

        return render(request, 'create_showing.html', {'form': form})

def get_showing(request, id):
    showing = Showing.objects.get(id=id)
    return render(request, 'showings/get_showing.html', {'showing': showing})

def get_showings(request):
    showings = Showing.objects.all()
    return render(request, 'showings/get_showings.html', {'showings': showings})

def update_showing(request, id):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        showing = Showing.objects.get(id=id)

        if request.method == 'POST':
            form = ShowingForm(request.POST, instance=showing)
            if form.is_valid():
                showing = form.save()
                showing.save()
                messages.success(request, 'Showing updated successfully!')
                return render(request, 'home.html', {'user': current_user})
        
        else:
            form = ShowingForm(instance=showing)

def delete_showing(request):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':

            #GET Showing ID
            showing_id = request.POST['showing_id']

            showing = Showing.objects.get(id=showing_id)
            showing.delete()

            messages.success(request, 'Showing Deleted successfully!')
            #RESET REQUEST
            request.method = 'GET'
            return cinema_manager_dashboard(request)
        
        else:
            showing_objs = Showing.objects.all()
            
            showings = ()
            for showing in showing_objs:
                showings += (showing.id, f"{showing.showing_date} - {showing.showing_time} - {showing.screen_id} - {showing.film_id}"),
                
            form = DeleteShowingForm(showings=showings)

        return render(request, 'delete_showing.html', {'form': form})
    
    else:
        return home(request)

#endregion

#region : CLUB CRUD
def create_club(request):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':
            form = ClubForm(request.POST)
            if form.is_valid():
                club = form.save()
                club.save()

                #ADD THE CLUB REP FROM THE FORM AND ADD TO THE CLUB REPRESENTIVE GROUP
                club_rep = User.objects.get(id=club.club_rep.user_id)
                club_rep.groups.add(Group.objects.get(name='Club Representitive'))

                messages.success(request, 'Club created successfully!')
                #RESET REQUEST
                request.method = 'GET'

                return cinema_manager_dashboard(request)
        
        else:
            form = ClubForm()

        return render(request, 'create_club.html', {'form': form})

def delete_club(request):
    current_user = request.user

    #CHECK IF USER IS A CINEMA MANAGER
    if current_user.groups.filter(name='Cinema Manager').exists():
        if request.method == 'POST':

            #GET Club ID
            club_id = request.POST['club_id']

            club = Club.objects.get(id=club_id)
            club.delete()

            messages.success(request, 'Club Deleted successfully!')

            #RESET REQUEST
            request.method = 'GET'

            return cinema_manager_dashboard(request)
        
        else:
            club_objs = Club.objects.all()
            
            clubs = ()
            for club in club_objs:
                clubs += (club.id, club.club_name),
                
            form = DeleteClubForm(clubs=clubs)

        return render(request, 'delete_club.html', {'form': form})
    
    else:
        return home(request)

#endregion

#region : BOOKING
def booking_show_showings(request, booking_date):
    showing_objs = Showing.objects.filter(showing_date=booking_date)

    showings = ()
    for showing in showing_objs:
        showings += (showing.id, f"{showing.showing_date} - {showing.showing_time} - Screen : {showing.screen_id} - Film : {showing.film_id}"),
    
    form = BookingShowingsForm(showings=showings)

    if request.method == 'POST':
        showing_id = request.POST['showing_id']

        return redirect('booking_show_seats', showing_id=showing_id)
        #return booking_show_seats(request, showing_id=showing_id)

    return render(request, 'booking/booking_showings.html', {'form': form})

def booking_show_seats(request, showing_id):
    showing = Showing.objects.get(id=showing_id)
    screen = showing.screen_id_id
    seats = Seat.objects.filter(screen_id_id=screen)
    tickets = Ticket.objects.all()
    ticketOrder = []

    discount = CinemaControls.objects.get(id=1).general_discount

    covid_distancing = CinemaControls.objects.get(id=1).covid_distancing

    #CHECK IF THE CLUB BOOKING SESSION VAR IS SET
    if 'club_booking' in request.session:
        club_booking = request.session['club_booking']

        if club_booking == True:
            tickets = Ticket.objects.filter(ticket_type='Student')
            discount = CinemaControls.objects.get(id=1).club_discount

    if request.method == 'POST':
        totalTicketQty = 0
        for ticket in tickets:
            ticketOrder.append({'ticketType': ticket.ticket_type, 'ticketPrice': str(ticket.ticket_price-discount), 'ticketQuantity': request.POST.get(ticket.ticket_type)})
            totalTicketQty += int(request.POST.get(ticket.ticket_type))

        orderTotal = 0
        for ticketType in ticketOrder:
            if ticketType['ticketQuantity'] != None:
                orderTotal += Decimal(ticketType['ticketPrice']) * int(ticketType['ticketQuantity'])

        #GET SELECTED SEATS
        selectedSeats = request.POST.getlist('seat')
        #CHECK IF THE SESSION CLUB BOOKING VARAIBLE IS True
        if 'club_booking' in request.session:
            club_booking = request.session['club_booking'] 
            if club_booking:
                if totalTicketQty < 10:
                    messages.error(request, 'You must book at least 10 tickets to make a club booking!')
                    
                    request.method = 'GET'
                    return booking_show_seats(request, showing_id=showing_id)

        if totalTicketQty > len(selectedSeats) or totalTicketQty < len(selectedSeats):
            messages.error(request, 'You have selected an unbalanced number of seats and tickets!')

            request.method = 'GET'
            return booking_show_seats(request, showing_id=showing_id)

        else:
            booking = {'showing': showing.id, 'ticketOrder': ticketOrder, 'selectedSeats': selectedSeats, 'orderTotal': str(orderTotal)}

            request.session['booking'] = booking
            return redirect('booking_confirm')

    return render(request, 'booking/booking_seats.html', {'seats': seats, 'tickets': tickets, 'discount': discount, 'covid_distancing': covid_distancing})

def booking_confirm(request):

    current_user = request.user

    booking = request.session['booking']

    showing_id = booking['showing']
    showing = Showing.objects.get(id=showing_id)
    film_id = showing.film_id_id
    film = Film.objects.get(id=film_id)

    ticketOrder = booking['ticketOrder']
    selectedSeats = booking['selectedSeats']

    student_ticket_quantity = 0
    adult_ticket_quantity = 0
    child_ticket_quantity = 0

    for ticket in ticketOrder:
        if ticket['ticketType'] == 'Student':
            student_ticket_quantity = ticket['ticketQuantity']
        elif ticket['ticketType'] == 'Adult':
            adult_ticket_quantity = ticket['ticketQuantity']
        elif ticket['ticketType'] == 'Child':
            child_ticket_quantity = ticket['ticketQuantity']
        
    seats = []
    for seat in selectedSeats:
        seats.append(Seat.objects.get(id=seat))

    orderTotal = booking['orderTotal']

    if request.method == "POST":

        #CREATE BOOKING
        booking = Booking()
        booking_date = datetime.now()
        booking.booking_date = booking_date
        booking.showing_id = showing

        #IF CURRENT USER IS A STUDENT
        if current_user.groups.filter(name='Student').exists():
            student = Student.objects.get(user_id=current_user.id)
            booking.student_id = student

        booking.student_ticket_quantity = student_ticket_quantity
        booking.adult_ticket_quantity = adult_ticket_quantity
        booking.child_ticket_quantity = child_ticket_quantity

        #CHECK IF THE SESSION CLUB BOOKING VARAIBLE IS True
        if 'club_booking' in request.session:
            club_booking = request.session['club_booking'] 

        if club_booking:
            booking.club_booking = True
            
            #GET CLUB REP ID 
            student = Student.objects.get(user_id=current_user.id)
            club = Club.objects.get(club_rep_id=student.id)
            booking.club_id = club
        else:
            booking.club_booking = False

        booking.total_price = orderTotal

        #IF USER ISN"T AUTHENTICATED GET PAYMENT INFO FROM THE BOKKINGPAYMENTFORM
        if not current_user.is_authenticated:
            form = BookingPaymentForm(request.POST)
            if form.is_valid():
                booking.name = form.cleaned_data['name']
                booking.email = form.cleaned_data['email']
                booking.card_num = form.cleaned_data['card_num']
                booking.card_exp_date = form.cleaned_data['exp_date']
                booking.card_cvv = form.cleaned_data['cvv']

        booking.save()
        
        for seat in seats:
            #CREAT BOOKING HAS SEATS
            booking_has_seat = BookingHasSeats()
            booking_has_seat.seat_id = seat
            booking_has_seat.booking_id = booking
            booking_has_seat.save()

            seat.booked = True
            seat.save()

        #IF USER IS STUDENT CHARGE THEIR CREDIT FOR THE BOOKING
        if current_user.groups.filter(name='Student').exists() and club_booking == False:
            #convert order total to pennies
            orderTotalPennies = Decimal(orderTotal) * 100
            student.credit_num_of_pennies -= orderTotalPennies
            student.save()

        if club_booking == True:
            
            orderTotalPennies = Decimal(orderTotal) * 100
            club.club_credit_num_of_pennies -= orderTotalPennies
            club.save()

        messages.success(request, 'Booking created successfully!')

        request.method = 'GET'
        return redirect('home')

    else:
        #RENDER THE PAYMENT FORM IF USER ISN"T AUTHENTICATED
        if not current_user.is_authenticated:
            form = BookingPaymentForm()
        else:
            form = None

    return render(request, 'booking/booking_confirm.html', {'selectedSeats': seats, 'showing': showing, 'ticketOrder': ticketOrder, 'orderTotal': orderTotal, 'film': film, 'form': form})

def club_booking_page(request):
    film_objs = Film.objects.all()
    showing_objs = Showing.objects.all()
    showing_dates = []
    for showing in showing_objs:
        if showing.showing_date not in showing_dates:
            showing_dates.append(showing.showing_date)

    showing_dates.sort()

    films_with_showings = []
    for showing in showing_objs:
        if showing.showing_date >= datetime.now().date():
            film = Film.objects.get(id=showing.film_id_id)
            if film not in films_with_showings:
                films_with_showings.append(film)

    dates = ()
    for date in showing_dates:
        dates += (date, date),
   
    if request.method == 'POST':
        # GET THE DATE FROM THE FORM
        booking_date = request.POST['booking_date']

        # SET SEESION VAR FOR CLUB BOOKING
        request.session['club_booking'] = True

        return redirect('booking_show_showings', booking_date=booking_date)

    else:
        form = BookingDateForm(dates=dates)

    return render(request, 'booking/club_booking_page.html', {'films': films_with_showings, 'form': form})

def bookings_list(request):
    #IF USER IS LOGGED IN
    if request.user.is_authenticated:
        #GET STUDENT OBJECT
        student = Student.objects.get(user_id=request.user.id)

        #GET BOOKINGS FOR THE STUDENT
        bookings = Booking.objects.filter(student_id=student)

        return render(request, 'booking/bookings_list.html', {'bookings': bookings})
    else:
        if request.method == 'POST':
            form = FindBookingForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']

                #GET BOOKINGS FOR THE name AND email
                bookings = Booking.objects.filter(name=name, email=email)

                print(bookings)

                return render(request, 'booking/bookings_list.html', {'bookings': bookings})

        else:
            #SHOW FIND BOOKINGS FORM
            form = FindBookingForm()
            return render(request, 'booking/bookings_list.html', {'form': form})

def get_daily_bookings(request):
    #check if the user is an account manager
    if request.user.groups.filter(name='Account Manager').exists():

        #GET BOOKINGS FOR THE SELECTED DATE
        if request.method == 'POST':
            form = DailyBookingsForm(request.POST)
            if form.is_valid():
                booking_date = form.cleaned_data['booking_date']
                bookings = Booking.objects.filter(booking_date=booking_date)

                total_revenue_for_day = 0
                for booking in bookings:
                    total_revenue_for_day += booking.total_price

                return render(request, 'finance/daily_bookings.html', {'bookings': bookings, 'total_revenue_for_day': total_revenue_for_day})

        else:
            form = DailyBookingsForm()
            return render(request, 'finance/daily_bookings.html', {'form': form})

    else:
        #RETURN HOME
        return redirect('home')

def get_monthly_report(request):
    #check if the user is an account manager
    if request.user.groups.filter(name='Account Manager').exists():

        #GET BOOKINGS FOR THE SELECTED MONTH
        if request.method == 'POST':
            form = MonthlyBookingsForm(request.POST)
            if form.is_valid():
                booking_month = form.cleaned_data['booking_month']

                #CONVERT MONTH NAME TO MONTH NUMBER
                #booking_month_num = datetime.strptime(booking_month, '%B').month

                #GET BOOKINGS WITH A BOOKING DATE WITHIN THE SELECETED MONTH
                bookings = Booking.objects.filter(booking_date__month=booking_month)

                total_revenue_for_month = 0
                for booking in bookings:
                    total_revenue_for_month += booking.total_price

                return render(request, 'finance/monthly_report.html', {'bookings': bookings, 'total_revenue_for_month': total_revenue_for_month})

        else:
            form = MonthlyBookingsForm()
            return render(request, 'finance/monthly_report.html', {'form': form})

    else:
        #RETURN HOME
        return redirect('home')

def booking_cancel(request, booking_id):
    # GET THE BOOKING OBJECT
    booking = Booking.objects.get(id=booking_id)

    # GET THE BOOKING SEATS
    seats = BookingHasSeats.objects.filter(booking_id=booking_id)

    for booking_seat in seats:
        # GET THE SEAT OBJECT
        seat = Seat.objects.get(id=booking_seat.seat_id_id)

        # SET THE SEAT AVAILABLE
        seat.booked = False
        seat.save()

        booking_seat.delete()

    if booking.club_booking:
        # GET THE CLUB OBJECT
        club = Club.objects.get(id=booking.club_id_id)

        # SET THE CLUB CREDIT NUMBER OF PENNIES
        total_price_pennies = booking.total_price * 100
        club.club_credit_num_of_pennies += total_price_pennies
        club.save()

    if booking.student_id and booking.club_booking != True:
        # GET THE STUDENT OBJECT
        student = Student.objects.get(id=booking.student_id_id)

        # SET THE STUDENT CREDIT NUMBER OF PENNIES
        total_price_pennies = booking.total_price * 100
        student.credit_num_of_pennies += total_price_pennies
        student.save()

    # DELETE THE BOOKING
    booking.delete()

    return redirect('bookings_list')
