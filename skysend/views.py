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
            # send email
            send_mail(
                subject=f"New message from {request_site_domain}",
                message="",
                html_message=table,
                from_email=email,
                recipient_list=([RECEIVER_EMAIL]),
                fail_silently=False,
            )

            # send email
            if settings.SEC_API:
                # send post request to SEC-API
                import requests

                # make form data mutable
                form_data = form_data.copy()

                # send post request to SEC-API
                response = requests.post(settings.SEC_API, data=form_data)
                if response.status_code != 200:
                    return JsonResponse(
                        {
                            "message": "An error occurred while sending email",
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
