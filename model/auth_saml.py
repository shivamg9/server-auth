# -*- encoding: utf-8 -*-
from openerp import models
from openerp import api
from openerp import fields
import lasso
import simplejson


class auth_saml_provider(models.Model):
    """Class defining the configuration values of an Saml2 provider"""

    _name = 'auth.saml.provider'
    _description = 'SAML2 provider'
    _order = 'name'

    @api.multi
    def _get_lasso_for_provider(self):
        """internal helper to get a configured lasso.Login object for the
        given provider id"""

        # user is not connected yet... so use SUPERUSER_ID

        # TODO: we should cache those results somewhere because it is
        # really costly to always recreate a login variable from buffers
        server = lasso.Server.newFromBuffers(
            self.sp_metadata,
            self.sp_pkey
        )
        server.addProviderFromBuffer(
            lasso.PROVIDER_ROLE_IDP,
            self.idp_metadata
        )
        return lasso.Login(server)

    @api.multi
    def _get_auth_request(self, state):
        """build an authentication request and give it back to our client
        WARNING: this method cannot be used for multiple ids
        """
        login = self._get_lasso_for_provider()

        # ! -- this is the part that MUST be performed on each call and
        # cannot be cached
        login.initAuthnRequest()
        login.request.nameIdPolicy.format = None
        login.request.nameIdPolicy.allowCreate = True
        login.msgRelayState = simplejson.dumps(state)
        login.buildAuthnRequestMsg()

        # msgUrl is a fully encoded url ready for redirect use
        # obtained after the buildAuthnRequestMsg() call
        return login.msgUrl

    # Name of the OAuth2 entity, authentic, xcg...
    name = fields.Char('Provider name')
    idp_metadata = fields.Text('IDP Configuration')
    sp_metadata = fields.Text('SP Configuration')
    sp_pkey = fields.Text(
        'Private key of our service provider (this openerpserver)'
    )
    enabled = fields.Boolean('Enabled', default=False)
    sequence = fields.Integer('Sequence')
    css_class = fields.Char('CSS Class')
    body = fields.Char('Body')
