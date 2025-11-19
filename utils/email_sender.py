import string
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import datetime as dt
import os

load_dotenv()

smtp_pw = os.getenv("SMTP_PASSWORD")

class EmailSender:

    @staticmethod
    def template(results):
        return f"""
<div style="font-family:Consolas,Monaco,monospace;padding:20px 30px;margin:0 auto;max-width:500px;border:2px solid #a8c4dd;border-radius:5px;">
    <h2 style="color:#a8c4dd;font-size:20px;margin:0 0 10px 0;padding-bottom:10px;border-bottom:1px solid #d0ddea;text-transform:uppercase;">
        <strong>ETL Result {dt.datetime.now().strftime("%Y-%m-%d %H:%M")}</strong>
    </h2>

    <h3 style="color:#5c7c99;font-size:16px;margin:15px 0 5px 0;">CNA</h3>
    <ul style="list-style:none;padding:0;margin:0;">
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># before:</span>
            <span style="color:#a8c4dd;font-weight:bold;text-align:right;min-width:60px;">{results['cna']['count_before']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># after:</span>
            <span style="color:#a8c4dd;font-weight:bold;text-align:right;min-width:60px;">{results['cna']['count_after']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># removed:</span>
            <span style="color:#ff9900;font-weight:bold;text-align:right;min-width:60px;">{results['cna']['removed_count']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#7ea6c8;"># added:</span>
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['cna']['count_after'] - results['cna']['count_before']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#7ea6c8;"># errors:</span>
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['cna']['errors']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['cna']['duration']}</span>
        </li>
    </ul>

    <h3 style="color:#5c7c99;font-size:16px;margin:15px 0 5px 0;">UDN</h3>
    <ul style="list-style:none;padding:0;margin:0;">
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># before:</span>
            <span style="color:#a8c4dd;font-weight:bold;text-align:right;min-width:60px;">{results['udn']['count_before']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># after:</span>
            <span style="color:#a8c4dd;font-weight:bold;text-align:right;min-width:60px;">{results['udn']['count_after']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># removed:</span>
            <span style="color:#ff9900;font-weight:bold;text-align:right;min-width:60px;">{results['udn']['removed_count']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#7ea6c8;"># added:</span>
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['udn']['count_after'] - results['udn']['count_before']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#7ea6c8;"># errors:</span>
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['udn']['errors']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['udn']['duration']}</span>
        </li>
    </ul>
    <h3 style="color:#5c7c99;font-size:16px;margin:15px 0 5px 0;">LTN</h3>
    <ul style="list-style:none;padding:0;margin:0;">
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># before:</span>
            <span style="color:#a8c4dd;font-weight:bold;text-align:right;min-width:60px;">{results['ltn']['count_before']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># after:</span>
            <span style="color:#a8c4dd;font-weight:bold;text-align:right;min-width:60px;">{results['ltn']['count_after']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #cccccc;">
            <span style="color:#7ea6c8;"># removed:</span>
            <span style="color:#ff9900;font-weight:bold;text-align:right;min-width:60px;">{results['ltn']['removed_count']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#7ea6c8;"># added:</span>
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['ltn']['count_after'] - results['ltn']['count_before']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#7ea6c8;"># errors:</span>
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['ltn']['errors']}</span>
        </li>
        <li style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#39ff14;font-weight:bold;font-size:1.1em;text-align:right;min-width:60px;">{results['ltn']['duration']}</span>
        </li>
    </ul>

    <div style="height:3px;margin-top:20px;background:#a8c4dd;"></div>
</div>
"""



    

    @staticmethod
    def send(recipient_email, body):
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('huang0jin@gmail.com', smtp_pw)

        from_addr = 'huang0jin@gmail.com'
        to_addr = recipient_email
        subject = "[News Scraper] Result of daily scraping\n\n"

        msg = MIMEText(body, 'html', 'utf-8') 
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr

        status = smtp.sendmail(from_addr, to_addr, msg.as_string())#加密文件，避免私密信息被截取
        if status=={}:
            return "Notification email sent."
        else:
            return "Failed to send Email!"
        smtp.quit()