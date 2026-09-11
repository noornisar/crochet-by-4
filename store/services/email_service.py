import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger('store')


def _sanitize_error(error_str: str) -> str:
    """Remove any sensitive credentials if they happen to appear in error strings."""
    password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
    if password and password in error_str:
        error_str = error_str.replace(password, '******')
    return error_str


def _send_email_with_retry(email_msg: EmailMultiAlternatives, max_retries: int = 2) -> tuple[bool, str | None]:
    """
    Sends an EmailMultiAlternatives message with automatic retry upon connection errors.
    Returns (success: bool, error_message: str | None).
    """
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            email_msg.connection = None  # Ensure fresh connection
            email_msg.send(fail_silently=False)
            return True, None
        except Exception as e:
            last_error = _sanitize_error(str(e))
            logger.warning(f"Attempt {attempt}/{max_retries} failed sending email to {email_msg.to}: {last_error}")
    return False, last_error


def send_test_email(recipient_email: str) -> tuple[bool, str | None]:
    """
    Sends a simple test email to verify Gmail SMTP configuration.
    Returns (success: bool, error_message: str | None).
    """
    subject = "Test Email - Crochet Store"
    body = "This is a test email from my Crochet Store Django website. SMTP configuration is working correctly."
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=from_email,
            to=[recipient_email],
        )
        return _send_email_with_retry(email)
    except Exception as e:
        safe_error = _sanitize_error(str(e))
        logger.error(f"Failed to send test email to {recipient_email}: {safe_error}")
        return False, safe_error


def send_welcome_email(user, site_domain: str = 'localhost:8000') -> tuple[bool, str | None]:
    """
    Sends a welcome email to newly registered customer.
    Returns (success: bool, error_message: str | None).
    """
    if not user.email:
        logger.warning(f"User {user.username} has no email address. Welcome email skipped.")
        return False, "User has no email address."

    subject = "Welcome to Crochet Store"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
    store_name = getattr(settings, 'STORE_NAME', 'Crochet Store')

    context = {
        'user': user,
        'username': user.username,
        'customer_name': user.get_full_name() or user.username,
        'store_name': store_name,
        'site_domain': site_domain,
    }

    try:
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = render_to_string('emails/welcome_email.txt', context)
    except Exception:
        text_content = f"Hello {context['customer_name']},\n\nWelcome to {store_name}! We are thrilled to have you in our crochet family.\n\nVisit us: http://{site_domain}/\n\nWarm regards,\n{store_name}"
        html_content = f"<p>Hello <strong>{context['customer_name']}</strong>,</p><p>Welcome to <strong>{store_name}</strong>! We are thrilled to have you in our crochet family.</p><p><a href='http://{site_domain}/'>Visit Crochet Store</a></p>"

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        success, error = _send_email_with_retry(email)
        if success:
            logger.info(f"Welcome email sent successfully to {user.email}")
            return True, None
        else:
            logger.error(f"Failed to send welcome email to {user.email}: {error}")
            return False, error
    except Exception as e:
        safe_error = _sanitize_error(str(e))
        logger.error(f"Failed to send welcome email to {user.email}: {safe_error}")
        return False, safe_error


def send_order_confirmation_email(order, site_domain: str = '127.0.0.1:8000') -> tuple[bool, str | None]:
    """
    Sends an order confirmation email to the customer upon successful checkout,
    and also sends an immediate New Order Alert to the store owner / admin.
    Returns (success: bool, error_message: str | None).
    """
    customer_email = (order.email or '').strip()
    if not customer_email:
        logger.warning(f"Order #{order.order_number} has no customer email address. Skipping email.")
        return False, "Order has no customer email address."

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', 'noornisar96@gmail.com')
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'noornisar96@gmail.com')
    store_name = getattr(settings, 'STORE_NAME', 'Crochet Store')

    # Ensure site_domain does not use placeholder example.com
    if not site_domain or site_domain == 'example.com':
        site_domain = '127.0.0.1:8000'

    context = {
        'order': order,
        'items': order.items.all(),
        'customer_name': order.full_name or 'Valued Customer',
        'customer_email': customer_email,
        'order_number': order.order_number,
        'order_date': order.created,
        'subtotal': order.subtotal,
        'shipping_cost': order.shipping_cost,
        'tax': order.tax,
        'total_price': order.total_price,
        'store_name': store_name,
        'site_domain': site_domain,
    }

    # Prepare Customer Email Content
    try:
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = render_to_string('emails/order_confirmation.txt', context)
    except Exception as e:
        logger.warning(f"Error rendering order confirmation template: {e}. Falling back to default text.")
        text_content = f"Thank you for your order, {order.full_name}!\n\nOrder ID: {order.order_number}\nTotal: Rs {order.total_price}\n\nWe appreciate your purchase at {store_name}!"
        html_content = f"<p>Thank you for your order, <strong>{order.full_name}</strong>!</p><p>Order ID: {order.order_number}<br>Total: Rs {order.total_price}</p>"

    # Prepare Admin Alert Email Content
    try:
        admin_html = render_to_string('emails/order_admin_alert.html', context)
        admin_text = render_to_string('emails/order_admin_alert.txt', context)
    except Exception as e:
        logger.warning(f"Error rendering admin alert template: {e}. Falling back to default text.")
        admin_text = f"New order received!\n\nOrder #{order.order_number}\nCustomer: {order.full_name} ({customer_email})\nTotal: Rs {order.total_price}"
        admin_html = f"<h2>New Order #{order.order_number}</h2><p>Customer: {order.full_name} ({customer_email})<br>Total: Rs {order.total_price}</p>"

    customer_subject = f"🌸 Order Confirmation #{order.order_number} - {store_name}"
    admin_subject = f"🌸 New Order Received: #{order.order_number} by {order.full_name} (Rs {order.total_price})"

    # 1. Send Order Confirmation to Customer (with retry)
    cust_email = EmailMultiAlternatives(
        subject=customer_subject,
        body=text_content,
        from_email=from_email,
        to=[customer_email],
        reply_to=[admin_email],
        headers={
            'X-Entity-Ref-ID': str(order.order_number),
            'Auto-Submitted': 'auto-generated',
        },
    )
    cust_email.attach_alternative(html_content, "text/html")
    customer_sent, customer_error = _send_email_with_retry(cust_email)
    if customer_sent:
        logger.info(f"Order confirmation email sent successfully for order #{order.order_number} to customer: {customer_email}")
    else:
        logger.error(f"Failed to send order confirmation email to customer {customer_email}: {customer_error}")

    # 2. Send New Order Alert to Store Admin / Owner (with retry)
    admin_msg = EmailMultiAlternatives(
        subject=admin_subject,
        body=admin_text,
        from_email=from_email,
        to=[admin_email],
        reply_to=[customer_email],
        headers={
            'X-Entity-Ref-ID': str(order.order_number),
        },
    )
    admin_msg.attach_alternative(admin_html, "text/html")
    admin_sent, admin_error = _send_email_with_retry(admin_msg)
    if admin_sent:
        logger.info(f"Admin order notification sent successfully for order #{order.order_number} to owner: {admin_email}")
    else:
        logger.error(f"Failed to send admin order notification to {admin_email}: {admin_error}")

    return customer_sent, customer_error


def send_contact_inquiry_emails(name: str, email_addr: str, subject_line: str, message_text: str) -> tuple[bool, str | None]:
    """
    Sends two emails for contact inquiries:
    1. Notification to store admin with customer's reply-to.
    2. Confirmation receipt to the customer.
    Returns (success: bool, error_message: str | None).
    """
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'noornisar96@gmail.com')
    store_name = getattr(settings, 'STORE_NAME', 'Crochet Store')

    context = {
        'name': name,
        'email': email_addr,
        'subject': subject_line,
        'message': message_text,
        'store_name': store_name,
    }

    # 1. Send alert to store Admin
    try:
        admin_subject = f"New Contact Inquiry: {subject_line} - {store_name}"
        try:
            admin_html = render_to_string('emails/contact_admin_alert.html', context)
            admin_text = render_to_string('emails/contact_admin_alert.txt', context)
        except Exception:
            admin_text = f"New message from {name} ({email_addr}):\n\nSubject: {subject_line}\n\nMessage:\n{message_text}"
            admin_html = f"<p><strong>From:</strong> {name} ({email_addr})</p><p><strong>Subject:</strong> {subject_line}</p><p><strong>Message:</strong><br>{message_text}</p>"

        admin_msg = EmailMultiAlternatives(
            subject=admin_subject,
            body=admin_text,
            from_email=from_email,
            to=[admin_email],
            reply_to=[email_addr],
        )
        admin_msg.attach_alternative(admin_html, "text/html")
        admin_msg.send(fail_silently=False)
        logger.info(f"Admin contact notification sent to {admin_email} for inquiry from {email_addr}")
    except Exception as e:
        safe_error = _sanitize_error(str(e))
        logger.error(f"Failed to send admin contact email: {safe_error}")
        return False, safe_error

    # 2. Send friendly confirmation to Customer
    try:
        customer_subject = f"Thank you for contacting {store_name}"
        try:
            cust_html = render_to_string('emails/contact_confirmation.html', context)
            cust_text = render_to_string('emails/contact_confirmation.txt', context)
        except Exception:
            cust_text = f"Hi {name},\n\nThank you for reaching out to {store_name}! We received your inquiry and will get back to you shortly.\n\nWarm regards,\n{store_name}"
            cust_html = f"<p>Hi <strong>{name}</strong>,</p><p>Thank you for reaching out to {store_name}! We have received your inquiry regarding '<em>{subject_line}</em>' and will get back to you shortly.</p>"

        cust_msg = EmailMultiAlternatives(
            subject=customer_subject,
            body=cust_text,
            from_email=from_email,
            to=[email_addr],
        )
        cust_msg.attach_alternative(cust_html, "text/html")
        cust_msg.send(fail_silently=True)  # Don't fail the whole flow if customer confirmation fails
        logger.info(f"Customer confirmation email sent to {email_addr}")
    except Exception as e:
        safe_error = _sanitize_error(str(e))
        logger.warning(f"Could not send customer contact confirmation: {safe_error}")

    return True, None
