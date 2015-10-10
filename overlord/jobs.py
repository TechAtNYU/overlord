
from flask import Flask
from flask import request, redirect
from datetime import datetime
import stripe
import os
app = Flask(__name__)

#$/week
fixed_rate = 100.0
#sg = sendgrid.SendGridClient(os.environ['TNYU_SendGrid_Username'], os.environ['TNYU_SendGrid_API'])

@app.route("/jobs", methods=['POST'])
def jobs():
	token = request.form['stripeToken']
	stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2" # os.environ['TNYU_Stripe_API']

	charge_amount = round(get_charge(request.form['expiration']), 2)
	charge_amount_cents = int(charge_amount * 100.0)

	try:
			charge = stripe.Charge.create(
					amount=charge_amount_cents, 
					currency="usd",
					source=token,
					description="Tech@NYU job listing"
			)
		
			body = build_body(request.form, charge_amount, charge.id)
			print(body)

	except stripe.error.CardError, e:
			pass

	return redirect('http://jobsatnyu.com/')


def get_charge(expiration_datetime):
	expiration = datetime.strptime(expiration_datetime, '%m/%d/%Y %I:%M %p')
	today = datetime.now()

	dt = expiration.date() - today.date()
	num_weeks = dt.days / 7.0
	return num_weeks * fixed_rate

def build_body(listing, amount_paid, charge_id):
	body = """<html>
							<body>
								Hi,<br />
								
								<p> A wild job listing has appeared. Head over to our <a href="https://api.tnyu.org/" target="_blank">pok&egravedex</a> to record this discovery. </p>

								Position name: :position-name <br />
								<br />
						
								Description: <br />
								<p> :description </p>
								Category: :category <br />
								Position level: :position-level <br />
								Expires At: :expiration <br />
						
								Company Name: :employer <br />
								Company URL: :url <br />
								Application Email: :app-email <br />
								Application URL: :app-url <br />
						
								Amount Paid: :paid <br />
								Stripe chargeId: :charge-id <br />
						
								Thanks,<br />
								The Job Board
							</body>
						</html>"""

	for key in listing.keys():
		body = body.replace(":" + key, listing[key])

	body = (body.replace(":paid", str(amount_paid))).replace(":charge-id", str(charge_id))
	return body

if __name__ == "__main__":
		app.run()
