from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing>", views.listing, name="listing"),
    path("bid", views.bid, name="bid"),
    path("comment", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("addtowatchlist/<int:item_id>", views.add_to_watchlist, name="add_to"),
    path("removefrom/<int:item_id>", views.remove_from, name="remove"),
    path("categories", views.categories, name="categories"),
    path("success", views.success, name="success"),
    path("addListing", views.addListing, name="add_listing"),
    path("user_listings", views.user_listings, name="user_listings"),
    path("close_listing/<int:listing_id>", views.close_listing, name="close_listing"),
]
