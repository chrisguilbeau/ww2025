from collections   import defaultdict
from config        import HA_ACCOUNT, HA_KEY
from datetime      import datetime
from datetime      import timedelta
from lib.framework import returnAs
from lib.model     import cacheOnDiskWithPickle

import requests

@cacheOnDiskWithPickle('hostaway_bookings.pkl')
def get_hostaway_token():
    """
    Obtains an access token from Hostaway using the Client Credentials Grant.

    Assumptions:
    - HA_CLIENT_ID and HA_CLIENT_SECRET are available as configuration variables.
    - The scope is 'general' and grant_type is 'client_credentials'.
    """
    url = "https://api.hostaway.com/v1/accessTokens"
    headers = {
        "Cache-control": "no-cache",
        "Content-type": "application/x-www-form-urlencoded"
    }

    # Prepare the payload as per Hostaway API documentation.
    payload = {
        "grant_type": "client_credentials",
        "client_id": HA_ACCOUNT,         # Your Hostaway account ID
        "client_secret": HA_KEY,  # Your Hostaway client secret
        "scope": "general"
    }

    # Make the POST request to obtain the access token.
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()  # Raises an exception for any HTTP errors

    # Parse the JSON response.
    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        raise ValueError("Access token not found in response: " + str(data))

    return access_token

def get_hostaway_listings(token):
    """
    Retrieves a list of all active listing IDs from Hostaway.

    Returns:
        list: A list of listing IDs.
    """
    url = "https://api.hostaway.com/v1/listings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Cache-control": "no-cache"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('result')

def get_hostaway_calendar(token, listing_id, days):
    """
    Retrieves the calendar for the next days for a given listing from Hostaway.

    Parameters:
    - listing_id (int): The ID of the listing to retrieve the calendar for.

    Returns:
    - A list of calendar day objects (as returned by the Hostaway API).
    """

    # Construct the URL using the provided listing_id
    url = f"https://api.hostaway.com/v1/listings/{listing_id}/calendar"

    # Prepare headers with the obtained access token.
    headers = {
        "Authorization": f"Bearer {token}",
        "Cache-control": "no-cache"
    }

    # Calculate today's date and the date days from now
    now = datetime.now()
    today = now.date()
    endDate = (now + timedelta(days=days)).date()

    # Format the dates as required (YYYY-MM-DD)
    params = {
        "startDate": today.isoformat(),
        "endDate": endDate.isoformat(),
        "includeResources": 1
    }

    # Make the GET request to fetch the calendar
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json().get("result")
    for c in result:
        for r in c['reservations']:
            r['listingId'] = listing_id
    return result

# example reservation object
# {
# 'adults': None,
# 'airbnbCancellationPolicy': None,
# 'airbnbExpectedPayoutAmount': None,
# 'airbnbListingBasePrice': None,
# 'airbnbListingCancellationHostFee': None,
# 'airbnbListingCancellationPayout': None,
# 'airbnbListingCleaningFee': None,
# 'airbnbListingHostFee': None,
# 'airbnbListingSecurityPrice': None,
# 'airbnbOccupancyTaxAmountPaidToHost': None,
# 'airbnbTotalPaidAmount': None,
# 'airbnbTransientOccupancyTaxPaidAmount': None,
# 'arrivalDate': '2025-03-24',
# 'assigneeUserId': None,
# 'braintreeGuestId': None,
# 'braintreeMessage': None,
# 'cancellationDate': None,
# 'cancellationPolicyId': 201185,
# 'cancelledBy': None,
# 'ccExpirationMonth': None,
# 'ccExpirationYear': None,
# 'ccName': None,
# 'ccNumber': None,
# 'ccNumberEndingDigits': None,
# 'channelCommissionAmount': None,
# 'channelId': 2000,
# 'channelName': 'direct',
# 'channelReservationId': '70924-186944-2000-2580655414',
# 'checkInTime': 16,
# 'checkOutTime': 10,
# 'children': None,
# 'claimStatus': None,
# 'cleaningFee': None,
# 'comment': None,
# 'confirmationCode': None,
# 'currency': 'USD',
# 'customFieldValues': [],
# 'customerIcalId': None,
# 'customerIcalName': None,
# 'customerUserId': None,
# 'cvc': None,
# 'departureDate': '2025-03-26',
# 'doorCode': '5306',
# 'doorCodeInstruction': None,
# 'doorCodeVendor': 'Hostaway',
# 'externalPropertyId': None,
# 'externalUnitId': None,
# 'financeField': [],
# 'guestAddress': None,
# 'guestAuthHash': '7d6672bd3a6e790d1631cd71ff946ebe644a83f0c0ba7685a2019626f86e7177',
# 'guestCity': None,
# 'guestCountry': None,
# 'guestEmail': 'rachelbaird9@gmail.com',
# 'guestExternalAccountId': None,
# 'guestFirstName': 'Rachel',
# 'guestLastName': None,
# 'guestLocale': None,
# 'guestName': 'Rachel Elion Baird',
# 'guestNote': None,
# 'guestPaymentCardIsVirtual': None,
# 'guestPicture': None,
# 'guestPortalRevampUrl': None,
# 'guestPortalUrl': 'https://dashboard.hostaway.com/v3/guestPortal/reservations/36696352/7d6672bd3a6e790d1631cd71ff946ebe644a83f0c0ba7685a2019626f86e7177',
# 'guestRecommendations': 0,
# 'guestTrips': 0,
# 'guestWork': None,
# 'guestZipCode': None,
# 'hostNote': None,
# 'hostProxyEmail': None,
# 'hostawayCommissionAmount': None,
# 'hostawayReservationId': '36696352',
# 'id': 36696352,
# 'infants': None,
# 'insertedOn': '2025-01-17 14:27:03',
# 'insurancePolicyId': None,
# 'insuranceStatus': 'not_eligible',
# 'isArchived': 0,
# 'isDatesUnspecified': 0,
# 'isGuestIdentityVerified': 0,
# 'isGuestVerifiedByEmail': 0,
# 'isGuestVerifiedByFacebook': 0,
# 'isGuestVerifiedByGovernmentId': 0,
# 'isGuestVerifiedByPhone': 0,
# 'isGuestVerifiedByReviews': 0,
# 'isGuestVerifiedByWorkEmail': 0,
# 'isInitial': 0,
# 'isInstantBooked': 0,
# 'isManuallyChecked': 0,
# 'isPaid': None,
# 'isPinned': 0,
# 'isProcessed': 1,
# 'isStarred': 0,
# 'latestActivityOn': '2025-01-17 14:27:10',
# 'listingCustomFields': None,
# 'listingMapId': 186944,
# 'listingName': '',
# 'localeForMessaging': None,
# 'localeForMessagingSource': None,
# 'nights': 2,
# 'numberOfGuests': 2,
# 'originalChannel': None,
# 'paymentStatus': 'Unpaid',
# 'pendingExpireDate': None,
# 'pets': None,
# 'phone': '+18029899992',
# 'previousArrivalDate': None,
# 'previousDepartureDate': None,
# 'remainingBalance': None,
# 'rentalAgreementFileUrl': None,
# 'reservationAgreement': 'not_required',
# 'reservationCouponId': None,
# 'reservationDate': '2025-01-17 14:27:03',
# 'reservationFees': [],
# 'reservationId': '70924-186944-2000-2580655414',
# 'reservationUnit': [],
# 'securityDepositFee': 0,
# 'source': None,
# 'status': 'new',
# 'stripeGuestId': None,
# 'stripeMessage': None,
# 'taxAmount': None,
# 'totalPrice': 80.66,
# 'updatedOn': '2025-02-15 22:18:09'}

@returnAs(list)
def getHostawayBookings():
    token = get_hostaway_token()
    days = 30
    calendars = []
    listings = get_hostaway_listings(token)
    listingIds = [listing['id'] for listing in listings]
    listingNames = {listing['id']: listing['name'] for listing in listings}
    reservations = defaultdict(list)
    for listingId in listingIds:
        calendars.append(get_hostaway_calendar(token, listingId, days))
    for calendar in calendars:
        for day in calendar:
            rs = day['reservations']
            if rs:
                reservations[day['date']].extend(rs)
    for date, rs in reservations.items():
        dt = datetime.strptime(date, "%Y-%m-%d").date()
        for r in rs:
            listingId = r.get('listingId')
            guestName = r.get('guestName')
            yield dt, f"{listingNames[listingId]}: {guestName}"
