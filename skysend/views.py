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

        # get all form data and put it in a table with key value pairs
        table = "<table>"
        for key, value in form_data.items():
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
                recipient_list=(
                    [RECEIVER_EMAIL, sec_email] if sec_email else [RECEIVER_EMAIL]
                ),
                fail_silently=False,
            )
            return JsonResponse(
                {"message": "Email sent successfully", "success": True}, status=200
            )
        except Exception as e:
            logging.error(e)
            return JsonResponse(
                {"message": "An error occurred", "success": False}, status=500
            )
    return JsonResponse({"message": "Method not allowed", "success": False}, status=405)
