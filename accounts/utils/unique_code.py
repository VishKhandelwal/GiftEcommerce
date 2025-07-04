import uuid
from datetime import timedelta
from django.utils import timezone
from accounts.models import UniqueCode

def generate_unique_code():
    """Generates a random 12-character alphanumeric code."""
    return f"UNQ-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"

def assign_unique_code_to_email(email):
    """
    Assigns an unused unique code to the given email.
    Handles reuse if expired and avoids duplication.
    """
    now = timezone.now()

    # Step 1: Check if existing assigned code is still valid
    existing_code = UniqueCode.objects.filter(
        assigned_to=email,
        is_used=False
    ).first()

    if existing_code and existing_code.assigned_time:
        if now < existing_code.assigned_time + timedelta(days=14):
            return existing_code

        # Expired — mark used
        existing_code.is_used = True
        existing_code.save()

    # Step 2: Reuse expired codes for the same email (optional fallback)
    reusable_code = UniqueCode.objects.filter(
        assigned_to=email,
        is_used=False,
        assigned_time__lt=now - timedelta(days=14)
    ).first()
    if reusable_code:
        return reusable_code

    # Step 3: Assign new code
    new_code = UniqueCode.objects.filter(
        assigned_to__isnull=True,
        is_used=False
    ).first()

    if new_code:
        new_code.assigned_to = email
        new_code.assigned_time = now
        new_code.save()
        return new_code

    # Step 4: If no unused code exists, create a new one (optional)
    generated_code = generate_unique_code()
    return UniqueCode.objects.create(
        code=generated_code,
        assigned_to=email,
        assigned_time=now
    )
