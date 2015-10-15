
from flask import Flask
from flask import request, redirect
from datetime import datetime
from reminder import sendEmail
from decimal import Decimal
import sendgrid
import stripe
import os
app = Flask(__name__)

#$/week
fixed_rate = 100.0
#sg = sendgrid.SendGridClient('techatnyu', os.environ['TNYU_send_grid_client_API'])

@app.route("/jobs", methods=['POST'])
def jobs():
	token = request.form['stripeToken']
	
	#To test, use 'sk_test_BQokikJOvBiI2HlWgH4olfQ2' with card number 4242-4242-4242-4242
	stripe.api_key = os.environ['TNYU_Stripe_API']
	charge_amount = float(Decimal(request.form['charge']))
	print charge_amount
	charge_amount_cents = int(charge_amount * 100.0)
	print(charge_amount_cents)

	try:
		charge = stripe.Charge.create(
			amount=charge_amount_cents, 
			currency="usd",
			source=token,
			description="Tech@NYU job listing"
		)

		body = build_body(request.form, charge_amount, charge.id)
		company_name = request.form["employer"]
		subject = "New job listing from " + company_name
		sendEmail("pjo256@nyu.edu", subject, body)


	except stripe.error.CardError, e:
		pass

	return redirect('http://jobsatnyu.com/')


def get_charge(expiration_datetime):
	expiration = datetime.strptime(expiration_datetime, '%m/%d/%Y')
	today = datetime.now()

	dt = expiration.date() - today.date()
	num_weeks = dt.days / 7.0
	return num_weeks * fixed_rate

def build_body(listing, amount_paid, charge_id):
	body = """	Hi,

	A wild job listing has appeared. Head over to our pokedex (https://api.tnyu.org/) to record this discovery.

	Position name: :position-name

	Description:

	:description

	Category: :category
	Position level: :position-level
	Expires At: :expiration

	Company Name: :employer
	Company URL: :url
	Application Email: :app-email
	Application URL: :app-url

	Amount Paid: $:paid
	Stripe chargeId: :token-id

	Thanks,
	The Job Board"""

	for key in listing.keys():
		body = body.replace(":" + key, listing[key])

	body = (body.replace(":paid", str(amount_paid))).replace(":token-id", str(charge_id))
	return body

if __name__ == "__main__":
		app.run()
