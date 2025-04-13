import uuid
from uuid import UUID
from django.utils.timezone import now
from user.models import UserOpenAccount, UserActivityLog
from user_agents import parse

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Get user or generate guest ID
        if request.user.is_authenticated:
            # For authenticated users, link to the existing User model (no new UserOpenAccount)
            user_id = str(request.user.id)  # Use real user ID
            user_account, created = UserOpenAccount.objects.get_or_create(
                id=user_id,  # Associate with the User's ID directly
                defaults={
                    "ip_address": self.get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "device": "Unknown",  # You can leave this or determine from headers
                    "browser": "Unknown",  # Same as above
                    "os": "Unknown",  # Same as above
                    "first_seen_at": now(),
                    "last_seen_at": now(),
                    "status": "active",
                }
            )
        else:
            # For guests, generate a new guest ID
            user_id = request.session.get("guest_id")
            if not user_id:
                user_id = str(uuid.uuid4())  # Generate unique guest ID
                request.session["guest_id"] = user_id
            
            # Create a UserOpenAccount for guest users
            user_account, created = UserOpenAccount.objects.get_or_create(
                id=user_id,
                defaults={
                    "ip_address": self.get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "device": "Unknown",  # You can leave this or determine from headers
                    "browser": "Unknown",  # Same as above
                    "os": "Unknown",  # Same as above
                    "first_seen_at": now(),
                    "last_seen_at": now(),
                    "status": "active",
                }
            )

        if not created:
            # If it's an existing entry, just update `last_seen_at`
            user_account.last_seen_at = now()
            user_account.save(update_fields=["last_seen_at"])

        # Store the URL visit log
        UserActivityLog.objects.create(user=user_account, url=request.path, timestamp=now())

        return response

    def get_client_ip(self, request):
        """Extract client IP address."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")

