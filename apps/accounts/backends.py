from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailOrPhoneModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None
            
        # Phone normalization logic
        phone_variants = [username]
        
        # If starts with 01, add 88 and +88 prefix variants
        if username.startswith('01'):
            phone_variants.append(f"88{username}")
            phone_variants.append(f"+88{username}")
        # If starts with 8801, strip 88 or add +
        elif username.startswith('8801'):
            phone_variants.append(username[2:]) # 01...
            phone_variants.append(f"+{username}")
        # If starts with +8801
        elif username.startswith('+8801'):
            phone_variants.append(username[3:]) # 01...
            phone_variants.append(username[1:]) # 8801...

        try:
            # Check user by email or any phone format variant
            user = User.objects.get(
                Q(email=username) | Q(phone_number__in=phone_variants)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Pick first if duplicate exists
            user = User.objects.filter(
                Q(email=username) | Q(phone_number__in=phone_variants)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None