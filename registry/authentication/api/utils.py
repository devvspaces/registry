import logging
# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')

from twilio.rest import Client

from django.http.response import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.core.mail import send_mail

def get_tokens_for_user(user):
	refresh = RefreshToken.for_user(user)
	return {
		'refresh': str(refresh),
		'access': str(refresh.access_token),
	}


def url_with_params(url, params):
	"""
	Url is a relative or full link,
	params is a dictionary of key/value pairs of the query parameters
	{id: 3, name: 'John doe'}
	"""
	# Add trailing backslash to url
	if not url.endswith('/'):
		url += '/'

	# Join the key/value pairs into a string 
	assiged = [f'{key}={value}' for key, value in params.items()]
	
	return url + '?' + '&'.join(assiged)


def send_email(email, subject, message, fail=True):
	print(message)
	val = send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=fail)
	return True if val else False



error_sets = {
	'ObjectNotFound': {
		'status': 404,
		'types': {
			'user-001': {
				'message': 'User does not exist.'
			}
		}
	},
	'TokenValidationError': {
		'status': 400,
		'types': {
			'user-001': {
				'message': 'Token passed is not valid.'
			},
			'user-002': {
				'message': 'User has already been verified.'
			},
			'user-003': {
				'message': 'Uidb64 value passed is not valid.'
			}
		}
	},
	'RequestError': {
		'status': 400,
		'types': {
			'req-001': {
				'message': 'ID value was not passed with the request.'
			},
			'req-003': {
				'message': 'Email was not passed with the request.'
			},
			'req-103': {
				'message': 'Email has already been used by another user.'
			},
			'req-004': {
				'message': 'Phone number not provided with request.'
			}
		}
	},
}


class CustomError:
	def __init__(self, status='', type = '', code = '', message='', request=None):
		self.type = type
		self.code = code
		self.status = status
		self.message = message
		self.path = ''
		
		if request is not None:
			self.path = request.META['PATH_INFO']

		# Get the error obj
		if type:
			obj = error_sets.get(type)

			if obj and code:
				main_err = obj['types'].get(code)
				self.status = obj.get('status', '')

				if main_err:
					self.message = main_err.get('message', '')

					main_status = main_err.get('status', '')
					if main_status:
						self.status = main_status
		
		if status:
			self.status = status

	def response(self):
		dict_form = {
			"status": self.status,
			"error": self.type,
			"code": self.code,
			"message": self.message,
			"path": self.path
		}
		return JsonResponse(data = dict_form, status=self.status)





# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

def send_sms(message, phone):
	try:
		message = client.messages \
					.create(
						body = message,
						from_='+1 864 732 4819',
						to = phone
					)
		logger.debug(f'sent sms message {phone} --- message: {message}')
		return True
	except Exception as e:
		err_logger.exception(e)
	return False