from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from decimal import *

from .models import User, Listing, Bid, Comment
from .forms import ListingForm
from .decorators import Unauthenticated_user, Authenticated_user

# dictionary variable to keep track of individual's watchlist
watch_list = dict()

def index(request):
    listings = []
    items = Listing.objects.filter(status="Pending")
    for item in items:
        try:
            bid = Bid.objects.get(listing=item)
        except:
            bid = None
        listings.append({
            'listing': item,
            'bid': bid,
        })
    context = {
        'listings': listings,
    }
    return render(request, "auctions/index.html", context)

@Unauthenticated_user
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@Authenticated_user
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


@Unauthenticated_user
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")

@Authenticated_user
def listing(request, listing):
    item = Listing.objects.get(pk=listing)
    old_bid = Bid.objects.filter(listing=item)
    if item.status == 'Closed':
        try: # fails if no bid was placed on the item when it was closed
            bid = old_bid[0]
            if bid.user == request.user:
                context = {
                    'listing': item,
                    'bid': bid,
                }
                return render(request, 'auctions/success.html', context)
        except:
            return render(request, 'auctions/closed.html') # return after try fails
        return render(request, 'auctions/closed.html') # return after try passes and the if statement fails
    comments = Comment.objects.filter(listing=item)
    if old_bid.count() is 1:
        default_bid = old_bid[0].highest_bid + 10
    else:
        default_bid = item.initial + 10
    try:
        bid_info = Bid.objects.get(listing=item)
    except:
        bid_info = None;
    context = {
        'listing': item,
        'bid': bid_info,
        'comments': comments,
        'default_bid': default_bid,
    }
    return render(request, "auctions/listing.html", context)

@Authenticated_user
def bid(request):
    if request.method == "POST":
        new_bid = request.POST["bid"]
        item_id = request.POST["list_id"]

        item = Listing.objects.get(pk=item_id)
        old_bid = Bid.objects.filter(listing=item)

        if old_bid.count() < 1:
            bid = Bid(user=request.user, listing=item, highest_bid=new_bid)
            bid.save()
            messages.success(request, 'Bid Placed Successfully!', fail_silently=True)
        elif Decimal(new_bid) < old_bid[0].highest_bid:
            messages.warning(request, 'The bid you placed was lower than needed.', fail_silently=True)
        elif Decimal(new_bid) == old_bid[0].highest_bid:
            messages.warning(request, 'The bid you placed was the same as the current bid', fail_silently=True)
        else:
            old_bid = Bid.objects.get(listing=item)
            old_bid.highest_bid = new_bid
            old_bid.user = request.user
            old_bid.save()
            messages.success(request, 'Bid Placed Successfully!', fail_silently=True)
    return redirect("auctions:listing", item_id)

@Authenticated_user
def comment(request):
    if request.method == "POST":
        content = request.POST["content"]
        item_id = request.POST["list_id"]
        item = Listing.objects.get(pk=item_id)
        newComment = Comment(user=request.user, comment=content, listing=item)
        newComment.save()
        return redirect("auctions:listing", item_id)
    return redirect("auctions:index")

@Authenticated_user
def watchlist(request):
    if request.user not in watch_list or watch_list[request.user] == []:
        context = {
            'message': "Nothing in your watchlist",
        }
        return render(request, "auctions/watchlist.html", context)
    listings = []
    for item_id in watch_list[request.user]:
        item = Listing.objects.get(pk=item_id)
        try:
            bid = Bid.objects.get(listing=item)
        except:
            bid = None
        listings.append({
            'listing': item,
            'bid': bid,
        })
    context = {
        'listings': listings,
    }
    return render(request, "auctions/watchlist.html", context)

@Authenticated_user
def add_to_watchlist(request, item_id):
    if request.user not in watch_list:
        watch_list[request.user] = []
        watch_list[request.user].append(item_id)
        messages.success(request, 'Successfully added item to your WatchList.', fail_silently=True)
    elif item_id in watch_list[request.user]:
        messages.warning(request, 'Item already present in your WatchList.', fail_silently=True)
    else:
        watch_list[request.user].append(item_id)
        messages.success(request, 'Successfully added item to your WatchList.', fail_silently=True)
    return redirect("auctions:index")

@Authenticated_user
def remove_from(request, item_id):
    if request.user not in watch_list:
        messages.warning(request, 'Cannot remove from empty WatchList.', fail_silently=True)
    elif item_id in watch_list[request.user]:
        watch_list[request.user].remove(item_id)
        messages.success(request, 'Successfully removed item from your WatchList.', fail_silently=True)
    else:
        messages.warning(request, 'Item not in your WatchList.', fail_silently=True)
    return redirect("auctions:index")

def categories(request):
    category = dict()
    listings = Listing.objects.filter(status="Pending")
    for item in listings:
        try:
            bid = Bid.objects.get(listing=item)
        except:
            bid = None
        if item.category not in category:
            category[item.category] = []
        category[item.category].append({
            'listing': item,
            'bid': bid,
        })
    context = {
        'category_list': category,
    }
    return render(request, "auctions/category.html", context)

@Authenticated_user
def success(request):
    return render(request, "auctions/success.html")

@Authenticated_user
def addListing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES or None)

        if form.is_valid():
            newListing = form.save(commit=False)
            newListing.user = request.user
            newListing.save()
            messages.success(request, 'Successfully created your listing.', fail_silently=True)
        else:
            messages.error(request, 'Invalid Listing!', fail_silently=True)
            return redirect("auctions:add_listing")
        return redirect("auctions:index")
    form = ListingForm()
    context = {
        'form': form,
    }
    return render(request, "auctions/addListing.html", context)

@Authenticated_user
def user_listings(request):
    listings = []
    current_user_listings = Listing.objects.filter(user=request.user, status='Pending')
    for item in current_user_listings:
        try:
            bid = Bid.objects.get(listing=item)
        except:
            bid = None
        listings.append({
            'listing': item,
            'bid': bid,
        })
    context = {
        'listings': listings,
    }
    return render(request, "auctions/userlistings.html", context)

@Authenticated_user
def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if listing.user == request.user:
        listing.status = 'Closed'
        listing.save()
        messages.success(request, 'Listing successfully closed.', fail_silently=True)
    else:
        messages.warning(request, 'Unable to close listing! Authentication error.', fail_silently=True)
    return redirect("auctions:user_listings")
