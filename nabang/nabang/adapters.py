from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, sociallogin):
        # 원하는 사용자 정의 로직을 추가하여 앱을 가져옵니다.
        app = super().get_app(request, sociallogin)
        # 추가적인 로직이나 수정이 필요하다면 여기에 작성합니다.
        return app