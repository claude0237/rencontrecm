import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import requests

class NotificationService:
    """Service pour envoyer des notifications par email et SMS"""
    
    @staticmethod
    def send_email(to_email, subject, html_content):
        """Envoie un email via SMTP"""
        try:
            smtp_server = current_app.config.get('SMTP_SERVER')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            smtp_username = current_app.config.get('SMTP_USERNAME')
            smtp_password = current_app.config.get('SMTP_PASSWORD')
            smtp_from = current_app.config.get('SMTP_FROM', 'noreply@rencontrescm.com')
            
            if not smtp_server or not smtp_username or not smtp_password:
                print("SMTP non configuré - Email non envoyé")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_from
            msg['To'] = to_email
            
            msg.attach(MIMEText(html_content, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email envoyé à {to_email}")
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    @staticmethod
    def send_sms(to_phone, message):
        """Envoie un SMS via le fournisseur configuré"""
        sms_provider = current_app.config.get('SMS_PROVIDER', 'none')
        
        if sms_provider == 'twilio':
            return NotificationService._send_sms_twilio(to_phone, message)
        elif sms_provider == 'africastalking':
            return NotificationService._send_sms_africastalking(to_phone, message)
        else:
            print("SMS non configuré - SMS non envoyé")
            return False
    
    @staticmethod
    def _send_sms_twilio(to_phone, message):
        """Envoie un SMS via Twilio"""
        try:
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            from_number = current_app.config.get('TWILIO_FROM_NUMBER')
            
            if not account_sid or not auth_token or not from_number:
                print("Twilio non configuré")
                return False
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            data = {
                'From': from_number,
                'To': to_phone,
                'Body': message
            }
            
            response = requests.post(url, data=data, auth=(account_sid, auth_token))
            
            if response.status_code == 201:
                print(f"SMS envoyé à {to_phone}")
                return True
            else:
                print(f"Erreur Twilio: {response.text}")
                return False
        except Exception as e:
            print(f"Erreur lors de l'envoi SMS Twilio: {e}")
            return False
    
    @staticmethod
    def _send_sms_africastalking(to_phone, message):
        """Envoie un SMS via Africa's Talking"""
        try:
            username = current_app.config.get('AFRICASTALKING_USERNAME')
            api_key = current_app.config.get('AFRICASTALKING_API_KEY')
            
            if not username or not api_key:
                print("Africa's Talking non configuré")
                return False
            
            url = "https://api.africastalking.com/version1/messaging"
            data = {
                'username': username,
                'to': to_phone,
                'message': message
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                print(f"SMS envoyé à {to_phone}")
                return True
            else:
                print(f"Erreur Africa's Talking: {response.text}")
                return False
        except Exception as e:
            print(f"Erreur lors de l'envoi SMS Africa's Talking: {e}")
            return False
    
    @staticmethod
    def send_password_reset_code(user, code, method='email'):
        """Envoie le code de réinitialisation par email ou SMS"""
        if method == 'email':
            subject = "Code de réinitialisation - RencontresCM"
            html_content = f"""
            <html>
            <body>
                <h2>Réinitialisation de mot de passe</h2>
                <p>Bonjour {user.nom},</p>
                <p>Vous avez demandé une réinitialisation de votre mot de passe.</p>
                <p>Votre code de réinitialisation est : <strong>{code}</strong></p>
                <p>Ce code expire dans 15 minutes.</p>
                <p>Si vous n'avez pas fait cette demande, ignorez cet email.</p>
                <br>
                <p>L'équipe RencontresCM</p>
            </body>
            </html>
            """
            return NotificationService.send_email(user.email, subject, html_content)
        elif method == 'sms':
            message = f"Votre code de réinitialisation RencontresCM est: {code}. Expire dans 15 min."
            # Format Cameroun: ajouter +237 si nécessaire
            phone = user.contact_direct
            if not phone.startswith('+'):
                phone = '+237' + phone
            return NotificationService.send_sms(phone, message)
        else:
            # Envoyer par les deux
            email_sent = NotificationService.send_password_reset_code(user, code, 'email')
            sms_sent = NotificationService.send_password_reset_code(user, code, 'sms')
            return email_sent or sms_sent
    
    @staticmethod
    def send_password_reset_confirmation(user):
        """Envoie une confirmation de réinitialisation de mot de passe"""
        subject = "Mot de passe réinitialisé - RencontresCM"
        html_content = f"""
        <html>
        <body>
            <h2>Mot de passe réinitialisé</h2>
            <p>Bonjour {user.nom},</p>
            <p>Votre mot de passe a été réinitialisé avec succès.</p>
            <p>Si vous n'avez pas fait cette demande, contactez-nous immédiatement.</p>
            <br>
            <p>L'équipe RencontresCM</p>
        </body>
        </html>
        """
        return NotificationService.send_email(user.email, subject, html_content)
    
    @staticmethod
    def send_ad_validation_notification(ad):
        """Envoie une notification SMS lorsque une publicité est validée"""
        message = f"Votre publicité '{ad.titre}' a été validée par l'admin. Connectez-vous à votre espace pour payer et activer votre publicité."
        
        # Format Cameroun: ajouter +237 si nécessaire
        phone = ad.numero_contact
        if phone and not phone.startswith('+'):
            phone = '+237' + phone
        
        if phone:
            return NotificationService.send_sms(phone, message)
        else:
            print("Aucun numéro de contact pour la publicité - SMS non envoyé")
            return False
