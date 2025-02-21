import uuid
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
            user_id = str(request.user.id)  # Use real user ID
        else:
            user_id = request.session.get("guest_id")
            if not user_id:
                user_id = str(uuid.uuid4())  # Generate unique guest ID
                request.session["guest_id"] = user_id

        ip_address = self.get_client_ip(request)
        user_agent_string = request.META.get("HTTP_USER_AGENT", "")
        user_agent = parse(user_agent_string)

        device = user_agent.device.family or "Unknown"
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}" if user_agent.browser.family else "Unknown"
        os = f"{user_agent.os.family} {user_agent.os.version_string}" if user_agent.os.family else "Unknown"

        # Store user account details
        user_account, created = UserOpenAccount.objects.get_or_create(
            id=user_id,
            defaults={
                "ip_address": ip_address,
                "user_agent": user_agent_string,
                "device": device,
                "browser": browser,
                "os": os,
                "first_seen_at": now(),
                "last_seen_at": now(),
                "status": "active",
            },
        )

        if not created:
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
