from allauth.socialaccount.models import SocialAccount


def get_user_profile_image(user):
    social_account = SocialAccount.objects.filter(user=user, provider='kakao').first()
    if social_account:
        return social_account.extra_data.get('properties', {}).get('profile_image', '')
    return None