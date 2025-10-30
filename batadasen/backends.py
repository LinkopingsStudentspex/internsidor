from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class BatadasenOIDCBackend(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        claim_username = claims.get("preferred_username")
        return self.UserModel.objects.filter(username=claim_username)
